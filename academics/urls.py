from django.urls import path
from . import views

urlpatterns = [
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("classes/", views.ClassListView.as_view(), name="class_list"),
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment_list"),
    path("lessons/", views.LessonListView.as_view(), name="lesson_list"),
    path("lessons/<int:pk>/", views.LessonDetailView.as_view(), name="lesson_detail"),
]
