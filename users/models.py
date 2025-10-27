from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    ]
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES)
    estado_suscripcion = models.BooleanField(default=False)
    fecha_inicio_suscripcion = models.DateField(null=True, blank=True)
    fecha_fin_suscripcion = models.DateField(null=True, blank=True)
    read_only_fields = ('id', 'estado_suscripcion', 'fecha_inicio_suscripcion', 'fecha_fin_suscripcion')
    def __str__(self):
        return self.username

def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password is not None:
            user.set_password(password)
            user.save()
        return user