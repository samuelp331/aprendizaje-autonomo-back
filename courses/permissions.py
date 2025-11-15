from rest_framework.permissions import BasePermission


class IsProfessor(BasePermission):
    message = 'Solo los profesores pueden realizar esta acción.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'rol', None) == '1')

class IsStudent(BasePermission):
    message = 'Solo los estudiantes pueden realizar esta acción.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'rol', None) == '2')


