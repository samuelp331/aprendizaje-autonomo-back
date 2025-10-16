from django.db import models
from users.models import User

class Course(models.Model):
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    descripcion_corta = models.TextField(max_length=250)
    descripcion_detallada = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100)
    nivel = models.CharField(max_length=50)
    duracion = models.PositiveIntegerField()
    gamificacion = models.BooleanField(default=False)
    tipo_gamificacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.titulo
