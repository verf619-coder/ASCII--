from django.urls import path

from . import views


app_name = "studio"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("studio/editor/", views.editor_view, name="editor"),
    path(
        "studio/editor/<int:artwork_id>/",
        views.editor_view,
        name="edit_artwork",
    ),
    path("studio/projects/", views.projects_view, name="projects"),
    path(
        "studio/api/projects/",
        views.api_create_project,
        name="api_create_project",
    ),
    path(
        "studio/api/projects/<int:artwork_id>/",
        views.api_project_detail,
        name="api_project_detail",
    ),
]
