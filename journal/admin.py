from django.contrib import admin
from .models import GradeRecord, AttendanceRecord

@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'value', 'max_value', 'date')
    list_filter = ('lesson__date', 'lesson__classroom', 'lesson__subject')
    search_fields = ('student__email', 'lesson__topic', 'lesson__subject__name')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'status')
    list_filter = ('status', 'lesson__date', 'lesson__classroom', 'lesson__subject')
    search_fields = ('student__email', 'lesson__topic', 'lesson__subject__name')
