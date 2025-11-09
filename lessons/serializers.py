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
        course = data.get('course') or self.instance.course
        order = data.get('order')
        is_game_linked = data.get('is_game_linked', False)

        # Validar orden consecutivo
        existing_orders = course.lessons.values_list('order', flat=True)
        if order not in [len(existing_orders) + 1, *existing_orders]:
            raise serializers.ValidationError("El número de orden debe ser consecutivo.")

        # Solo una lección con is_game_linked=True por curso
        if is_game_linked:
            qs = course.lessons.filter(is_game_linked=True)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("Solo puede haber una lección vinculada a un juego por curso.")
        return data