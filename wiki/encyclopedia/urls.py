from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("entries/<str:entry>", views.entry, name="entry"),
    path("search_results", views.search_results, name="search_results")
]