from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Lesson
from .serializers import LessonSerializer

class IsProfessorOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'professor'

    def has_object_permission(self, request, view, obj):
        return obj.course.professor == request.user

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsProfessorOwner]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')
        queryset = Lesson.objects.filter(course__professor=user)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.professor != self.request.user:
            return Response({'detail': 'No tienes permiso para agregar lecciones a este curso.'}, status=403)
        serializer.save()
