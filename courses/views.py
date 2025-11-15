from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Course, CourseSubscription
from lessons.models import Lesson, LessonProgress
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    CourseProgressSerializer,
    CourseSubscriptionSerializer,
)
from .permissions import IsProfessor, IsStudent
from .utils import update_course_progress


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

class MyCoursesStudentListView(generics.ListAPIView):
    """Lista únicamente los cursos del estudiante autenticado."""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    pagination_class = CoursesPagination

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(profesor=user).order_by('-created_at')


class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
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


class LessonProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        user = request.user
        if getattr(user, 'rol', None) != '2':
            return Response(
                {'detail': 'Solo los estudiantes pueden actualizar su progreso.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        lesson = get_object_or_404(Lesson, pk=lesson_id)
        completed = request.data.get('completed', True)
        if isinstance(completed, str):
            completed = completed.lower() in ['1', 'true', 'yes']
        completed = bool(completed)

        progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        progress.completed = completed
        progress.save()

        course_progress = update_course_progress(user, lesson.course)
        serializer = CourseProgressSerializer(course_progress, context={'request': request})

        return Response(
            {
                'message': 'Progreso actualizado',
                'lesson': {
                    'lesson_id': lesson.id,
                    'completed': progress.completed,
                    'completed_at': progress.completed_at,
                },
                'course_progress': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CourseProgressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, public_code):
        user = request.user
        if getattr(user, 'rol', None) != '2':
            return Response(
                {'detail': 'Solo los estudiantes pueden consultar su progreso.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, codigo=public_code, estado='publicado')
        course_progress = update_course_progress(user, course)
        serializer = CourseProgressSerializer(course_progress, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, public_code):
        user = request.user
        if getattr(user, 'rol', None) != '2':
            return Response(
                {'detail': 'Solo los estudiantes pueden suscribirse a un curso.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        course = get_object_or_404(Course, codigo=public_code, estado='publicado')
        subscription, created = CourseSubscription.objects.get_or_create(user=user, course=course)
        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.save()
        serializer = CourseSubscriptionSerializer(subscription, context={'request': request})
        return Response(
            {'message': 'Suscripción activada', 'subscription': serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, public_code):
        user = request.user
        if getattr(user, 'rol', None) != '2':
            return Response(
                {'detail': 'Solo los estudiantes pueden cancelar una suscripción.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        course = get_object_or_404(Course, codigo=public_code, estado='publicado')
        try:
            subscription = CourseSubscription.objects.get(user=user, course=course)
            subscription.is_active = False
            subscription.save()
            return Response({'message': 'Suscripción cancelada'}, status=status.HTTP_200_OK)
        except CourseSubscription.DoesNotExist:
            return Response({'detail': 'No existe una suscripción activa.'}, status=status.HTTP_404_NOT_FOUND)
