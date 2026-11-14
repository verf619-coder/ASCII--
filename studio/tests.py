import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import AsciiArtwork


class AccountAndArtworkTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="artist", password="safe-password-123"
        )
        self.other_user = get_user_model().objects.create_user(
            username="another-artist", password="safe-password-456"
        )
        self.artwork = AsciiArtwork.objects.create(
            owner=self.user,
            title="My art",
            source_text="Hello",
            ascii_text="HELLO",
            font_name="Standard",
        )

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-artist",
                "password1": "a-strong-password-123",
                "password2": "a-strong-password-123",
            },
        )

        self.assertRedirects(response, reverse("studio:home"))
        self.assertTrue(
            get_user_model().objects.filter(username="new-artist").exists()
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_redirects_to_home(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "artist", "password": "safe-password-123"},
        )

        self.assertRedirects(response, reverse("studio:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_projects_page_requires_login(self):
        response = self.client.get(reverse("studio:projects"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('studio:projects')}",
        )

    def test_api_requires_login(self):
        response = self.client.get(
            reverse(
                "studio:api_project_detail",
                kwargs={"artwork_id": self.artwork.id},
            )
        )

        self.assertEqual(response.status_code, 401)

    def test_api_create_update_and_delete_artwork(self):
        self.client.force_login(self.user)
        collection_url = reverse("studio:api_create_project")
        payload = {
            "title": "New art",
            "source_text": "Hello",
            "ascii_text": "HELLO",
            "font_name": "Standard",
            "text_color": "#ffffff",
            "background_color": "#000000",
        }

        create_response = self.client.post(
            collection_url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 201)
        artwork_id = create_response.json()["id"]
        created_artwork = AsciiArtwork.objects.get(id=artwork_id)
        self.assertEqual(created_artwork.owner, self.user)

        detail_url = reverse(
            "studio:api_project_detail", kwargs={"artwork_id": artwork_id}
        )
        update_response = self.client.patch(
            detail_url,
            data=json.dumps({"title": "Updated art"}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["title"], "Updated art")

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(AsciiArtwork.objects.filter(id=artwork_id).exists())

    def test_api_write_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(
            reverse("studio:api_create_project"),
            data=json.dumps(
                {
                    "title": "New art",
                    "source_text": "Hello",
                    "ascii_text": "HELLO",
                    "font_name": "Standard",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_read_or_change_another_users_artwork(self):
        self.client.force_login(self.other_user)
        url = reverse(
            "studio:api_project_detail",
            kwargs={"artwork_id": self.artwork.id},
        )

        get_response = self.client.get(url)
        patch_response = self.client.patch(
            url,
            data=json.dumps({"title": "Changed"}),
            content_type="application/json",
        )
        delete_response = self.client.delete(url)

        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(patch_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.artwork.refresh_from_db()
        self.assertEqual(self.artwork.title, "My art")
