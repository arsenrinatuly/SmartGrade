from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator



name_validator = RegexValidator(
    regex=r'^[А-Яа-яA-Za-zЁё-]{2,30}$',
    message="Имя и фамилия могут содержать только буквы и дефис (2–30 символов)."
)


phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message="Введите корректный номер телефона, например +71234567890."
)


class User(AbstractUser):
    """
    Кастомная модель пользователя с расширенными ролями и валидацией имени.

    Атрибуты:
        email (EmailField): основной идентификатор пользователя.
        role (CharField): роль в системе (Ученик, Учитель, Администратор).
        first_name (CharField): имя пользователя с валидацией.
        last_name (CharField): фамилия пользователя с валидацией.

    Методы:
        __str__(): возвращает строковое представление пользователя.
        is_admin(): проверяет, является ли пользователь администратором.
        is_teacher(): проверяет, является ли пользователь учителем.
        is_student(): проверяет, является ли пользователь учеником.
    """

    ROLE_CHOICES = (
        ('STUDENT', 'Ученик'),
        ('TEACHER', 'Учитель'),
        ('ADMIN', 'Администратор'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')


    first_name = models.CharField(
        max_length=30,
        validators=[name_validator],
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=30,
        validators=[name_validator],
        verbose_name="Фамилия"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """Возвращает e-mail и роль пользователя в виде строки."""
        return f"{self.email} ({self.role})"

    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == 'ADMIN' or self.is_superuser

    def is_teacher(self):
        """Проверяет, является ли пользователь учителем."""
        return self.role == 'TEACHER'

    def is_student(self):
        """Проверяет, является ли пользователь учеником."""
        return self.role == 'STUDENT'


class Profile(models.Model):
    """
    Модель профиля пользователя, содержащая дополнительную информацию.

    Атрибуты:
        user (OneToOneField): связь с моделью пользователя.
        photo (ImageField): аватар пользователя.
        bio (TextField): краткая биография.
        date_of_birth (DateField): дата рождения.
        phone (CharField): номер телефона с валидацией.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name="Телефон"
    )

    def __str__(self):
        """Возвращает строковое представление профиля с email пользователя."""
        return f"Профиль {self.user.email}"
