from rest_framework import serializers
from accounts.models import User
from academics.models import Subject, ClassRoom, Lesson, Enrollment
from journal.models import GradeRecord, AttendanceRecord


# ---------- Пользователи ----------
class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя.
    Используется для отображения основной информации о пользователях системы.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


# ---------- Академические сериализаторы ----------
class SubjectSerializer(serializers.ModelSerializer):
    """
    Сериализатор предмета.
    Включает информацию о преподавателе (teacher) через вложенный UserSerializer.
    """
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'teacher']


class ClassRoomSerializer(serializers.ModelSerializer):
    """
    Сериализатор школьного класса.
    Отображает базовую информацию и куратора (curator).
    """
    curator = UserSerializer(read_only=True)

    class Meta:
        model = ClassRoom
        fields = ['id', 'grade_level', 'name', 'curator']


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор зачисления ученика в класс.
    Используется для отображения связей между учеником и классом.
    """
    student = UserSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'classroom', 'date_enrolled']


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор урока.
    Включает вложенные данные о предмете, классе и учителе.
    """
    subject = SubjectSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'subject', 'classroom', 'teacher', 'date', 'topic']


# ---------- Журнал ----------
class GradeRecordSerializer(serializers.ModelSerializer):
    """
    Сериализатор оценок учеников.
    Используется для отображения и создания записей об успеваемости.
    """
    student = UserSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = GradeRecord
        fields = ['id', 'lesson', 'student', 'value', 'max_value', 'note', 'date']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """
    Сериализатор посещаемости учеников.
    Показывает статус посещения для конкретного урока.
    """
    student = UserSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'lesson', 'student', 'status', 'comment']
