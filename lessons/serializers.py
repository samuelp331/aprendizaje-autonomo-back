from rest_framework import serializers
from .models import Lesson
import os

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.pdf', '.docx']:
                raise serializers.ValidationError("Solo se permiten archivos .pdf o .docx.")
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no debe superar los 5 MB.")
        return value

    def validate(self, data):
        course = data.get('course') or getattr(self.instance, 'course', None)
        order = data.get('order', getattr(self.instance, 'order', None))
        is_game_linked = data.get('is_game_linked', getattr(self.instance, 'is_game_linked', False))

        if course is None:
            raise serializers.ValidationError({"course": "El curso es requerido."})

        # Orden: si no se envía, asignar siguiente disponible; si se envía, debe ser >=1
        if order is None:
            existing_orders = list(course.lessons.values_list('order', flat=True))
            data['order'] = (max(existing_orders) + 1) #if existing_orders else 1
        elif int(order) < 1:
            raise serializers.ValidationError({"order": "El orden debe ser un entero positivo."})

        # Solo una lección con is_game_linked=True por curso
        if is_game_linked:
            qs = course.lessons.filter(is_game_linked=True)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({"is_game_linked": "Solo puede haber una lección vinculada a un juego por curso."})
        return data
