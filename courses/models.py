from django.db import models
from django.core.exceptions import ValidationError
from users.models import User


class Course(models.Model):
    NIVEL_CHOICES = [
        ("basico", "Básico"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado"),
    ]

    TIPO_GAMIFICACION_CHOICES = [
        ("memoria", "Juego de memoria"),
    ]

    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")

    # Información general
    titulo = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion_corta = models.TextField(max_length=250)
    descripcion_detallada = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    duracion = models.PositiveIntegerField(blank=True, null=True)
    imagen_portada = models.URLField(blank=True, null=True)

    # Publicación y trazabilidad
    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("publicado", "Publicado"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="publicado")
    created_at = models.DateTimeField(auto_now_add=True)

    # Gamificación
    gamificacion = models.BooleanField(default=False)
    tipo_gamificacion = models.CharField(
        max_length=100,
        choices=TIPO_GAMIFICACION_CHOICES,
        blank=True,
        null=True,
    )

    def clean(self):
        # Si se activa gamificación, exigir tipo de gamificación
        if self.gamificacion and not self.tipo_gamificacion:
            raise ValidationError({
                "tipo_gamificacion": "Debe seleccionar un tipo de gamificación cuando está activada."
            })

    def __str__(self):
        return self.titulo

    class Meta:
        constraints = [
            # Si gamificación está activa, tipo_gamificacion no puede ser NULL
            models.CheckConstraint(
                check=(
                    models.Q(gamificacion=False)
                    | models.Q(gamificacion=True, tipo_gamificacion__isnull=False)
                ),
                name="chk_tipo_gamificacion_requerido_si_activo",
            )
        ]
