from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Course
from .serializers import CourseSerializer, CourseListSerializer, CourseDetailSerializer
from .permissions import IsProfessor


class CoursesPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsProfessor]
    pagination_class = CoursesPagination

    def get_queryset(self):
        # GET: listar cursos publicados con filtros opcionales
        if self.request.method == 'GET':
            qs = Course.objects.filter(estado='publicado').order_by('-created_at')
            category = self.request.query_params.get('category')
            level = self.request.query_params.get('level')
            if category:
                qs = qs.filter(categoria__iexact=category)
            if level:
                level_norm = level.strip().lower()
                # Acepta 'basico' / 'básico' o etiquetas
                mapping = {
                    'básico': 'basico',
                    'basico': 'basico',
                    'intermedio': 'intermedio',
                    'avanzado': 'avanzado',
                }
                qs = qs.filter(nivel=mapping.get(level_norm, level_norm))
            return qs

        # POST: cursos del profesor autenticado
        user = self.request.user
        if hasattr(user, 'rol') and user.rol == '1':
            return Course.objects.filter(profesor=user)
        return Course.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsProfessor()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CourseListSerializer
        return CourseSerializer

    def list(self, request, *args, **kwargs):
        # Validación simple de parámetros de paginación
        for param in ("page", "page_size"):
            val = request.query_params.get(param)
            if val is not None:
                try:
                    iv = int(val)
                    if iv <= 0:
                        raise ValueError
                except ValueError:
                    return Response({
                        'detail': f'Parámetro inválido: {param} debe ser un entero positivo.'
                    }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MyCoursesListView(generics.ListAPIView):
    """Lista únicamente los cursos del profesor autenticado."""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsProfessor]
    pagination_class = CoursesPagination

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(profesor=user).order_by('-created_at')


class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        from django.shortcuts import get_object_or_404
        public_code = self.kwargs.get('public_code')
        return get_object_or_404(Course, codigo=public_code, estado='publicado')

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
