from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.readentry, name="readentry"),
    path("search/", views.search, name="search"),
    path("create/", views.createentry, name="createentry"),
    path("edit/<str:title>", views.editentry, name="editentry"),
    path("random/", views.randompage, name="randompage")
]
