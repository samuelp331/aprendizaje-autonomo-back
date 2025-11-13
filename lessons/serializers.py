from rest_framework import serializers
from .models import Lesson
import os


class LessonSerializer(serializers.ModelSerializer):
    resource_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'resource_url']

    def get_resource_url(self, obj):
        if obj.file:
            url = obj.file.url
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return ""

    def validate_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext != '.pdf':
                raise serializers.ValidationError("Solo se permiten archivos .pdf.")
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no debe superar los 5 MB.")
        return value

    def validate(self, attrs):
        course = attrs.get('course') or getattr(self.instance, 'course', None)
        if course is None:
            raise serializers.ValidationError({"course": "El curso es requerido."})

        # Determinar si el cliente envió 'order' o no
        sent_order = 'order' in getattr(self, 'initial_data', {})
        order = attrs.get('order', getattr(self.instance, 'order', None))

        # Si no lo envió, asignar el siguiente consecutivo
        if not sent_order:
            existing = list(course.lessons.values_list('order', flat=True))
            attrs['order'] = (max(existing) + 1) if existing else 1
        else:
            # Validar que sea entero positivo
            if order is None or int(order) < 1:
                raise serializers.ValidationError({"order": "El orden debe ser un entero positivo."})

        # Solo una lección con is_game_linked=True por curso
        is_game_linked = attrs.get('is_game_linked', getattr(self.instance, 'is_game_linked', False))
        if is_game_linked:
            qs = course.lessons.filter(is_game_linked=True)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({"is_game_linked": "Solo puede haber una lección vinculada a un juego por curso."})
        return attrs
