import os
import logging
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING_CONFIG = None

# Cria o diretório de logs se não existir
log_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(
            log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
}
