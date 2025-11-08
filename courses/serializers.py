from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'titulo',
            'codigo',
            'descripcion_corta',
            'descripcion_detallada',
            'categoria',
            'nivel',
            'duracion',
            'imagen_portada',
            'gamificacion',
            'tipo_gamificacion',
            'profesor',
        ]
        read_only_fields = ('id', 'profesor')

    def validate(self, attrs):
        # Si gamificación está activa, tipo_gamificacion es obligatorio
        if attrs.get('gamificacion') and not attrs.get('tipo_gamificacion'):
            raise serializers.ValidationError({
                'tipo_gamificacion': 'Debe seleccionar un tipo de gamificación cuando está activada.'
            })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return Course.objects.create(profesor=user, **validated_data)
