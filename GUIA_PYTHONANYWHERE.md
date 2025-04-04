# Guia de Configuração no PythonAnywhere

## 1. Criar Conta no PythonAnywhere

1. Acesse https://www.pythonanywhere.com/
2. Clique em "Create a Beginner account" (plano gratuito para testes)
3. Preencha o formulário de registro
4. Verifique seu email

## 2. Configurar Banco de Dados MySQL

1. No painel do PythonAnywhere, vá em "Databases"
2. Clique em "Create a new database"
3. Anote:
   - Nome do banco de dados
   - Nome de usuário
   - Senha
   - Hostname

## 3. Configurar Ambiente Virtual

1. No console web, execute:
```bash
# Criar ambiente virtual
mkvirtualenv --python=/usr/bin/python3.8 venv

# Ativar ambiente virtual
workon venv

# Instalar dependências
pip install -r requirements.txt
```

## 4. Fazer Upload do Código

1. No painel, vá em "Files"
2. Crie um diretório para seu projeto
3. Faça upload de todos os arquivos do projeto
4. Certifique-se que a estrutura está correta

## 5. Configurar Aplicação Web

1. No painel, vá em "Web"
2. Clique em "Add a new web app"
3. Escolha "Manual configuration"
4. Selecione Python 3.8
5. Em "Virtualenv", selecione o ambiente criado
6. Em "Source code", selecione o diretório do projeto
7. Em "WSGI configuration file", edite o arquivo:
```python
import os
import sys

path = '/home/seu_usuario/caminho/para/seu/projeto'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_pythonanywhere'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 6. Configurar Arquivos Estáticos

1. No console web, execute:
```bash
python manage.py collectstatic
```

2. No painel "Web", em "Static files":
   - URL: /static/
   - Directory: /home/seu_usuario/caminho/para/seu/projeto/staticfiles

3. Em "Media files":
   - URL: /media/
   - Directory: /home/seu_usuario/caminho/para/seu/projeto/mediafiles

## 7. Configurar Banco de Dados

1. No console web, execute:
```bash
# Fazer migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

## 8. Configurar Domínio

1. No painel "Web", em "Domains":
   - Use o subdomínio gratuito (seu_usuario.pythonanywhere.com)
   - Ou configure um domínio personalizado (requer plano pago)

## 9. Reiniciar Aplicação

1. No painel "Web", clique em "Reload"
2. Aguarde alguns segundos
3. Acesse seu site pelo URL fornecido

## 10. Verificar Logs

1. No painel "Web", em "Error log"
2. Verifique se há erros
3. Corrija qualquer problema encontrado

## 11. Configurações Adicionais

### Backup
1. No console web, execute:
```bash
# Backup do banco de dados
mysqldump -u seu_usuario -p seu_banco > backup.sql
```

### Atualizações
1. Para atualizar o código:
```bash
# Atualizar código
git pull

# Atualizar dependências
pip install -r requirements.txt

# Fazer migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Reiniciar aplicação (no painel Web)
```

## 12. Solução de Problemas Comuns

### Erro 500
1. Verifique os logs de erro
2. Verifique se todas as configurações estão corretas
3. Verifique se o banco de dados está acessível

### Arquivos Estáticos não Carregam
1. Verifique se o collectstatic foi executado
2. Verifique as configurações de static files no painel
3. Verifique as permissões dos arquivos

### Banco de Dados não Conecta
1. Verifique as credenciais
2. Verifique se o banco de dados existe
3. Verifique se o usuário tem permissões

## 13. Dicas Importantes

1. Sempre faça backup antes de atualizações
2. Mantenha o ambiente virtual atualizado
3. Monitore os logs regularmente
4. Use o plano gratuito para testes antes de migrar para produção 