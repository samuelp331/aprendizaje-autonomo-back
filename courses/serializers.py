from rest_framework import serializers
from .models import Course, CourseProgress, CourseSubscription
from lessons.models import LessonProgress, Lesson
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
    id = serializers.IntegerField(source='pk')
    public_code = serializers.CharField(source='codigo')
    image = serializers.SerializerMethodField()
    title = serializers.CharField(source='titulo')
    category = serializers.CharField(source='categoria')
    nivel = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'public_code',
            'image',
            'title',
            'category',
            'nivel',
            'duration',
            'description',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'rol', None) == '1':
            return True
        return CourseSubscription.objects.filter(user=user, course=obj, is_active=True).exists()

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
        if isinstance(url, str) and url.startswith('data:image'):
            try:
                return url.split(',')[1]
            except Exception:
                return ""
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


class LessonBriefSerializer(serializers.Serializer):
    title = serializers.CharField()
    duration = serializers.CharField(allow_blank=True, required=False)
    order = serializers.IntegerField()
    is_game_linked = serializers.BooleanField()
    locked = serializers.BooleanField()


class CourseDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='titulo')
    short_description = serializers.CharField(source='descripcion_corta')
    long_description = serializers.CharField(source='descripcion_detallada', allow_blank=True, allow_null=True)
    category = serializers.CharField(source='categoria')
    nivel = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'title',
            'short_description',
            'long_description',
            'category',
            'nivel',
            'duration',
            'cover_image',
            'lessons',
            'is_subscribed',
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

    def get_cover_image(self, obj: Course):
        url = obj.imagen_portada
        if not url:
            return ""
        if isinstance(url, str) and url.startswith('data:image'):
            try:
                return url.split(',')[1]
            except Exception:
                return ""
        try:
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                with urlopen(url) as resp:
                    ctype = resp.headers.get('Content-Type', '')
                    if not any(t in ctype for t in ("image/jpeg", "image/jpg", "image/png")):
                        return ""
                    data = resp.read(2 * 1024 * 1024 + 1)
                    if len(data) > 2 * 1024 * 1024:
                        return ""
                    return base64.b64encode(data).decode('ascii')
        except Exception:
            return ""
        return ""

    def _user_is_subscribed(self):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        # Profesores siempre pueden ver su propio contenido
        if getattr(user, 'rol', None) == '1':
            return True
        # Verificar suscripción específica al curso
        course = self.instance
        if course is not None:
            return CourseSubscription.objects.filter(user=user, course=course, is_active=True).exists()
        return False

    def get_is_subscribed(self, obj: Course):
        return self._user_is_subscribed()

    def get_lessons(self, obj: Course):
        request = self.context.get('request')
        is_subscribed = self._user_is_subscribed()
        items = []
        for lesson in getattr(obj, 'lessons', []).all().order_by('order'):
            resource_url = ''
            if getattr(lesson, 'file', None) and is_subscribed:
                resource_url = lesson.file.url
                if request is not None:
                    resource_url = request.build_absolute_uri(resource_url)
            items.append({
                'title': getattr(lesson, 'title', ''),
                'content': (getattr(lesson, 'content', '') or '') if is_subscribed else '',
                'duration': '',
                'order': getattr(lesson, 'order', 0),
                'is_game_linked': bool(getattr(lesson, 'is_game_linked', False)),
                'resource_url': resource_url,
                'locked': not is_subscribed,
            })
        return items


class CourseProgressSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.codigo')
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = CourseProgress
        fields = (
            'course',
            'completed_lessons',
            'total_lessons',
            'status',
            'completed_at',
            'lessons',
        )

    def get_lessons(self, obj: CourseProgress):
        user = obj.user
        lessons = obj.course.lessons.all().order_by('order')
        progress_map = {
            lp.lesson_id: lp
            for lp in LessonProgress.objects.filter(user=user, lesson__course=obj.course)
        }
        data = []
        for lesson in lessons:
            lp = progress_map.get(lesson.id)
            data.append({
                'lesson_id': lesson.id,
                'title': lesson.title,
                'order': lesson.order,
                'completed': lp.completed if lp else False,
                'completed_at': lp.completed_at if lp else None,
            })
        return data


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.codigo', read_only=True)

    class Meta:
        model = CourseSubscription
        fields = (
            'course',
            'is_active',
            'created_at',
            'updated_at',
        )
