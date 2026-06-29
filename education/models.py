from django.db import models
from django.conf import settings


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructor_profile"
    )
    bio = models.TextField(blank=True)
    credentials = models.TextField(blank=True)
    expertise_areas = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="instructors/", blank=True, null=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    compensation_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Concept(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    content = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class or emoji")
    prerequisites = models.ManyToManyField("self", blank=True, symmetrical=False)
    related_concepts = models.ManyToManyField("self", blank=True)
    estimated_minutes = models.IntegerField(default=10)
    is_published = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class Project(models.Model):
    DIFFICULTY_CHOICES = Concept.DIFFICULTY_CHOICES
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    learning_objectives = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    concepts = models.ManyToManyField(Concept, related_name="projects", blank=True)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects"
    )
    estimated_minutes = models.IntegerField(default=30)
    is_interactive = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    thumbnail = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class ProjectStep(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="steps")
    title = models.CharField(max_length=255)
    description = models.TextField()
    instruction = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    step_type = models.CharField(
        max_length=20,
        choices=[
            ("info", "Information"),
            ("input", "User Input"),
            ("quiz", "Quiz"),
            ("calculation", "Calculation"),
            ("reflection", "Reflection"),
        ],
        default="info",
    )
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order"]
        unique_together = ["project", "sort_order"]

    def __str__(self):
        return f"{self.project.title} - Step {self.sort_order}: {self.title}"


class Course(models.Model):
    DIFFICULTY_CHOICES = Concept.DIFFICULTY_CHOICES
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )
    concepts = models.ManyToManyField(Concept, related_name="courses", blank=True)
    projects = models.ManyToManyField(Project, related_name="courses", blank=True)
    prerequisites = models.ManyToManyField("self", blank=True, symmetrical=False)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    estimated_hours = models.IntegerField(default=1)
    thumbnail = models.ImageField(upload_to="courses/", blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField(default=10)
    sort_order = models.IntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]
        unique_together = ["course", "sort_order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Workshop(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, null=True, related_name="workshops"
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    max_attendees = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    meeting_url = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_premium_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return self.title


class Webinar(models.Model):
    STATUS_CHOICES = Workshop.STATUS_CHOICES
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, null=True, related_name="webinars"
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    live_url = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_premium_only = models.BooleanField(default=False)
    max_attendees = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="enrollments"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name="enrollments"
    )
    workshop = models.ForeignKey(
        Workshop, on_delete=models.CASCADE, null=True, blank=True, related_name="enrollments"
    )
    webinar = models.ForeignKey(
        Webinar, on_delete=models.CASCADE, null=True, blank=True, related_name="enrollments"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [
            ("user", "course"),
            ("user", "project"),
            ("user", "workshop"),
            ("user", "webinar"),
        ]

    def __str__(self):
        enrolled_in = self.course or self.project or self.workshop or self.webinar
        return f"{self.user} - {enrolled_in} ({self.status})"


class ProjectSubmission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="submissions"
    )
    step = models.ForeignKey(ProjectStep, on_delete=models.CASCADE, related_name="submissions")
    response = models.TextField(blank=True)
    is_complete = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["enrollment", "step"]

    def __str__(self):
        return f"Submission for {self.step} by {self.enrollment.user}"


class LearningPath(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    concepts = models.ManyToManyField(Concept, related_name="learning_paths", blank=True)
    projects = models.ManyToManyField(Project, related_name="learning_paths", blank=True)
    courses = models.ManyToManyField(Course, related_name="learning_paths", blank=True)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title
