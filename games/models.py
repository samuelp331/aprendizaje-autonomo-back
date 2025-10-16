from django.db import models
from lessons.models import Lesson

class MemoryGame(models.Model):
    leccion = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    posicion = models.CharField(max_length=20, choices=[('inicio', 'Inicio'), ('mitad', 'Mitad'), ('final', 'Final')])
    grid_size = models.CharField(max_length=10)
    # estado = models.CharField(max_length=20, default='publicado')

    def __str__(self):
        return self.nombre

class MemoryGamePair(models.Model):
    juego = models.ForeignKey(MemoryGame, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to='juegos/')
    answer_text = models.CharField(max_length=255)
    pair_id = models.IntegerField()

    def __str__(self):
        return f"Pair {self.id} - {self.juego.nombre}"
