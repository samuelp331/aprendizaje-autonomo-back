from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    MyCoursesListView,
    LessonProgressUpdateView,
    CourseProgressDetailView,
)


urlpatterns = [
    path('', CourseListCreateView.as_view(), name='courses-list-create'),
    path('teacher/', MyCoursesListView.as_view(), name='my-courses'),
    path('progress/courses/<str:public_code>/', CourseProgressDetailView.as_view(), name='course-progress-detail'),
    path('progress/lessons/<int:lesson_id>/', LessonProgressUpdateView.as_view(), name='lesson-progress-update'),
    path('<str:public_code>/', CourseDetailView.as_view(), name='course-detail'),
]
