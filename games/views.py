from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MemoryGame # Asegúrate de que MemoryGame apunta al modelo actualizado
from .serializers import MemoryGameSerializer, MemoryGamePairSerializer, GameWithPairsSerializer
import logging
from django.db import transaction
import traceback
from  courses.models import Course
logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
# ----------------------------------------------------
# GET /memory-games/{id}
# ----------------------------------------------------
class GetMemoryGame(APIView):
    def get(self, request, id):
        try:
            game = MemoryGame.objects.get(id=id)
        except MemoryGame.DoesNotExist:
            return Response({"error": "El juego no existe"}, status=404)

        serializer = MemoryGameSerializer(game)
        return Response(serializer.data, status=200)


# ----------------------------------------------------
# GET /memory-games/{id}/pairs
# ----------------------------------------------------
class ListMemoryGamePairs(APIView):
    def get(self, request, id):
        try:
            try:
                game = MemoryGame.objects.get(id=id)
            except MemoryGame.DoesNotExist:
                return Response({"error": "El juego no existe"}, status=status.HTTP_404_NOT_FOUND)
            
            # Asumo que el related_name es 'pairs' o 'memorygamepair_set'
            pairs = game.pairs.all() 
            serializer = MemoryGamePairSerializer(pairs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error al listar pares del juego {id}: {e}", exc_info=True)
            return Response(
                {"error": "Ocurrió un error interno al procesar la solicitud."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
# ----------------------------------------------------
# POST /memory-games (CORREGIDO)
# ----------------------------------------------------
class CreateMemoryGame(APIView):
    def post(self, request):
        data = request.data
        # 1. Cambiar de 'leccion' a 'curso'
        curso_id = data.get('curso') 
        
        if not curso_id:
            # 2. Actualizar el mensaje de error
            return Response({"detail": "El ID del curso es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. Cambiar el campo de filtro a 'curso'
            if MemoryGame.objects.filter(curso=curso_id).exists(): 
                return Response(
                    # 4. Actualizar el mensaje de conflicto
                    {"detail": f"Ya existe un juego de memoria asociado al curso ID {curso_id}."},
                    status=status.HTTP_409_CONFLICT 
                )
        except Exception:
            # 5. Actualizar el mensaje de error de verificación
            return Response({"detail": "Error al verificar el curso."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MemoryGameSerializer(data=data)
        
        if serializer.is_valid():
            game = serializer.save()
            return Response({
                "message": "Juego creado correctamente",
                "game": MemoryGameSerializer(game).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------
# POST /memory-games/{id}/pairs
# ---------------------------------------------
class AddPairToMemoryGame(APIView):
    def post(self, request, game_id):
        try:
            game = MemoryGame.objects.get(id=game_id)
        except MemoryGame.DoesNotExist:
            return Response({"error": "El juego no existe"}, status=404)
        
        data = request.data.copy()
        # Asumo que el campo ForeignKey en MemoryGamePair es 'juego'
        data["juego"] = game.id 

        serializer = MemoryGamePairSerializer(data=data)

        if serializer.is_valid():
            pair = serializer.save()
            return Response({
                "message": "Par agregado correctamente",
                "pair": MemoryGamePairSerializer(pair).data
            }, status=201)

        return Response(serializer.errors, status=400)


# ----------------------------------------------------
# GET COMPLETO (Juego + Pares)
# ----------------------------------------------------
class GetMemoryGameFull(APIView):
    def get(self, request, id):
        try:
            try:
                game = MemoryGame.objects.get(id=id)
            except MemoryGame.DoesNotExist:
                return Response({"error": "El juego no existe"}, status=404)

            serializer = GameWithPairsSerializer(game)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error(f"Error al listar todo el juego {id}: {e}", exc_info=True)

            return Response(
                {"error": "Ocurrió un error interno al procesar la solicitud."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetMemoryGameByCourseFull(APIView):
    def get(self, request, public_code):
        try:
            course = get_object_or_404(Course, codigo=public_code)
            game = MemoryGame.objects.get(curso=course)
        
        except MemoryGame.DoesNotExist:
         return Response({"game": None, "pairs": []}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Ocurrió un error interno al procesar la solicitud."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = GameWithPairsSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AddPairsBulk(APIView):
    def post(self, request, game_id):
        try:
            game = MemoryGame.objects.get(id=game_id)
        except MemoryGame.DoesNotExist:
            return Response({"error": "El juego no existe"}, status=404)

        pairs_data = request.data.get("pairs", [])

        if not isinstance(pairs_data, list) or len(pairs_data) == 0:
            return Response({"error": "Debe enviar una lista de pares"}, status=400)

        created_pairs = []

        try:
            with transaction.atomic():
                for index, pair in enumerate(pairs_data):
                    serializer = MemoryGamePairSerializer(data=pair)

                    if serializer.is_valid():
                        created = serializer.save(juego=game) 
                        created_pairs.append(created)
                    else:
                        # Se puede usar raise serializers.ValidationError para DRF estándar
                        transaction.set_rollback(True)
                        return Response({
                            "error": f"Error en el par #{index + 1}",
                            "details": serializer.errors,
                            "pair_data": pair
                        }, status=400)

        except Exception as e:
            logger.error(f"Error en AddPairsBulk para el juego {game_id}: {traceback.format_exc()}", exc_info=True)
            return Response({
                "error": "Error inesperado al procesar los pares",
                "details": str(e),
            }, status=500)

        return Response(
            {
                "message": "Pares agregados correctamente",
                "pairs": MemoryGamePairSerializer(created_pairs, many=True).data
            },
            status=201
        )