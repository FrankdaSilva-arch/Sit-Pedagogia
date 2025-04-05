from .settings import *

# Desativar modo debug em produção
DEBUG = False

# Configurar hosts permitidos
ALLOWED_HOSTS = ['*']

# Desativar logging completamente
LOGGING_CONFIG = None
LOGGING = {}

# Configurações de banco de dados MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'FRANKPED2025$default',  # Nome do banco de dados existente
        'USER': 'FRANKPED2025',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sua_senha'),
        'HOST': 'FRANKPED2025.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Configurações de arquivos estáticos e mídia
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
