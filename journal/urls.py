from django.urls import path
from . import views

urlpatterns = [
    
    path("grades/new/", views.GradeCreateView.as_view(), name="grade_new"),
    path("attendance/new/", views.AttendanceCreateView.as_view(), name="attendance_new"),


    path("teacher/lessons/", views.TeacherLessonListView.as_view(), name="teacher_lessons"),
    path("teacher/grades/", views.TeacherGradesListView.as_view(), name="teacher_grades"),
    path("teacher/attendance/", views.TeacherAttendanceListView.as_view(), name="teacher_attendance"),

    path("me/grades/", views.StudentGradesListView.as_view(), name="my_grades"),
    path("me/attendance/", views.StudentAttendanceListView.as_view(), name="my_attendance"),

]
