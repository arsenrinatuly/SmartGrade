# accounts/views.py
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.urls import reverse
from django.conf import settings
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegistrationForm, ProfileForm
from django.contrib.auth.decorators import login_required


class EmailLoginView(View):
    """
    Представление для аутентификации пользователя по e-mail и паролю.

    Особенности:
    - Используется вместо стандартного `username`.
    - Проверяет активность учётной записи.
    - После успешного входа перенаправляет на `LOGIN_REDIRECT_URL` или 'dashboard'.
    """
    template_name = "accounts/login.html"

    def get(self, request):
        """Отображает форму входа, если пользователь не аутентифицирован."""
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL or reverse("dashboard"))
        return render(request, self.template_name, {"error": None})

    def post(self, request):
        """Обрабатывает ввод e-mail и пароля, выполняет вход при успешной проверке."""
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        U = get_user_model()
        user = U.objects.filter(email__iexact=email).first()  
        if not user or not user.check_password(password):
            return render(request, self.template_name, {"error": "Неверный e-mail или пароль."})
        if not user.is_active:
            return render(request, self.template_name, {"error": "Учётная запись деактивирована."})
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL or reverse("dashboard"))


class RegistrationView(CreateView):
    """
    Представление для регистрации нового пользователя.

    Использует форму `RegistrationForm` и шаблон `accounts/register.html`.
    После успешного создания перенаправляет на страницу входа.
    """
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")


@login_required
def profile_view(request):
    """
    Представление профиля пользователя.

    Поддерживает два режима:
    - Просмотр (edit_mode=False)
    - Редактирование профиля (edit_mode=True)

    При POST-запросе обновляет данные профиля и сохраняет изменения.
    """
    profile = request.user.profile
    edit_mode = request.GET.get("edit") == "true"

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'edit_mode': edit_mode,
    }
    return render(request, 'accounts/profile.html', context)
