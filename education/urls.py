from django.urls import path
from . import views

urlpatterns = [
    path("concepts/", views.concept_list, name="concept_list"),
    path("concepts/<slug:slug>/", views.concept_detail, name="concept_detail"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:course_slug>/lessons/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),
    path("workshops/", views.workshop_list, name="workshop_list"),
    path("webinars/", views.webinar_list, name="webinar_list"),
    path("enroll/<str:content_type>/<int:content_id>/", views.enroll, name="enroll"),
]
