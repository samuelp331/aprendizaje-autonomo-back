from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MemoryGame
from .serializers import MemoryGameSerializer, MemoryGamePairSerializer, GameWithPairsSerializer
import logging
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
logger = logging.getLogger(__name__)

class ListMemoryGamePairs(APIView):
    def get(self, request, id):
        try:
            try:
                game = MemoryGame.objects.get(id=id)
            except MemoryGame.DoesNotExist:
                return Response({"error": "El juego no existe"}, status=status.HTTP_404_NOT_FOUND)
            
            pairs = game.pairs.all()
            serializer = MemoryGamePairSerializer(pairs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:

            logger.error(f"Error al listar pares del juego {id}: {e}", exc_info=True)

            return Response(
                {"error": "Ocurrió un error interno al procesar la solicitud."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# -----------------------------
# POST /memory-games
# -----------------------------
class CreateMemoryGame(APIView):
    def post(self, request):
        serializer = MemoryGameSerializer(data=request.data)
        
        if serializer.is_valid():
            game = serializer.save()
            return Response({
                "message": "Juego creado correctamente",
                "game": MemoryGameSerializer(game).data
            }, status=201)
        
        return Response(serializer.errors, status=400)


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
        data["juego"] = game.id  # clave correcta

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

