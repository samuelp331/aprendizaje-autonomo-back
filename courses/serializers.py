from rest_framework import serializers
from .models import Course
import base64
from urllib.parse import urlparse
from urllib.request import urlopen


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


class CourseListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    title = serializers.CharField(source='titulo')
    category = serializers.CharField(source='categoria')
    nivel = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'image',
            'title',
            'category',
            'nivel',
            'duration',
            'description',
        )

    def get_nivel(self, obj: Course) -> str:
        try:
            return obj.get_nivel_display()
        except Exception:
            return obj.nivel

    def get_duration(self, obj: Course) -> str:
        if obj.duracion is None:
            return ""
        return f"{obj.duracion} horas"

    def get_description(self, obj: Course) -> str:
        text = obj.descripcion_corta or ""
        return text[:150]

    def get_image(self, obj: Course) -> str:
        url = obj.imagen_portada
        if not url:
            return ""
        # Si ya viene en data URI base64, devolver solo el payload base64
        if isinstance(url, str) and url.startswith('data:image'):
            try:
                # data:image/png;base64,XXXX
                return url.split(',')[1]
            except Exception:
                return ""
        # Si es una URL http(s), intentar descargar y codificar
        try:
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                with urlopen(url) as resp:
                    ctype = resp.headers.get('Content-Type', '')
                    if not any(t in ctype for t in ("image/jpeg", "image/jpg", "image/png")):
                        return ""
                    clen = resp.headers.get('Content-Length')
                    if clen is not None:
                        try:
                            if int(clen) > 2 * 1024 * 1024:
                                return ""
                        except Exception:
                            pass
                    data = resp.read(2 * 1024 * 1024 + 1)
                    if len(data) > 2 * 1024 * 1024:
                        return ""
                    return base64.b64encode(data).decode('ascii')
        except Exception:
            return ""
        return ""
