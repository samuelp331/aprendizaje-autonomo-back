from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth import authenticate, login
from .models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # Permitir registro sin autenticación y sin CSRF
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Usuario registrado exitosamente",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']

        user = serializer.validated_data['user_instance']

        if user.cuenta_bloqueada:
            return Response({"status": "error", "detail": "Cuenta bloqueada por intentos fallidos."}, status=status.HTTP_403_FORBIDDEN)

        user_auth = authenticate(request, username=email, password=password)
        if user_auth is None:
            # incrementar intentos y bloquear si llega a 3
            user.intentos_fallidos = (user.intentos_fallidos or 0) + 1
            if user.intentos_fallidos >= 3:
                user.cuenta_bloqueada = True
            user.save(update_fields=["intentos_fallidos", "cuenta_bloqueada"])
            return Response({"status": "error", "detail": "Correo o contraseña incorrectos."}, status=status.HTTP_400_BAD_REQUEST)

        # éxito: reiniciar intentos fallidos
        if user.intentos_fallidos or user.cuenta_bloqueada:
            user.intentos_fallidos = 0
            user.cuenta_bloqueada = False
            user.save(update_fields=["intentos_fallidos", "cuenta_bloqueada"])

        # Iniciar sesión de Django si vas a usar sesiones
        try:
            login(request, user_auth)
        except Exception:
            pass

        # emitir/obtener token de autenticación para DRF TokenAuthentication
        token, _ = Token.objects.get_or_create(user=user_auth)

        data = {
            "status": "ok",
            "message": "Login exitoso",
            "token": token.key,
            "user": {
                "id": user_auth.id,
                "email": user_auth.username,
                "first_name": user_auth.first_name,
                "last_name": user_auth.last_name,
                "rol": user_auth.rol,
            },
        }
        return Response(data, status=status.HTTP_200_OK)
