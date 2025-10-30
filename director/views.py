from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from academics.models import ClassRoom, Subject, Enrollment, Lesson
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.contrib import messages

from accounts.models import User
from .forms import LessonForm


User = get_user_model()


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Миксин, ограничивающий доступ только для директора (ADMIN).
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            raise PermissionDenied("Доступ только для директора.")
        return super().dispatch(request, *args, **kwargs)


class UserListView(AdminRequiredMixin, ListView):
    """
    Отображает список всех пользователей.
    Фильтрация по роли (ученик, учитель, администратор).
    """
    model = User
    template_name = "director/users_list.html"
    context_object_name = "users"
    paginate_by = 30

    def get_queryset(self):
        qs = User.objects.all().order_by("role", "last_name")
        role = self.request.GET.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs


class UserRoleUpdateView(AdminRequiredMixin, UpdateView):
    """
    Позволяет директору изменить роль пользователя.
    После сохранения — автоматически добавляет пользователя в группу по роли.
    """
    model = User
    fields = ["role"]
    template_name = "director/user_role_form.html"
    success_url = reverse_lazy("director:user_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        group, _ = Group.objects.get_or_create(name=self.object.role)
        self.object.groups.set([group])
        return response


class ClassCreateView(AdminRequiredMixin, CreateView):
    """
    Создание нового класса (класс, литера, куратор).
    """
    model = ClassRoom
    fields = ["grade_level", "name", "curator"]
    template_name = "director/class_form.html"
    success_url = reverse_lazy("director:class_list")


class ClassListView(AdminRequiredMixin, ListView):
    """
    Отображает список всех классов школы.
    """
    model = ClassRoom
    template_name = "director/class_list.html"
    context_object_name = "classes"
    ordering = ["grade_level", "name"]


class SubjectCreateView(AdminRequiredMixin, CreateView):
    """
    Создание нового предмета с привязкой к преподавателю.
    """
    model = Subject
    fields = ["name", "teacher"]
    template_name = "director/subject_form.html"
    success_url = reverse_lazy("director:subject_list")


class SubjectListView(AdminRequiredMixin, ListView):
    """
    Отображает список всех учебных предметов.
    """
    model = Subject
    template_name = "director/subject_list.html"
    context_object_name = "subjects"
    ordering = ["name"]


class ClassStudentListView(ListView):
    """
    Просмотр списка учеников конкретного класса.
    Поддерживает поиск и сортировку по имени или фамилии.
    """
    model = Enrollment
    template_name = "director/class_students.html"
    context_object_name = "enrollments"

    def get_queryset(self):
        classroom = get_object_or_404(ClassRoom, pk=self.kwargs["pk"])
        qs = classroom.enrollments.select_related("student").all()

        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search)
            )

        sort = self.request.GET.get("sort", "last_name")
        if sort == "first_name":
            qs = qs.order_by("student__first_name")
        else:
            qs = qs.order_by("student__last_name")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["classroom"] = get_object_or_404(ClassRoom, pk=self.kwargs["pk"])
        context["current_sort"] = self.request.GET.get("sort", "last_name")
        return context


class ClassAddStudentView(AdminRequiredMixin, CreateView):
    """
    Добавление ученика в выбранный класс.
    Исключает уже зачисленных учеников из списка выбора.
    """
    model = Enrollment
    fields = ["student"]
    template_name = "director/class_add_student.html"

    def form_valid(self, form):
        form.instance.classroom_id = self.kwargs["pk"]
        return super().form_valid(form)

    def get_form(self):
        form = super().get_form()
        enrolled = Enrollment.objects.filter(classroom_id=self.kwargs["pk"]).values_list("student_id", flat=True)
        form.fields["student"].queryset = User.objects.filter(role="STUDENT").exclude(id__in=enrolled)
        return form

    def get_success_url(self):
        return reverse_lazy("director:class_students", kwargs={"pk": self.kwargs["pk"]})


def is_director(user):
    """
    Проверяет, является ли пользователь директором.
    """
    return user.is_authenticated and user.role == 'ADMIN'


@user_passes_test(is_director)
def class_students_view(request, class_id):
    """
    Отображает список учеников класса.
    Доступно только директору.
    Поддерживает поиск по имени или фамилии.
    """
    classroom = get_object_or_404(ClassRoom, id=class_id)
    query = request.GET.get("search", "").strip()

    enrollments = (
        classroom.enrollments
        .select_related("student")
        .order_by("student__last_name", "student__first_name")
    )

    if query:
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query)
        )

    context = {
        "classroom": classroom,
        "enrollments": enrollments,
        "search": query,
    }
    return render(request, "director/class_students.html", context)


@user_passes_test(is_director)
def add_lesson(request):
    """
    Создание нового урока директором.
    """
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Урок успешно создан.")
            return redirect('director:lesson_list')
    else:
        form = LessonForm()
    return render(request, 'director/add_lesson.html', {'form': form})


@user_passes_test(is_director)
def lesson_list(request):
    """
    Отображает список всех уроков в системе.
    Только для директора.
    """
    lessons = Lesson.objects.select_related('subject', 'teacher', 'classroom').order_by('-date')
    return render(request, 'director/lesson_list.html', {'lessons': lessons})
