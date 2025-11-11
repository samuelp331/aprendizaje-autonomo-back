from django.urls import path
from .views import CourseListCreateView, CourseDetailView, MyCoursesListView


urlpatterns = [
    # /api/courses/
    path('', CourseListCreateView.as_view(), name='courses-list-create'),
    path('teacher/', MyCoursesListView.as_view(), name='my-courses'),
    path('<str:public_code>/', CourseDetailView.as_view(), name='course-detail'),
]

