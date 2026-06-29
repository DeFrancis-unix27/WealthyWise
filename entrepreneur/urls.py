from django.urls import path
from . import views

urlpatterns = [
    path("", views.business_list, name="business_list"),
    path("<int:business_id>/", views.business_detail, name="business_detail"),
    path("create/", views.business_create, name="business_create"),
    path("side-hustles/", views.side_hustle_list, name="side_hustle_list"),
    path("side-hustles/create/", views.side_hustle_create, name="side_hustle_create"),
    path("paths/", views.path_list, name="path_list"),
]
