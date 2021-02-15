from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("random_entry", views.random_entry, name="random_entry"),
    path("edit-entry", views.load_entry, name="load_entry"),
    path("submit-entry", views.submit_entry, name="submit_entry"),

    path("dev", views.dev, name="dev")      # DEV ONLY
]