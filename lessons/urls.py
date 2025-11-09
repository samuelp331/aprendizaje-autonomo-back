from rest_framework.routers import DefaultRouter
from .views import LessonViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')

urlpatterns = [
    path('', include(router.urls)),
]