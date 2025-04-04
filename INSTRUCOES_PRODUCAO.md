# Instruções para Colocar o Sistema em Produção

## 1. Preparação do Ambiente

### 1.1. Servidor
- Use um servidor Ubuntu 20.04 LTS ou superior
- Recomendado: 2GB RAM, 2 vCPUs, 20GB SSD
- Exemplo de provedores: DigitalOcean, AWS, Google Cloud, etc.

### 1.2. Domínio
- Registre um domínio (exemplo: seudominio.com.br)
- Configure o DNS para apontar para o IP do seu servidor
- Adicione os registros A e AAAA para o domínio e www

## 2. Configuração do Servidor

### 2.1. Acesso Inicial
```bash
# Conectar ao servidor
ssh usuario@seu-ip

# Atualizar sistema
sudo apt update && sudo apt upgrade -y
```

### 2.2. Instalar Dependências
```bash
# Instalar dependências básicas
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx memcached supervisor
```

### 2.3. Configurar PostgreSQL
```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco de dados e usuário
CREATE DATABASE loja;
CREATE USER loja_user WITH PASSWORD 'sua-senha-aqui';
ALTER ROLE loja_user SET client_encoding TO 'utf8';
ALTER ROLE loja_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE loja_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE loja TO loja_user;
\q
```

## 3. Configuração do Projeto

### 3.1. Clonar Projeto
```bash
# Criar diretório
mkdir /var/www/loja
cd /var/www/loja

# Clonar repositório
git clone seu-repositorio .

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3.2. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env.production

# Editar arquivo .env.production com suas configurações
nano .env.production
```

### 3.3. Configurar Nginx
```bash
# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/loja

# Conteúdo do arquivo (substitua os valores):
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.com www.seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    location /static/ {
        alias /var/www/loja/staticfiles/;
    }

    location /media/ {
        alias /var/www/loja/mediafiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Ativar site
sudo ln -s /etc/nginx/sites-available/loja /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3.4. Configurar Gunicorn
```bash
# Criar arquivo de configuração
sudo nano /etc/supervisor/conf.d/loja.conf

# Conteúdo do arquivo:
[program:loja]
command=/var/www/loja/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
directory=/var/www/loja
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/loja.err.log
stdout_logfile=/var/log/loja.out.log

# Atualizar supervisor
sudo supervisorctl reread
sudo supervisorctl update
```

### 3.5. Configurar SSL
```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

## 4. Finalização

### 4.1. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --noinput
```

### 4.2. Fazer Migrações
```bash
python manage.py migrate
```

### 4.3. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 4.4. Reiniciar Serviços
```bash
sudo supervisorctl restart loja
sudo systemctl restart nginx
```

## 5. Manutenção

### 5.1. Backup
```bash
# Backup do banco de dados
pg_dump -U loja_user loja > backup_$(date +%Y%m%d).sql

# Backup dos arquivos de mídia
tar -czf media_backup_$(date +%Y%m%d).tar.gz mediafiles/
```

### 5.2. Logs
```bash
# Verificar logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar logs da aplicação
sudo tail -f /var/log/loja.err.log
```

### 5.3. Atualizações
```bash
# Atualizar código
git pull

# Atualizar dependências
pip install -r requirements.txt

# Fazer migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Reiniciar aplicação
sudo supervisorctl restart loja
```

## 6. Segurança

### 6.1. Firewall
```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar regras
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 6.2. Fail2Ban
```bash
# Instalar Fail2Ban
sudo apt install -y fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl restart fail2ban
```

## 7. Monitoramento

### 7.1. Status dos Serviços
```bash
# Verificar status do Nginx
sudo systemctl status nginx

# Verificar status do Supervisor
sudo supervisorctl status

# Verificar status do PostgreSQL
sudo systemctl status postgresql
```

### 7.2. Recursos do Sistema
```bash
# Verificar uso de CPU e memória
htop

# Verificar espaço em disco
df -h

# Verificar logs em tempo real
sudo tail -f /var/log/nginx/access.log
``` 