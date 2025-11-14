from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    MyCoursesListView,
    LessonProgressUpdateView,
    CourseProgressDetailView,
    CourseSubscriptionView,
)


urlpatterns = [
    path('', CourseListCreateView.as_view(), name='courses-list-create'), #probado
    path('teacher/', MyCoursesListView.as_view(), name='my-courses'), #probado
    path('progress/courses/<str:public_code>/', CourseProgressDetailView.as_view(), name='course-progress-detail'), #probado
    path('progress/lessons/<int:lesson_id>/', LessonProgressUpdateView.as_view(), name='lesson-progress-update'), #probado
    path('<str:public_code>/subscribe/', CourseSubscriptionView.as_view(), name='course-subscription'),
    path('<str:public_code>/', CourseDetailView.as_view(), name='course-detail'), #probado
]
