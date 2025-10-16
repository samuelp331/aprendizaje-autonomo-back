from django.db import models
from courses.models import Course

class Lesson(models.Model):
    curso = models.ForeignKey(Course, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    archivo = models.FileField(upload_to='lecciones/', blank=True, null=True)
    orden = models.PositiveIntegerField()
    is_game_linked = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
