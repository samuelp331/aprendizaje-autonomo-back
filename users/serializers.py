from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'rol',
        ]

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Este campo es obligatorio."})
        email_lc = email.strip().lower()
        # Validar unicidad mapeada a username=email
        if User.objects.filter(username=email_lc).exists():
            raise serializers.ValidationError({"email": "Ya existe un usuario con este correo."})
        attrs['email'] = email_lc
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Usar email como username si no se envía explícitamente
        email = validated_data.get('email')
        username = validated_data.get('username') or email

        user = User(username=username, **validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError({"detail": "Correo y contraseña son requeridos."})

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Correo o contraseña incorrectos."})

        if user.cuenta_bloqueada:
            raise serializers.ValidationError({"detail": "Cuenta bloqueada por intentos fallidos."})

        attrs['user_instance'] = user
        return attrs
