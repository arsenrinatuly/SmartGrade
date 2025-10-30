from django.db import models
from django.conf import settings
from academics.models import Lesson

User = settings.AUTH_USER_MODEL


class GradeRecord(models.Model):
    """
    Модель для хранения оценок учащихся за уроки.

    Атрибуты:
        lesson (ForeignKey): ссылка на урок, к которому относится оценка.
        student (ForeignKey): ссылка на ученика, получившего оценку.
        value (DecimalField): значение оценки.
        max_value (DecimalField): максимальный возможный балл (по умолчанию 100).
        note (CharField): комментарий к оценке (необязательно).
        date (DateField): дата выставления оценки.

    Ограничения:
        unique_together: каждый ученик может иметь только одну запись об оценке за конкретный урок.
    """

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Урок'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name='Ученик'
    )
    value = models.DecimalField('Оценка', max_digits=5, decimal_places=2)
    max_value = models.DecimalField('Макс. балл', max_digits=5, decimal_places=2, default=100)
    note = models.CharField('Комментарий', max_length=255, blank=True)
    date = models.DateField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ('lesson', 'student')
        ordering = ['-date']

    def __str__(self):
        """Возвращает строку вида 'Иванов Иван · Математика 5А · 90/100'."""
        return f"{self.student} · {self.lesson} · {self.value}/{self.max_value}"


class AttendanceRecord(models.Model):
    """
    Модель для учета посещаемости учащихся.

    Атрибуты:
        lesson (ForeignKey): ссылка на урок, к которому относится запись.
        student (ForeignKey): ссылка на ученика.
        status (CharField): статус посещаемости (был, отсутствовал, опоздал).
        comment (CharField): дополнительный комментарий (например, причина отсутствия).

    Ограничения:
        unique_together: один ученик может иметь только одну запись посещаемости за конкретный урок.
    """

    class Status(models.TextChoices):
        """Перечисление возможных статусов посещаемости."""
        PRESENT = 'P', 'Был'
        ABSENT = 'A', 'Отсутствовал'
        LATE = 'L', 'Опоздал'

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attendance',
        verbose_name='Урок'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name='Ученик'
    )
    status = models.CharField('Статус', max_length=1, choices=Status.choices)
    comment = models.CharField('Комментарий', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        unique_together = ('lesson', 'student')

    def __str__(self):
        """Возвращает строку вида 'Иванов Иван · 5А Математика · Был'."""
        return f"{self.student} · {self.lesson} · {self.get_status_display()}"
