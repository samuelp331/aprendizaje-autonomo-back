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


# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         user = authenticate(username=email, password=password)
#         if user is not None:
#             return Response({
#                 "message": "Inicio de sesión exitoso",
#                 "user": {
#                     "id": user.id,
#                     "username": user.email,
#                     "email": user.email,
#                 }
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)