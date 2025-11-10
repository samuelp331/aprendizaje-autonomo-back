from rest_framework import serializers
from .models import Lesson
from courses.models import Course
import os

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    # --- Validación de archivos PDF/Word ---
    def validate_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.pdf', '.docx']:
                raise serializers.ValidationError("Solo se permiten archivos .pdf o .docx.")
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no debe superar los 5 MB.")
        return value

    # --- Validaciones generales ---
    def validate(self, data):
        course = data.get('course') or getattr(self.instance, 'course', None)
        order = data.get('order')
        is_game_linked = data.get('is_game_linked', False)

        # Validar orden consecutivo
        if course and order is not None:
            existing_orders = course.lessons.values_list('order', flat=True)
            if order not in [len(existing_orders) + 1, *existing_orders]:
                raise serializers.ValidationError("El número de orden debe ser consecutivo.")

        # --- Validar is_game_linked (solo una por curso gamificado) ---
        if course and is_game_linked:
            # Verifica si el curso es gamificado
            if hasattr(course, "is_gamified") and course.is_gamified:
                existing = course.lessons.filter(is_game_linked=True)
                if self.instance:
                    existing = existing.exclude(id=self.instance.id)
                if existing.exists():
                    existing_lesson = existing.first()
                    raise serializers.ValidationError({
                        "is_game_linked": f"Ya existe una lección con juego asignado: '{existing_lesson.title}'."
                    })
            else:
                raise serializers.ValidationError({
                    "is_game_linked": "Este curso no es gamificado, no puede asignar una lección con juego."
                })

        return data