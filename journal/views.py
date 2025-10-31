from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator

from .models import GradeRecord, AttendanceRecord
from academics.models import Lesson, Enrollment


def user_is_teacher(user) -> bool:
    """
    Проверяет, является ли пользователь учителем.
    """
    if not user.is_authenticated:
        return False
    if hasattr(user, "is_teacher") and callable(user.is_teacher):
        return user.is_teacher()
    return getattr(user, "role", None) == "TEACHER"


def user_is_student(user) -> bool:
    """
    Проверяет, является ли пользователь учеником.
    """
    if not user.is_authenticated:
        return False
    if hasattr(user, "is_student") and callable(user.is_student):
        return user.is_student()
    return getattr(user, "role", None) == "STUDENT"


class TeacherRequiredMixin(LoginRequiredMixin):
    """
    Миксин, ограничивающий доступ только для учителей.
    """

    def dispatch(self, request, *args, **kwargs):
        if not user_is_teacher(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LoginRequiredMixin):
    """
    Миксин, ограничивающий доступ только для учеников.
    """

    def dispatch(self, request, *args, **kwargs):
        if not user_is_student(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def _enrolled_student_qs_for_lesson(lesson):
    """
    Возвращает queryset учеников, зачисленных в класс данного урока.
    """
    student_ids = (
        Enrollment.objects
        .filter(classroom=lesson.classroom)
        .values_list("student_id", flat=True)
    )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.filter(id__in=student_ids)


class GradeCreateView(TeacherRequiredMixin, CreateView):
    """
    Представление для добавления оценки ученику.
    Доступно только для учителей.
    """
    model = GradeRecord
    fields = ["lesson", "student", "value", "max_value", "note"]
    template_name = "journal/grade_form.html"
    success_url = reverse_lazy("dashboard")

    def get_form(self, form_class=None):
        """
        Настраивает форму — ограничивает выбор уроков и учеников.
        """
        form = super().get_form(form_class)


        form.fields["lesson"].queryset = Lesson.objects.filter(
            teacher=self.request.user
        ).order_by("-date")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        form.fields["student"].queryset = User.objects.filter(role="STUDENT")

        # Ограничиваем выбор учеников теми, кто записан в класс урока
        lesson_id = self.request.POST.get("lesson") or self.request.GET.get("lesson")
        if lesson_id:
            try:
                lesson = Lesson.objects.get(pk=lesson_id, teacher=self.request.user)
                form.fields["student"].queryset = _enrolled_student_qs_for_lesson(lesson)
            except Lesson.DoesNotExist:
                pass

        return form

    def form_valid(self, form):
        """
        Проверяет корректность урока и ученика перед сохранением оценки.
        """
        lesson = form.cleaned_data["lesson"]
        if lesson.teacher_id != self.request.user.id:
            raise PermissionDenied("Вы не можете ставить оценки на чужом уроке.")

        student = form.cleaned_data["student"]
        if not Enrollment.objects.filter(classroom=lesson.classroom, student=student).exists():
            form.add_error("student", "Ученик не зачислен в класс выбранного урока.")
            return self.form_invalid(form)

        return super().form_valid(form)


class AttendanceCreateView(TeacherRequiredMixin, CreateView):
    """
    Представление для отметки посещаемости учеников.
    Доступно только для учителей.
    """
    model = AttendanceRecord
    fields = ["lesson", "student", "status", "comment"]
    template_name = "journal/attendance_form.html"
    success_url = reverse_lazy("dashboard")

    def get_form(self, form_class=None):
        """
        Настраивает форму — ограничивает выбор уроков и учеников.
        """
        form = super().get_form(form_class)
        form.fields["lesson"].queryset = Lesson.objects.filter(
            teacher=self.request.user
        ).order_by("-date")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        form.fields["student"].queryset = User.objects.filter(role="STUDENT")

        lesson_id = self.request.POST.get("lesson") or self.request.GET.get("lesson")
        if lesson_id:
            try:
                lesson = Lesson.objects.get(pk=lesson_id, teacher=self.request.user)
                form.fields["student"].queryset = _enrolled_student_qs_for_lesson(lesson)
            except Lesson.DoesNotExist:
                pass

        return form

    def form_valid(self, form):
        """
        Проверяет корректность данных перед сохранением записи посещаемости.
        """
        lesson = form.cleaned_data["lesson"]
        if lesson.teacher_id != self.request.user.id:
            raise PermissionDenied("Вы не можете отмечать посещаемость на чужом уроке.")

        student = form.cleaned_data["student"]
        if not Enrollment.objects.filter(classroom=lesson.classroom, student=student).exists():
            form.add_error("student", "Ученик не зачислен в класс выбранного урока.")
            return self.form_invalid(form)

        return super().form_valid(form)


class TeacherLessonListView(TeacherRequiredMixin, ListView):
    """
    Отображает список уроков, проведённых текущим учителем.
    """
    model = Lesson
    template_name = "journal/teacher_lessons.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            Lesson.objects
            .filter(teacher=self.request.user)
            .select_related("subject", "classroom")
            .order_by("-date")
        )


class TeacherGradesListView(TeacherRequiredMixin, ListView):
    """
    Отображает список всех оценок, выставленных данным учителем.
    """
    model = GradeRecord
    template_name = "journal/teacher_grades.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            GradeRecord.objects
            .filter(lesson__teacher=self.request.user)
            .select_related("lesson", "lesson__subject", "lesson__classroom", "student")
            .order_by("-date")
        )


class TeacherAttendanceListView(TeacherRequiredMixin, ListView):
    """
    Отображает список всех отметок посещаемости, сделанных данным учителем.
    """
    model = AttendanceRecord
    template_name = "journal/teacher_attendance.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            AttendanceRecord.objects
            .filter(lesson__teacher=self.request.user)
            .select_related("lesson", "lesson__subject", "lesson__classroom", "student")
            .order_by("-lesson__date")
        )


class StudentGradesListView(StudentRequiredMixin, ListView):
    """
    Отображает список оценок текущего ученика.
    """
    model = GradeRecord
    template_name = "journal/my_grades.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            GradeRecord.objects
            .filter(student=self.request.user)
            .select_related("lesson", "lesson__subject", "lesson__classroom")
            .order_by("-date")
        )


class StudentAttendanceListView(StudentRequiredMixin, ListView):
    """
    Отображает список посещаемости текущего ученика.
    """
    model = AttendanceRecord
    template_name = "journal/my_attendance.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            AttendanceRecord.objects
            .filter(student=self.request.user)
            .select_related("lesson", "lesson__subject", "lesson__classroom")
            .order_by("-lesson__date")
        )
