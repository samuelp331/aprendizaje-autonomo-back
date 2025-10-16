from django.http import JsonResponse

def test_connection(request):
    return JsonResponse({
        "status": "ok",
        "message": "El backend está conectado correctamente ✅"
    })
