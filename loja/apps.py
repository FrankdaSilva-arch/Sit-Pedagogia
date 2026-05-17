from django.apps import AppConfig
import os

class LojaConfig(AppConfig):
    name = 'loja'
    verbose_name = 'Loja'
    path = os.path.dirname(os.path.abspath(__file__))