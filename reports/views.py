from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from academics.models import ClassRoom, Enrollment, Lesson
from journal.models import GradeRecord
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
import os
from accounts.models import User
from django.utils import timezone
from django.db.models import Q


def user_is_teacher_or_director(user):
    """
    Проверяет, является ли пользователь учителем или администратором.

    Аргументы:
        user (User): текущий пользователь.

    Возвращает:
        bool: True, если пользователь — учитель или администратор.
    """
    return user.is_authenticated and user.role in ["TEACHER", "ADMIN"]


@login_required
def class_report(request, class_id):
    """
    Отображает HTML-страницу с отчётом по успеваемости всего класса.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        class_id (int): идентификатор класса.

    Возвращает:
        HttpResponse: HTML-страница с таблицей оценок и средними баллами.
    """
    classroom = get_object_or_404(ClassRoom, id=class_id)

    if not user_is_teacher_or_director(request.user):
        return HttpResponseForbidden("Доступ запрещён")

    enrollments = Enrollment.objects.filter(classroom=classroom).select_related('student')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    subject = request.GET.get('subject')

    grades = GradeRecord.objects.filter(student__in=[e.student for e in enrollments])

    if start_date:
        grades = grades.filter(date__gte=start_date)
    if end_date:
        grades = grades.filter(date__lte=end_date)
    if subject:
        grades = grades.filter(lesson__subject__id=subject)

    student_data = []
    for enroll in enrollments:
        student_grades = grades.filter(student=enroll.student)
        avg = (
            round(sum(g.value for g in student_grades) / student_grades.count(), 2)
            if student_grades.exists() else '-'
        )
        student_data.append({
            'student': enroll.student,
            'average': avg,
            'grades': student_grades
        })

    context = {
        'classroom': classroom,
        'students': student_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'reports/class_report.html', context)


@login_required
def class_report_pdf(request, class_id):
    """
    Генерирует PDF-отчёт по успеваемости класса.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        class_id (int): идентификатор класса.

    Возвращает:
        HttpResponse: PDF-файл со списком учеников, средними баллами и комментариями.
    """
    classroom = get_object_or_404(ClassRoom, id=class_id)
    enrollments = Enrollment.objects.filter(classroom=classroom).select_related('student')
    grades = GradeRecord.objects.filter(student__in=[e.student for e in enrollments])

    buffer = BytesIO()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='DejaVuSans', fontSize=10, leading=12)
    elements = []

  
    title = Paragraph(f"<b>Отчёт по классу {classroom}</b>", ParagraphStyle('Title', fontName='DejaVuSans', fontSize=16))
    date_info = Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y')}", normal_style)
    author_info = Paragraph(f"Сформировал: {request.user.get_full_name()}", normal_style)
    elements += [title, Spacer(1, 12), date_info, author_info, Spacer(1, 20)]


    data = [[
        Paragraph("<b>Ученик</b>", normal_style),
        Paragraph("<b>Средний балл</b>", normal_style),
        Paragraph("<b>Кол-во оценок</b>", normal_style),
        Paragraph("<b>Комментарий</b>", normal_style)
    ]]

    for enroll in enrollments:
        student_grades = grades.filter(student=enroll.student)
        avg = round(sum(g.value for g in student_grades) / student_grades.count(), 2) if student_grades.exists() else "-"
        comment_text = ", ".join(g.note for g in student_grades if g.note) or "-"
        data.append([
            Paragraph(f"{enroll.student.last_name} {enroll.student.first_name}", normal_style),
            Paragraph(str(avg), normal_style),
            Paragraph(str(student_grades.count()), normal_style),
            Paragraph(comment_text, normal_style),
        ])

    table = Table(data, colWidths=[130, 70, 80, 200])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"class_report_{classroom}.pdf\"'
    return response


@login_required
def student_report_pdf(request, student_id):
    """
    Генерирует PDF-отчёт по оценкам конкретного ученика.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        student_id (int): идентификатор ученика.

    Возвращает:
        HttpResponse: PDF-документ с таблицей оценок, средним баллом и комментариями.
    """
    student = get_object_or_404(User, id=student_id, role='STUDENT')
    grades = GradeRecord.objects.filter(student=student).select_related('lesson__subject', 'lesson__classroom')

    buffer = BytesIO()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='DejaVuSans', fontSize=10, leading=12)
    elements = []

    title = Paragraph(f"<b>Отчёт об успеваемости ученика</b>", ParagraphStyle('Title', fontName='DejaVuSans', fontSize=16))
    elements += [title, Spacer(1, 12)]
    elements.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y')}", normal_style))
    elements.append(Paragraph(f"Сформировал: {request.user.get_full_name()}", normal_style))
    elements.append(Spacer(1, 20))

    data = [[
        Paragraph("<b>Предмет</b>", normal_style),
        Paragraph("<b>Класс</b>", normal_style),
        Paragraph("<b>Тема урока</b>", normal_style),
        Paragraph("<b>Оценка</b>", normal_style),
        Paragraph("<b>Макс. балл</b>", normal_style),
        Paragraph("<b>Дата</b>", normal_style),
        Paragraph("<b>Комментарий</b>", normal_style)
    ]]

    for g in grades:
        data.append([
            Paragraph(g.lesson.subject.name, normal_style),
            Paragraph(str(g.lesson.classroom), normal_style),
            Paragraph(g.lesson.topic or "-", normal_style),
            Paragraph(str(g.value), normal_style),
            Paragraph(str(g.max_value), normal_style),
            Paragraph(g.date.strftime("%d.%m.%Y"), normal_style),
            Paragraph(g.note or "-", normal_style)
        ])

    avg = round(sum(g.value for g in grades) / grades.count(), 2) if grades.exists() else "-"
    data.append([Paragraph("<b>Средний балл</b>", normal_style), "", "", "", "", "", Paragraph(f"<b>{avg}</b>", normal_style)])

    table = Table(data, colWidths=[70, 50, 100, 50, 50, 60, 120])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"student_report_{student.last_name}.pdf\"'
    return response


@login_required
def student_search(request):
    """
    Позволяет искать ученика по имени, фамилии или логину.

    Аргументы:
        request (HttpRequest): HTTP-запрос.

    Возвращает:
        HttpResponse: HTML-страница с результатами поиска.
    """
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = User.objects.filter(
            role='STUDENT'
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )
    return render(request, 'reports/student_search.html', {'query': query, 'results': results})


@login_required
def student_report(request, student_id):
    """
    Отображает страницу отчёта об успеваемости конкретного ученика в HTML-формате.
    """
    student = get_object_or_404(User, id=student_id, role='STUDENT')
    grades = GradeRecord.objects.filter(student=student).select_related('lesson__subject', 'lesson__classroom')
    avg = round(sum(g.value for g in grades) / grades.count(), 2) if grades.exists() else None
    classroom = grades.first().lesson.classroom if grades.exists() else None

    return render(request, 'reports/student_report.html', {
        'student': student,
        'grades': grades,
        'average': avg,
        'classroom': classroom,
    })


@login_required
def class_attendance_report_pdf(request, class_id):
    """
    Генерирует PDF-отчёт по посещаемости класса.

    Аргументы:
        request (HttpRequest): HTTP-запрос.
        class_id (int): идентификатор класса.

    Возвращает:
        HttpResponse: PDF-файл с данными посещаемости.
    """
    from journal.models import AttendanceRecord
    classroom = get_object_or_404(ClassRoom, id=class_id)
    enrollments = Enrollment.objects.filter(classroom=classroom).select_related('student')
    records = AttendanceRecord.objects.filter(student__in=[e.student for e in enrollments])

    buffer = BytesIO()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='DejaVuSans', fontSize=10, leading=12)
    elements = []

    title = Paragraph(f"<b>Отчёт по посещаемости класса {classroom}</b>", ParagraphStyle('Title', fontName='DejaVuSans', fontSize=16))
    date_info = Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y')}", normal_style)
    author_info = Paragraph(f"Сформировал: {request.user.get_full_name()}", normal_style)
    elements += [title, Spacer(1, 12), date_info, author_info, Spacer(1, 20)]

    data = [[
        Paragraph("<b>Ученик</b>", normal_style),
        Paragraph("<b>Дата</b>", normal_style),
        Paragraph("<b>Предмет</b>", normal_style),
        Paragraph("<b>Статус</b>", normal_style),
        Paragraph("<b>Комментарий</b>", normal_style),
    ]]

    for record in records:
        data.append([
            Paragraph(f"{record.student.last_name} {record.student.first_name}", normal_style),
            Paragraph(record.lesson.date.strftime('%d.%m.%Y'), normal_style),
            Paragraph(str(record.lesson.subject), normal_style),
            Paragraph(dict(record.Status.choices).get(record.status, '—'), normal_style),
            Paragraph(record.comment or "-", normal_style),
        ])

    table = Table(data, colWidths=[120, 70, 100, 70, 150])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"attendance_report_{classroom}.pdf\"'
    return response
