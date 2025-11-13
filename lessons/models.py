from django.db import models
from django.core.exceptions import ValidationError
from courses.models import Course
import os



def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Solo se permiten archivos PDF (.pdf).")
    if value.size > 5 * 1024 * 1024:  # 5 MB
        raise ValidationError("El archivo no debe superar los 5 MB.")



def lesson_file_path(instance, filename):
    return f'lessons/files/{filename}'



class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=lesson_file_path, validators=[validate_file_extension], blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    is_game_linked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order') 

    
    def clean(self):
        
        if self.is_game_linked:
            existing = Lesson.objects.filter(course=self.course, is_game_linked=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Solo puede haber una lección con juego por curso.")

    def __str__(self):
        # Course mantiene campo Python 'titulo' (db_column 'title')
        course_title = getattr(self.course, 'titulo', None) or ''
        return f"{self.title} ({course_title})"
