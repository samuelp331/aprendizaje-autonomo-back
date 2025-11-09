from django.urls import path
from .views import UserListCreate, UserDetail, RegisterView, LoginView

urlpatterns = [
    # /api/users/
    path('', UserListCreate.as_view(), name='users-list'),
    # /api/users/<id>/
    path('<int:pk>/', UserDetail.as_view(), name='user-detail'),
    # /api/users/register/
    path('register/', RegisterView.as_view(), name='user-register'),
    # /api/users/login/
    path('login/', LoginView.as_view(), name='user-login'),
]
