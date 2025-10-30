from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Subject, ClassRoom, Enrollment, Lesson


class SubjectListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех учебных предметов.

    Доступ разрешён только авторизованным пользователям.
    """
    model = Subject
    template_name = "academics/subject_list.html"
    context_object_name = "subjects"


class ClassListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех учебных классов.

    Используется для просмотра классов в системе.
    """
    model = ClassRoom
    template_name = "academics/class_list.html"
    context_object_name = "classes"


class EnrollmentListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех записей о зачислении учеников в классы.

    Реализована пагинация для удобства просмотра большого количества записей.
    """
    model = Enrollment
    template_name = "academics/enrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 50 


class LessonListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех уроков.

    Поддерживает пагинацию и требует авторизации пользователя.
    """
    model = Lesson
    template_name = "academics/lesson_list.html"
    context_object_name = "lessons"
    paginate_by = 50


class LessonDetailView(LoginRequiredMixin, DetailView):
    """
    Отображает детальную информацию об отдельном уроке.

    Используется для просмотра содержания и метаданных конкретного урока.
    """
    model = Lesson
    template_name = "academics/lesson_detail.html"
    context_object_name = "lesson"
