from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import (
    Instructor, Concept, Project, ProjectStep, Course, Lesson,
    Workshop, Webinar, Enrollment, ProjectSubmission, LearningPath,
)


@admin.register(Instructor)
class InstructorAdmin(UnfoldModelAdmin):
    list_display = ('user', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active')
    search_fields = ('user__username', 'user__email', 'bio')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Concept)
class ConceptAdmin(UnfoldModelAdmin):
    list_display = ('title', 'difficulty', 'estimated_minutes', 'is_published', 'sort_order')
    list_filter = ('difficulty', 'is_published')
    search_fields = ('title', 'description')
    list_editable = ('is_published', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Project)
class ProjectAdmin(UnfoldModelAdmin):
    list_display = ('title', 'difficulty', 'status', 'is_premium', 'is_interactive', 'sort_order')
    list_filter = ('difficulty', 'status', 'is_premium', 'is_interactive')
    search_fields = ('title', 'description', 'learning_objectives')
    list_editable = ('status', 'is_premium', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ProjectStep)
class ProjectStepAdmin(UnfoldModelAdmin):
    list_display = ('project', 'title', 'step_type', 'sort_order')
    list_filter = ('step_type',)
    search_fields = ('project__title', 'title')
    list_editable = ('sort_order',)


@admin.register(Course)
class CourseAdmin(UnfoldModelAdmin):
    list_display = ('title', 'difficulty', 'estimated_hours', 'is_premium', 'is_published', 'sort_order')
    list_filter = ('difficulty', 'is_premium', 'is_published')
    search_fields = ('title', 'description')
    list_editable = ('is_premium', 'is_published', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(UnfoldModelAdmin):
    list_display = ('course', 'title', 'duration_minutes', 'is_preview', 'sort_order')
    list_filter = ('is_preview',)
    search_fields = ('course__title', 'title')
    list_editable = ('is_preview', 'sort_order')


@admin.register(Workshop)
class WorkshopAdmin(UnfoldModelAdmin):
    list_display = ('title', 'instructor', 'scheduled_at', 'price', 'status', 'is_premium_only')
    list_filter = ('status', 'is_premium_only')
    search_fields = ('title', 'description')
    date_hierarchy = 'scheduled_at'


@admin.register(Webinar)
class WebinarAdmin(UnfoldModelAdmin):
    list_display = ('title', 'instructor', 'scheduled_at', 'price', 'status', 'is_premium_only')
    list_filter = ('status', 'is_premium_only')
    search_fields = ('title', 'description')
    date_hierarchy = 'scheduled_at'


@admin.register(Enrollment)
class EnrollmentAdmin(UnfoldModelAdmin):
    list_display = ('user', 'course', 'project', 'workshop', 'webinar', 'status', 'progress_percent')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('started_at',)


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(UnfoldModelAdmin):
    list_display = ('enrollment', 'step', 'is_complete', 'submitted_at')
    list_filter = ('is_complete',)
    search_fields = ('enrollment__user__username',)


@admin.register(LearningPath)
class LearningPathAdmin(UnfoldModelAdmin):
    list_display = ('title', 'is_premium', 'is_published', 'sort_order')
    list_filter = ('is_premium', 'is_published')
    search_fields = ('title', 'description')
    list_editable = ('is_premium', 'is_published', 'sort_order')
    prepopulated_fields = {'slug': ('title',)}
