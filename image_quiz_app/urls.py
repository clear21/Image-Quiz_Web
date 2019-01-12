# -*- coding: utf-8 -*-


from django.urls import path
from . import views

#ゲームスタート時の your_ans
start_your_ans = 99999

urlpatterns = [
        path('/' , views.index , name='index'),
        path('/game/<int:your_ans>/' , views.game , name='_game'),
        path('/game/' + str(start_your_ans) + '/' , views.game , name='game_start')
        ]