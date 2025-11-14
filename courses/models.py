from django.db import models
from django.conf import settings
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

    profesor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        db_column="professor_id",
    )

    # Información general
    titulo = models.CharField(max_length=150, db_column="title")
    codigo = models.CharField(max_length=50, blank=True, null=True, db_column="code")
    descripcion_corta = models.TextField(max_length=250, db_column="short_description")
    descripcion_detallada = models.TextField(blank=True, null=True, db_column="long_description")
    categoria = models.CharField(max_length=100, db_column="category")
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, db_column="level")
    duracion = models.PositiveIntegerField(blank=True, null=True, db_column="duration_hours")
    imagen_portada = models.URLField(blank=True, null=True, db_column="cover_image_url")

    # Publicación y trazabilidad
    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("publicado", "Publicado"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="publicado", db_column="status")
    created_at = models.DateTimeField(auto_now_add=True)

    # Gamificación
    gamificacion = models.BooleanField(default=False, db_column="gamification_enabled")
    tipo_gamificacion = models.CharField(
        max_length=100,
        choices=TIPO_GAMIFICACION_CHOICES,
        blank=True,
        null=True,
        db_column="gamification_type",
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

class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('in_progress','En progreso'),('completed','Completado')], default='in_progress')
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')


class CourseSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_subscriptions',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} -> {self.course} ({'Activo' if self.is_active else 'Inactivo'})"
