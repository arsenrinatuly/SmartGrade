from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from accounts.models import User
from academics.models import Subject, ClassRoom, Lesson, Enrollment
from journal.models import GradeRecord, AttendanceRecord
from .serializers import (
    UserSerializer, SubjectSerializer, ClassRoomSerializer, LessonSerializer,
    EnrollmentSerializer, GradeRecordSerializer, AttendanceRecordSerializer
)


class IsDirector(permissions.BasePermission):
    """Разрешение: доступ только для пользователей с ролью директора (ADMIN)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsTeacher(permissions.BasePermission):
    """Разрешение: доступ только для пользователей с ролью учителя (TEACHER)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TEACHER'


class IsStudent(permissions.BasePermission):
    """Разрешение: доступ только для пользователей с ролью ученика (STUDENT)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'



class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint: Список и детальная информация о предметах.
    Доступно только аутентифицированным пользователям.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ClassRoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint: Список и детали классов.
    - Учитель видит только свои классы.
    - Ученик — только тот, где он зачислен.
    - Администратор — все.
    """
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтрация классов в зависимости от роли пользователя."""
        user = self.request.user
        if user.role == 'TEACHER':
            return ClassRoom.objects.filter(curator=user)
        elif user.role == 'STUDENT':
            return ClassRoom.objects.filter(enrollments__student=user)
        return super().get_queryset()


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint: Просмотр уроков.
    - Учитель видит только свои уроки.
    - Ученик видит уроки своего класса.
    - Директор видит все.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтрация уроков в зависимости от роли пользователя."""
        user = self.request.user
        if user.role == 'TEACHER':
            return Lesson.objects.filter(teacher=user)
        elif user.role == 'STUDENT':
            return Lesson.objects.filter(classroom__enrollments__student=user)
        return super().get_queryset()


class GradeRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint: Управление оценками (чтение, создание, редактирование).
    - Учитель может выставлять оценки своим ученикам.
    - Ученик может просматривать только свои оценки.
    - Директор видит все записи.
    """
    queryset = GradeRecord.objects.all()
    serializer_class = GradeRecordSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтрация оценок по роли пользователя."""
        user = self.request.user
        if user.role == 'TEACHER':
            return GradeRecord.objects.filter(lesson__teacher=user)
        elif user.role == 'STUDENT':
            return GradeRecord.objects.filter(student=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        """Создание записи об оценке (только учитель)."""
        user = self.request.user
        if user.role != 'TEACHER':
            raise permissions.PermissionDenied("Только учителя могут ставить оценки.")
        serializer.save()


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint: Управление посещаемостью (чтение, создание, редактирование).
    - Учитель может отмечать посещаемость своих учеников.
    - Ученик видит только свои отметки.
    - Директор видит все записи.
    """
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтрация записей посещаемости по роли пользователя."""
        user = self.request.user
        if user.role == 'TEACHER':
            return AttendanceRecord.objects.filter(lesson__teacher=user)
        elif user.role == 'STUDENT':
            return AttendanceRecord.objects.filter(student=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        """Создание записи о посещаемости (только учитель)."""
        user = self.request.user
        if user.role != 'TEACHER':
            raise permissions.PermissionDenied("Только учителя могут отмечать посещаемость.")
        serializer.save()
