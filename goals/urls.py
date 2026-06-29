from django.urls import path
from . import views

urlpatterns = [
    path("", views.goal_list, name="goal_list"),
    path("<int:goal_id>/", views.goal_detail, name="goal_detail"),
    path("create/", views.goal_create, name="goal_create"),
    path("literacy/", views.literacy_view, name="literacy"),
]
