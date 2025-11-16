from django.urls import path
from .views import CreateMemoryGame, AddPairToMemoryGame, GetMemoryGame, ListMemoryGamePairs, GetMemoryGameFull, AddPairsBulk, GetMemoryGameByCourseFull

urlpatterns = [
    path('memory-games/create', CreateMemoryGame.as_view()), #probado
    path('memory-games/<int:id>/pairs', ListMemoryGamePairs.as_view()), #probado
    path('memory-games/<int:game_id>/pairs', AddPairToMemoryGame.as_view()), #probado
    path('memory-games/<int:id>', GetMemoryGame.as_view()), #probado
    path('memory-games/<int:id>/full', GetMemoryGameFull.as_view()),
    path("memory-games/<int:game_id>/pairs/bulk", AddPairsBulk.as_view()),
    path('memory-games/by-course/<str:public_code>/full', GetMemoryGameByCourseFull.as_view()),
]
