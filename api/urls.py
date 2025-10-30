from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, ClassRoomViewSet, LessonViewSet,
    GradeRecordViewSet, AttendanceRecordViewSet
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'classes', ClassRoomViewSet, basename='class')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'grades', GradeRecordViewSet, basename='grade')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')

urlpatterns = router.urls
