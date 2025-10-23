from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('1', 'Profesor'),
        ('2', 'Estudiante'),
    ]
    rol = models.CharField(max_length=1, choices=ROLE_CHOICES, default='2')
    estado_suscripcion = models.BooleanField(default=False)
    fecha_inicio_suscripcion = models.DateField(null=True, blank=True)
    fecha_fin_suscripcion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
