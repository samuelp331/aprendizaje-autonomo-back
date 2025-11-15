from rest_framework import serializers
from .models import Course, CourseProgress, CourseSubscription
from lessons.models import LessonProgress, Lesson


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
    short_description = serializers.CharField(source='descripcion_corta')
    long_description = serializers.CharField(source='descripcion_detallada')
    category = serializers.CharField(source='categoria')
    nivel = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    professor = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'public_code',
            'image',
            'title',
            'short_description',
            'long_description',
            'category',
            'nivel',
            'duration',
            'professor',
            'is_subscribed',
            'lessons',
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

    def get_image(self, obj: Course) -> str:
        return obj.imagen_portada or ""

    def get_professor(self, obj: Course):
        if obj.profesor:
            return {
                'id': obj.profesor.id,
                'name': f"{obj.profesor.first_name} {obj.profesor.last_name}".strip() or obj.profesor.username,
                'email': obj.profesor.email,
            }
        return None

    def get_lessons(self, obj: Course):
        return list(
            obj.lessons.all().order_by('order').values_list('id', flat=True)
        )


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
    professor = serializers.SerializerMethodField()
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
            'professor',
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
        return obj.imagen_portada or ""

    def get_lessons(self, obj: Course):
        return list(obj.lessons.all().order_by('order').values_list('id', flat=True))

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

    def get_professor(self, obj: Course):
        if obj.profesor:
            return {
                'id': obj.profesor.id,
                'name': f"{obj.profesor.first_name} {obj.profesor.last_name}".strip() or obj.profesor.username,
                'email': obj.profesor.email,
            }
        return None


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
