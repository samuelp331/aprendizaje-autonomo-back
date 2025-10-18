from django.shortcuts import render, redirect
from .forms import RegistroForm
from django.contrib import messages

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            rol = form.cleaned_data.get('rol')

            messages.success(request, 'Usuario registrado con éxito.')

            # Redirección según rol
            if rol == 'profesor':
                return redirect('/panel_profesor/')
            else:
                return redirect('/panel_estudiante/')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()

    return render(request, 'users/register.html', {'form': form})
