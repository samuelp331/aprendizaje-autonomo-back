from django.urls import path
from .views import CourseListCreateView, CourseDetailView, MyCoursesListView


urlpatterns = [
    # /api/courses/
    path('', CourseListCreateView.as_view(), name='courses-list-create'),
    # /api/courses/my/ -> cursos del profesor autenticado
    path('my/', MyCoursesListView.as_view(), name='my-courses'),
    # /api/courses/<public_code>/
    path('<str:public_code>/', CourseDetailView.as_view(), name='course-detail'),
]

