from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Lesson
from .serializers import LessonSerializer
from courses.models import CourseSubscription


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')
        role = getattr(user, 'rol', None)

        if role == '1':  # Profesor: ver solo sus cursos
            qs = Lesson.objects.filter(course__profesor=user)
        elif role == '2':  # Estudiante: ver cursos con suscripción activa
            qs = Lesson.objects.filter(
                course__subscriptions__user=user,
                course__subscriptions__is_active=True,
            )
        else:
            qs = Lesson.objects.none()

        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs.order_by('order')

    def perform_create(self, serializer):
        if getattr(self.request.user, 'rol', None) != '1':
            raise PermissionDenied('Solo los profesores pueden crear lecciones.')
        course = serializer.validated_data.get('course')
        if not course or course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para agregar lecciones a este curso.')
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if getattr(self.request.user, 'rol', None) != '1' or instance.course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para modificar esta lección.')
        serializer.save()

    def perform_destroy(self, instance):
        if getattr(self.request.user, 'rol', None) != '1' or instance.course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para eliminar esta lección.')
        instance.delete()
