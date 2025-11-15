from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('1', 'Profesor'),
        ('2', 'Estudiante'),
    ]
    rol = models.CharField(max_length=1, choices=ROLE_CHOICES, default='2', db_column='role')
    #estado_suscripcion = models.BooleanField(default=False, db_column='subscription_status')
    #fecha_inicio_suscripcion = models.DateField(null=True, blank=True, db_column='subscription_start_date')
    #fecha_fin_suscripcion = models.DateField(null=True, blank=True, db_column='subscription_end_date')
    intentos_fallidos = models.PositiveIntegerField(default=0, db_column='failed_attempts')
    cuenta_bloqueada = models.BooleanField(default=False, db_column='is_locked')
    read_only_fields = ('id', 'estado_suscripcion', 'fecha_inicio_suscripcion', 'fecha_fin_suscripcion')
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
