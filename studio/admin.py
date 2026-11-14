from django.contrib import admin

from .models import AsciiArtwork


@admin.register(AsciiArtwork)
class AsciiArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "font_name", "created_at", "updated_at")
    list_filter = ("font_name", "created_at")
    search_fields = ("title", "source_text", "owner__username")
    readonly_fields = ("created_at", "updated_at")
