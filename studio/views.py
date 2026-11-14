import json
import re
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST

from .models import AsciiArtwork


FONT_CHOICES = (
    ("Standard", "Standard"),
    ("Small", "Small"),
    ("Block", "Block"),
)

ARTWORK_FIELDS = {
    "title": (str, 120),
    "source_text": (str, None),
    "ascii_text": (str, None),
    "font_name": (str, 80),
    "text_color": (str, 7),
    "background_color": (str, 7),
}
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def home_view(request):
    return render(request, "studio/home.html")


def editor_view(request, artwork_id=None):
    artwork = None
    if artwork_id is not None:
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        artwork = get_object_or_404(
            AsciiArtwork, id=artwork_id, owner=request.user
        )

    font_choices = list(FONT_CHOICES)
    if artwork and artwork.font_name not in dict(font_choices):
        font_choices.append((artwork.font_name, artwork.font_name))

    return render(
        request,
        "studio/editor.html",
        {"artwork": artwork, "font_choices": font_choices},
    )


@login_required
def projects_view(request):
    artworks = AsciiArtwork.objects.filter(owner=request.user)
    return render(request, "studio/projects.html", {"artworks": artworks})


def api_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication is required."}, status=401
            )
        return view_func(request, *args, **kwargs)

    return wrapped_view


def parse_json_body(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse(
            {"error": "Request body must contain valid JSON."}, status=400
        )

    if not isinstance(data, dict):
        return None, JsonResponse(
            {"error": "JSON body must be an object."}, status=400
        )
    return data, None


def validate_artwork_data(data, partial=False):
    unknown_fields = set(data) - set(ARTWORK_FIELDS)
    if unknown_fields:
        return f"Unknown fields: {', '.join(sorted(unknown_fields))}"

    required_fields = {"title", "source_text", "ascii_text", "font_name"}
    if not partial and not required_fields.issubset(data):
        missing_fields = required_fields - set(data)
        return f"Missing required fields: {', '.join(sorted(missing_fields))}"

    for field, value in data.items():
        expected_type, max_length = ARTWORK_FIELDS[field]
        if not isinstance(value, expected_type):
            return f"'{field}' must be a string."
        if field in {"title", "font_name"} and not value.strip():
            return f"'{field}' cannot be empty."
        if max_length is not None and len(value) > max_length:
            return f"'{field}' must be at most {max_length} characters."
        if field in {"text_color", "background_color"}:
            if not COLOR_PATTERN.fullmatch(value):
                return f"'{field}' must be a six-digit hex color."
    return None


@require_POST
@api_login_required
def api_create_project(request):
    data, error_response = parse_json_body(request)
    if error_response:
        return error_response

    validation_error = validate_artwork_data(data)
    if validation_error:
        return JsonResponse({"error": validation_error}, status=400)

    artwork = AsciiArtwork.objects.create(owner=request.user, **data)
    return JsonResponse(serialize_artwork(artwork), status=201)


@require_http_methods(["GET", "PATCH", "DELETE"])
@api_login_required
def api_project_detail(request, artwork_id):
    artwork = AsciiArtwork.objects.filter(
        id=artwork_id, owner=request.user
    ).first()
    if artwork is None:
        return JsonResponse({"error": "Artwork not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(serialize_artwork(artwork))

    if request.method == "DELETE":
        artwork.delete()
        return JsonResponse({"message": "Artwork deleted."}, status=200)

    data, error_response = parse_json_body(request)
    if error_response:
        return error_response

    validation_error = validate_artwork_data(data, partial=True)
    if validation_error:
        return JsonResponse({"error": validation_error}, status=400)

    for field, value in data.items():
        setattr(artwork, field, value)
    artwork.save()
    return JsonResponse(serialize_artwork(artwork))


def serialize_artwork(artwork):
    return {
        "id": artwork.id,
        "title": artwork.title,
        "source_text": artwork.source_text,
        "ascii_text": artwork.ascii_text,
        "font_name": artwork.font_name,
        "text_color": artwork.text_color,
        "background_color": artwork.background_color,
        "created_at": artwork.created_at.isoformat(),
        "updated_at": artwork.updated_at.isoformat(),
    }
