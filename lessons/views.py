from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Lesson
from .serializers import LessonSerializer
from courses.permissions import IsProfessor


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsProfessor]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')
        qs = Lesson.objects.filter(course__profesor=user)
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs.order_by('order')

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not course or course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para agregar lecciones a este curso.')
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para modificar esta lección.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.course.profesor != self.request.user:
            raise PermissionDenied('No tienes permiso para eliminar esta lección.')
        instance.delete()
