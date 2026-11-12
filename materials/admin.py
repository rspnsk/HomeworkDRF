from django.contrib import admin
from .models import Course, Lesson

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    search_fields = ('title', 'description')

class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course')
    list_filter = ('course',)


# Регистрация в самом конце файла
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)