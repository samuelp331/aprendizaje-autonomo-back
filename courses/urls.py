from django.urls import path
from .views import CourseListCreateView, CourseDetailView


urlpatterns = [
    # /api/courses/
    path('', CourseListCreateView.as_view(), name='courses-list-create'),
    # /api/courses/<public_code>/
    path('<str:public_code>/', CourseDetailView.as_view(), name='course-detail'),
]

