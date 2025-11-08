from django.urls import path
from .views import CourseListCreateView


urlpatterns = [
    # /api/courses/
    path('', CourseListCreateView.as_view(), name='courses-list-create'),
]

