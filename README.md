# Loja Virtual - Formandos Pedagogia 2027

Sistema de loja virtual desenvolvido para o projeto de formatura da turma de Pedagogia 2027.

## Funcionalidades

- Catálogo de produtos
- Sistema de pagamentos
- Área administrativa
- Gerenciamento de compradores
- Controle de pedidos
- Interface responsiva

## Tecnologias Utilizadas

- Python 3.8+
- Django 4.2
- PostgreSQL
- Bootstrap 5
- Gunicorn
- Nginx

## Requisitos do Sistema

- Python 3.8 ou superior
- PostgreSQL
- Nginx (recomendado)
- Gunicorn

## Instruções para Desenvolvimento Local

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd [NOME_DO_PROJETO]
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

8. Acesse http://127.0.0.1:8000/

## Instruções para Deploy em Produção

### 1. Configuração do Ambiente

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd [NOME_DO_PROJETO]
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações

### 2. Configuração do Banco de Dados

1. Crie um banco de dados PostgreSQL:
```bash
createdb loja_db
```

2. Execute as migrações:
```bash
python manage.py migrate
```

3. Crie um superusuário:
```bash
python manage.py createsuperuser
```

### 3. Coleta de Arquivos Estáticos

```bash
python manage.py collectstatic
```

### 4. Configuração do Gunicorn

Crie um arquivo `gunicorn.service`:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=seu_usuario
Group=seu_grupo
WorkingDirectory=/caminho/para/seu/projeto
ExecStart=/caminho/para/venv/bin/gunicorn --workers 3 --bind unix:/caminho/para/seu/projeto/loja.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 5. Configuração do Nginx

Crie um arquivo de configuração para o Nginx:
```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /caminho/para/seu/projeto/staticfiles;
    }
    
    location /media/ {
        root /caminho/para/seu/projeto/mediafiles;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/caminho/para/seu/projeto/loja.sock;
    }
}
```

### 6. Iniciando o Serviço

1. Inicie o Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

2. Reinicie o Nginx:
```bash
sudo systemctl restart nginx
```

### 7. Verificação

Acesse seu domínio para verificar se tudo está funcionando corretamente.

### Manutenção

- Para atualizar o código:
```bash
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart gunicorn
```

- Para verificar logs:
```bash
sudo journalctl -u gunicorn
sudo tail -f /var/log/nginx/error.log
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 