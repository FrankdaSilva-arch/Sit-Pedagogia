import logging

# Configura o logger
logger = logging.getLogger(__name__)

# Log da configuração de timezone
logger.info(f"Timezone configurado: {TIME_ZONE}")

MIDDLEWARE = [
    # ... existing middleware ...
    'loja.middleware.RelogioDigitalMiddleware',
    # ... existing middleware ...
]
