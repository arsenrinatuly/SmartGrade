from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('class/<int:class_id>/', views.class_report, name='class_report'),
    path('class/<int:class_id>/pdf/', views.class_report_pdf, name='class_report_pdf'),
    path('student/<int:student_id>/', views.student_report, name='student_report'),
    path('student/<int:student_id>/pdf/', views.student_report_pdf, name="student_report_pdf"),
    path("students/search/", views.student_search, name="student_search"),
    path('class/<int:class_id>/attendance/pdf/', views.class_attendance_report_pdf, name='class_attendance_report_pdf'),
]
