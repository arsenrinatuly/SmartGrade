from django.contrib import admin
from .models import Subject, ClassRoom, Enrollment, Lesson


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("grade_level", "name", "curator")
    list_filter = ("grade_level",)
    search_fields = ("name", "curator__email", "curator__first_name", "curator__last_name")
    autocomplete_fields = ("curator",)
    ordering = ("grade_level", "name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "classroom", "date_enrolled")
    list_filter = ("classroom",)
    search_fields = (
        "student__email", "student__first_name", "student__last_name",
        "classroom__name",
    )
    autocomplete_fields = ("student", "classroom")
    date_hierarchy = "date_enrolled"
    ordering = ("classroom", "student")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("date", "classroom", "subject", "teacher", "topic")
    list_filter = ("date", "classroom", "subject")
    search_fields = (
        "topic",
        "subject__name", "subject__code",
        "classroom__name",
        "teacher__email", "teacher__first_name", "teacher__last_name",
    )
    autocomplete_fields = ("subject", "classroom", "teacher")
    date_hierarchy = "date"
    ordering = ("-date",)
