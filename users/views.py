from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        print("📩 Datos recibidos:", request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado correctamente ✅"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username") 
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password) 
        
        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Inicio de sesión exitoso",
                "tokens": tokens,
                "email": user.email
            }, status=status.HTTP_200_OK)
        else:
            # ⭐️ CAMBIAR A 400 BAD REQUEST ⭐️
            return Response(
                {"error": "Credenciales inválidas (nombre de usuario o contraseña incorrectos)"}, 
                status=status.HTTP_400_BAD_REQUEST # <--- Código 400 es más preciso aquí
            )