import os
from pathlib import Path

# Defina BASE_DIR no início do arquivo
BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'loja',  # apenas este app
]

# Adicione/atualize estas configurações
DEBUG = True  # Ativar modo debug em desenvolvimento

ALLOWED_HOSTS = ['*']  # Permitir todos os hosts em desenvolvimento

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configurações de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Adicione uma SECRET_KEY (não use esta em produção)
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 'django-insecure-1234567890-sua-chave-secreta-aqui')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'loja',
        'USER': 'postgres',
        'PASSWORD': 'FSA171612',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}

# Configurações de idioma e fuso horário
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Manaus'
USE_I18N = True
USE_TZ = True

# Configurações de login
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'

# Configurações de sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas em segundos
SESSION_SAVE_EVERY_REQUEST = True

# Configurações do Admin
ADMIN_SITE_HEADER = "Administração do Sistema"
ADMIN_SITE_TITLE = "Portal de Administração"
ADMIN_INDEX_TITLE = "Bem-vindo ao Portal de Administração"

# Configurações do Admin
ADMIN_SITE_CSS = {
    'all': ('admin/css/custom_admin.css',),
}
