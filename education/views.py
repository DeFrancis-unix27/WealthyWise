from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Concept, Project, ProjectStep, Course, Lesson, Workshop, Webinar, Enrollment, ProjectSubmission

def concept_list(request):
    concepts = Concept.objects.filter(is_published=True)
    difficulty = request.GET.get("difficulty")
    if difficulty:
        concepts = concepts.filter(difficulty=difficulty)
    return render(request, "education/concept_list.html", {"concepts": concepts})

def concept_detail(request, slug):
    concept = get_object_or_404(Concept, slug=slug, is_published=True)
    return render(request, "education/concept_detail.html", {"concept": concept})

def project_list(request):
    projects = Project.objects.filter(status="published")
    difficulty = request.GET.get("difficulty")
    if difficulty:
        projects = projects.filter(difficulty=difficulty)
    return render(request, "education/project_list.html", {"projects": projects})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, status="published")
    return render(request, "education/project_detail.html", {"project": project})

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    difficulty = request.GET.get("difficulty")
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    return render(request, "education/course_list.html", {"courses": courses})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    return render(request, "education/course_detail.html", {"course": course})

def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    all_lessons = list(course.lessons.all())
    idx = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
    prev_lesson = all_lessons[idx - 1] if idx and idx > 0 else None
    next_lesson = all_lessons[idx + 1] if idx is not None and idx < len(all_lessons) - 1 else None
    return render(request, "education/lesson_detail.html", {
        "course": course, "lesson": lesson,
        "prev_lesson": prev_lesson, "next_lesson": next_lesson,
    })

def workshop_list(request):
    workshops = Workshop.objects.filter(status__in=["scheduled", "live"]).order_by("scheduled_at")
    return render(request, "education/workshop_list.html", {"workshops": workshops})

def webinar_list(request):
    webinars = Webinar.objects.filter(status__in=["scheduled", "live"]).order_by("scheduled_at")
    return render(request, "education/webinar_list.html", {"webinars": webinars})

@login_required
def enroll(request, content_type, content_id):
    model_map = {"course": Course, "project": Project, "workshop": Workshop, "webinar": Webinar}
    obj = get_object_or_404(model_map[content_type], id=content_id)
    kwargs = {"user": request.user, content_type: obj}
    enrollment, created = Enrollment.objects.get_or_create(**kwargs, defaults={"status": "active"})
    if not created:
        messages.info(request, f"You are already enrolled in {obj.title}.")
    else:
        messages.success(request, f"Enrolled in {obj.title}!")
    return redirect("course_list")
