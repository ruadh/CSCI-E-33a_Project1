from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("random_entry", views.random_entry, name="random_entry"),
    path("dev", views.dev, name="dev")      # DEV ONLY
    # path("new_entry", views.new_entry, name="new_entry")
]