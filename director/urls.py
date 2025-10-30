from django.urls import path
from . import views

app_name = "director"

urlpatterns = [

    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/role/", views.UserRoleUpdateView.as_view(), name="user_role_update"),

    path("classes/", views.ClassListView.as_view(), name="class_list"),
    path("classes/new/", views.ClassCreateView.as_view(), name="class_create"),
    path("classes/<int:pk>/students/", views.ClassStudentListView.as_view(), name="class_students"),
    path("classes/<int:pk>/add-student/", views.ClassAddStudentView.as_view(), name="class_add_student"),

    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/new/", views.SubjectCreateView.as_view(), name="subject_create"),

    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/new/', views.add_lesson, name="lesson_add"),
]
