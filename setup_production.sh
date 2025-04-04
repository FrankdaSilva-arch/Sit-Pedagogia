#!/bin/bash

# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências do sistema
sudo apt-get install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx memcached supervisor

# Criar diretórios necessários
mkdir -p logs
mkdir -p staticfiles
mkdir -p mediafiles

# Instalar dependências Python
pip3 install -r requirements.txt

# Configurar PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE loja;"
sudo -u postgres psql -c "CREATE USER loja_user WITH PASSWORD 'sua-senha-aqui';"
sudo -u postgres psql -c "ALTER ROLE loja_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE loja_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE loja_user SET timezone TO 'America/Sao_Paulo';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE loja TO loja_user;"

# Configurar Nginx
sudo tee /etc/nginx/sites-available/loja << EOF
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.com www.seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    location /static/ {
        alias /caminho/para/seu/projeto/staticfiles/;
    }

    location /media/ {
        alias /caminho/para/seu/projeto/mediafiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Configurar Gunicorn
sudo tee /etc/supervisor/conf.d/loja.conf << EOF
[program:loja]
command=/caminho/para/seu/virtualenv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
directory=/caminho/para/seu/projeto
user=seu-usuario
autostart=true
autorestart=true
stderr_logfile=/var/log/loja.err.log
stdout_logfile=/var/log/loja.out.log
EOF

# Configurar SSL com Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Coletar arquivos estáticos
python3 manage.py collectstatic --noinput

# Fazer migrações
python3 manage.py migrate

# Criar superusuário
python3 manage.py createsuperuser

# Reiniciar serviços
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl restart nginx 