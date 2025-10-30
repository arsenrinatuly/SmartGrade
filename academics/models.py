from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

User = settings.AUTH_USER_MODEL


class Subject(models.Model):
    """
    Модель учебного предмета.

    Атрибуты:
        name (CharField): название предмета.
        code (CharField): уникальный код предмета (генерируется автоматически).
        teacher (ForeignKey): преподаватель, ведущий данный предмет.

    Методы:
        __str__(): возвращает читаемое название предмета с кодом.
        save(): при отсутствии кода генерирует уникальный slug-код.
    """

    name = models.CharField("Название", max_length=100)
    code = models.CharField("Код", max_length=20, unique=True, blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'TEACHER'},
        related_name="subjects",
        verbose_name="Учитель"
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self):
        """Возвращает строковое представление предмета в формате «Название (Код)»."""
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        """
        При сохранении автоматически генерирует уникальный код предмета,
        если поле `code` не заполнено.
        """
        if not self.code:
            base_code = slugify(self.name, allow_unicode=False)[:8].upper()
            unique_suffix = uuid.uuid4().hex[:4].upper()
            self.code = f"{base_code}-{unique_suffix}"
        super().save(*args, **kwargs)


class ClassRoom(models.Model):
    """
    Модель школьного класса.

    Атрибуты:
        name (CharField): буква или обозначение класса.
        grade_level (PositiveSmallIntegerField): уровень обучения (номер класса).
        curator (ForeignKey): куратор класса (учитель).
    """

    name = models.CharField("Буква класса", max_length=50)
    grade_level = models.PositiveSmallIntegerField("Уровень (класс)")
    curator = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="curated_classes",
        limit_choices_to={'role': 'TEACHER'},
        verbose_name="Куратор (учитель)"
    )

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        ordering = ["grade_level", "name"]

    def __str__(self):
        """Возвращает строковое представление класса, например '5А'."""
        return f"{self.grade_level}{self.name}"


class Enrollment(models.Model):
    """
    Модель зачисления ученика в класс.

    Атрибуты:
        student (ForeignKey): пользователь-ученик.
        classroom (ForeignKey): класс, в который зачислен ученик.
        date_enrolled (DateField): дата зачисления.

    Ограничения:
        - Каждый ученик может быть зачислен только в один экземпляр конкретного класса.
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name="enrollments",
        verbose_name="Ученик"
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Класс"
    )
    date_enrolled = models.DateField("Дата зачисления", auto_now_add=True)

    class Meta:
        verbose_name = "Зачисление"
        verbose_name_plural = "Зачисления"
        unique_together = ('student', 'classroom')
        ordering = ["classroom", "student"]

    def __str__(self):
        """Возвращает строку вида 'Ученик → Класс'."""
        return f"{self.student} → {self.classroom}"


class Lesson(models.Model):
    """
    Модель урока.

    Атрибуты:
        subject (ForeignKey): предмет, к которому относится урок.
        classroom (ForeignKey): класс, в котором проводится урок.
        teacher (ForeignKey): учитель, ведущий урок.
        date (DateField): дата проведения.
        topic (CharField): тема урока.
    """

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Предмет"
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Класс"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'TEACHER'},
        related_name="lessons",
        verbose_name="Учитель"
    )
    date = models.DateField("Дата проведения")
    topic = models.CharField("Тема урока", max_length=255, blank=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["-date"]

    def __str__(self):
        """Возвращает строку вида '2025-03-12 — 5А — Математика'."""
        return f"{self.date} — {self.classroom} — {self.subject}"
