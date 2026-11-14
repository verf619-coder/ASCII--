from django.conf import settings
from django.db import models


class AsciiArtwork(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ascii_artworks",
    )
    title = models.CharField(max_length=120)
    source_text = models.TextField()
    ascii_text = models.TextField(blank=True)
    font_name = models.CharField(max_length=80)
    text_color = models.CharField(max_length=7, default="#f5f5f5")
    background_color = models.CharField(max_length=7, default="#111827")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "ASCII-робота"
        verbose_name_plural = "ASCII-роботи"

    def __str__(self):
        return self.title
