from django.apps import AppConfig
import os

class EventosConfig(AppConfig):
    name = 'eventos'
    verbose_name = 'Eventos'
    # path explícito elimina qualquer ambiguidade residual
    path = os.path.dirname(os.path.abspath(__file__))