from rest_framework import serializers
from .models import MemoryGame, MemoryGamePair

class MemoryGamePairSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryGamePair
        fields = ("id", "question_text", "answer_text")

class MemoryGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryGame
        fields = "__all__" 

class GameWithPairsSerializer(serializers.ModelSerializer):
    pairs = MemoryGamePairSerializer(many=True, read_only=True) 
    class Meta:
        model = MemoryGame
        fields = (
            "id",
            "curso", 
            "nombre",
            "grid_size",
            "posicion",
            "pairs"
        )