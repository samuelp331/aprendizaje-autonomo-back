from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer
from .permissions import IsProfessor


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsProfessor]

    def get_queryset(self):
        # Por defecto, lista solo los cursos del profesor autenticado
        user = self.request.user
        if hasattr(user, 'rol') and user.rol == '1':
            return Course.objects.filter(profesor=user)
        # Otros roles verán una lista vacía por defecto
        return Course.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Curso creado exitosamente',
                'course': serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
