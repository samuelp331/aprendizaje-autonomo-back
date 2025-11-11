from rest_framework.routers import DefaultRouter
from .views import LessonViewSet

router = DefaultRouter()
#/api/lessons/
router.register(r'', LessonViewSet, basename='lesson')

urlpatterns = router.urls
