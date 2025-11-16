from rest_framework import serializers
from django.http import QueryDict
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    file = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    order = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


    def validate(self, attrs):
        course = attrs.get('course') or getattr(self.instance, 'course', None)
        if course is None:
            raise serializers.ValidationError({"course": "El curso es requerido."})

        # Determinar orden (si no viene o es null, se asigna automáticamente)
        order = attrs.get('order', getattr(self.instance, 'order', None))
        if order in (None, ''):
            existing = list(course.lessons.values_list('order', flat=True))
            attrs['order'] = (max(existing) + 1) if existing else 1
        else:
            try:
                order = int(order)
            except (TypeError, ValueError):
                raise serializers.ValidationError({"order": "El orden debe ser un número entero."})
            if order < 1:
                raise serializers.ValidationError({"order": "El orden debe ser un entero positivo."})
            attrs['order'] = order

        # Solo una lección con is_game_linked=True por curso
        is_game_linked = attrs.get('is_game_linked', getattr(self.instance, 'is_game_linked', False))
        if is_game_linked:
            qs = course.lessons.filter(is_game_linked=True)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({"is_game_linked": "Solo puede haber una lección vinculada a un juego por curso."})
        return attrs
