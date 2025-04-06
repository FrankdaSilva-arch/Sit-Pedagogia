from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Produto, Pedido, Comprovante, ConfiguracaoPagamento, Comprador, Moeda, LogAcesso
from .forms import ComprovanteForm
from django.core.files.storage import FileSystemStorage
import logging
from django.db import connection
from django.urls import reverse
import os
from django.conf import settings
import sys
from datetime import datetime
import traceback
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import qrcode
import base64
from io import BytesIO
from django.utils import timezone
from django.core import serializers
import json
from django.db.models import Sum
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
import pytz

# Configurar logging
logger = logging.getLogger(__name__)

print("CARREGANDO VIEWS DA LOJA")

# Adicionar no início do arquivo, após os imports


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'loja/lista_produtos.html', {'produtos': produtos})


def carrinho(request):
    return render(request, 'loja/carrinho.html')


def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    # Lógica para adicionar ao carrinho
    return redirect('carrinho')


def remover_do_carrinho(request, produto_id):
    # Lógica para remover do carrinho
    return redirect('carrinho')


def checkout(request):
    return render(request, 'loja/checkout.html')


def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    return render(request, 'loja/detalhe_pedido.html', {'pedido': pedido})


def meus_pedidos(request):
    pedidos = Pedido.objects.filter(nome_comprador=request.user.username)
    return render(request, 'loja/meus_pedidos.html', {'pedidos': pedidos})


def enviar_comprovante(request, pedido_id):
    print(f"\n{Colors.CYAN}=== Iniciando envio de comprovante ==={Colors.END}")
    print(f"{Colors.BLUE}Pedido ID: {pedido_id}{Colors.END}")

    pedido = get_object_or_404(Pedido, pk=pedido_id)
    print(f"{Colors.GREEN}Pedido encontrado: {pedido}{Colors.END}")

    if request.method == 'POST':
        print(f"{Colors.YELLOW}Método POST recebido{Colors.END}")
        if request.FILES.get('comprovante'):
            print(
                f"{Colors.GREEN}Arquivo recebido: {request.FILES['comprovante'].name}{Colors.END}")
            Comprovante.objects.create(
                pedido=pedido,
                arquivo=request.FILES['comprovante']
            )
            print(f"{Colors.GREEN}Comprovante criado com sucesso{Colors.END}")

            # Atualiza o status do pedido para Confirmação de Pagamento
            pedido.status = 'AGUARDANDO_CONFIRMACAO'
            pedido.save()
            print(
                f"{Colors.GREEN}Status do pedido atualizado para AGUARDANDO_CONFIRMACAO{Colors.END}")

            messages.success(request, 'Comprovante enviado com sucesso!')
            print(
                f"{Colors.GREEN}Redirecionando para página de confirmação{Colors.END}")
            return redirect('loja:confirmacao_compra', pedido_id=pedido_id)
        else:
            print(f"{Colors.RED}Nenhum arquivo foi enviado{Colors.END}")
            messages.error(
                request, 'Por favor, selecione um arquivo para enviar.')
            return redirect('loja:pagamento', produto_id=pedido.produto.id, pedido_id=pedido_id)

    print(f"{Colors.YELLOW}Método não é POST, redirecionando para página de pagamento{Colors.END}")
    return redirect('loja:pagamento', produto_id=pedido.produto.id, pedido_id=pedido_id)


def visualizar_pagamentos(request):
    print("\n=== DEBUG: Iniciando visualizar_pagamentos ===")
    print(f"Sessão atual: {request.session.items()}")

    # Verifica se o usuário tem permissão de acesso
    if not request.session.get('tem_acesso'):
        print("=== DEBUG: Sem acesso, redirecionando para verificar_senha ===")
        return redirect('loja:verificar_senha')

    # Não limpa a permissão de acesso para manter a sessão
    print(
        f"\n=== DEBUG: Nome do usuário na sessão: {request.session.get('nome_usuario')}")
    print(
        f"=== DEBUG: Tem acesso na sessão: {request.session.get('tem_acesso')}")

    # Busca todos os produtos
    produtos = Produto.objects.all()

    # Para cada produto, busca seus pedidos e compradores sem cotas
    dados_produtos = []
    for produto in produtos:
        print(f"\nProcessando produto: {produto.nome}")

        # Busca os pedidos deste produto
        pedidos = Pedido.objects.filter(produto=produto).order_by('-data')

        # Ajusta o horário para GMT-4 em todos os pedidos
        for pedido in pedidos:
            pedido.data = pedido.data - timezone.timedelta(hours=4)
            print(f"=== DEBUG: Data do pedido ajustada: {pedido.data}")

        # Busca compradores que não compraram cotas deste produto
        compradores_sem_cotas = []
        compradores_com_cotas = set(
            pedido.nome_comprador for pedido in pedidos if pedido.nome_comprador)
        for comprador in Comprador.objects.all():
            if comprador.nome not in compradores_com_cotas:
                compradores_sem_cotas.append(comprador)

        # Formata o mês/ano em português
        if produto.data_cadastro:
            meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            mes_ano = f"{meses[produto.data_cadastro.month]}/{produto.data_cadastro.year}"
        else:
            mes_ano = None

        # Adiciona os dados do produto à lista
        dados_produtos.append({
            'produto': produto,
            'pedidos': pedidos,
            'compradores_sem_cotas': compradores_sem_cotas,
            'mes_ano': mes_ano
        })

    # Busca ou cria a configuração de pagamento
    configuracao, created = ConfiguracaoPagamento.objects.get_or_create(
        id=1,
        defaults={
            'valor_quota': 10.00,
            'data_vencimento': timezone.now().date()
        }
    )

    # Obtém o nome do usuário da sessão
    nome_usuario = request.session.get('nome_usuario', 'Usuário')
    print(
        f"\n=== DEBUG: Nome do usuário passado para o template: {nome_usuario}")
    print(f"=== DEBUG: Sessão completa: {request.session.items()}")

    # Cria o contexto com todas as variáveis necessárias
    context = {
        'dados_produtos': dados_produtos,
        'configuracao': configuracao,
        'nome_usuario': nome_usuario,
        'tem_acesso': request.session.get('tem_acesso', False),
        'request': request
    }

    print(f"=== DEBUG: Contexto enviado para o template: {context}")

    return render(request, 'loja/visualizar_pagamentos.html', context)


@staff_member_required
def iniciar_contagem(request):
    if not request.user.is_staff:
        messages.error(
            request, 'Você não tem permissão para realizar esta ação.')
        return redirect('admin:index')

    try:
        # Salva todos os pedidos existentes com seus comprovantes
        pedidos = []
        for pedido in Pedido.objects.all():
            pedido_data = {
                'id': pedido.id,
                'nome_comprador': pedido.nome_comprador,
                'produto': pedido.produto,
                'cota': pedido.cota,
                'valor': pedido.valor,
                'status': pedido.status,
                'data': pedido.data,
                'comprovantes': list(pedido.comprovantes.all().values())
            }
            pedidos.append(pedido_data)

        total_pedidos = len(pedidos)
        print(f"Total de pedidos encontrados: {total_pedidos}")

        # Deleta todos os pedidos (os comprovantes serão deletados em cascata)
        Pedido.objects.all().delete()
        print("Todos os pedidos foram deletados")

        # Reseta o contador interno do SQLite
        with connection.cursor() as cursor:
            # Primeiro, verifica se a tabela existe
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='loja_pedido'")
            if cursor.fetchone():
                # Reseta o contador interno do SQLite
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name='loja_pedido'")
                cursor.execute(
                    "INSERT INTO sqlite_sequence (name, seq) VALUES ('loja_pedido', 0)")
                print("Contador interno do SQLite foi resetado")

        # Recria os pedidos com IDs sequenciais começando do 1
        for i, pedido_data in enumerate(pedidos, 1):
            # Cria o pedido com a data original
            novo_pedido = Pedido.objects.create(
                id=i,
                nome_comprador=pedido_data['nome_comprador'],
                produto=pedido_data['produto'],
                cota=pedido_data['cota'],
                valor=pedido_data['valor'],
                status=pedido_data['status'],
                data=pedido_data['data']
            )

            # Recria os comprovantes associados ao pedido
            for comprovante_data in pedido_data['comprovantes']:
                Comprovante.objects.create(
                    pedido=novo_pedido,
                    arquivo=comprovante_data['arquivo'],
                    data_envio=comprovante_data['data_envio']
                )

            print(f"Pedido recriado com ID {i}")

        messages.success(
            request, f'Contagem reiniciada com sucesso. {total_pedidos} pedidos foram recriados.')
    except Exception as e:
        messages.error(request, f'Erro ao reiniciar contagem: {str(e)}')
        print(f"Erro: {str(e)}")

    return redirect('admin:loja_pedido_changelist')


def comprar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    return render(request, 'loja/detalhe_produto.html', {'produto': produto})


def iniciar_pagamento(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    # Configurar o SDK do Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Criar preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": f"Pedido #{pedido.id}",
                "quantity": pedido.quantidade,
                "unit_price": float(pedido.total),
                "currency_id": "BRL"
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri('/pagamento/sucesso/'),
            "failure": request.build_absolute_uri('/pagamento/falha/'),
            "pending": request.build_absolute_uri('/pagamento/pendente/')
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return render(request, 'loja/pagamento.html', {
        'preference_id': preference['id'],
        'pedido': pedido,
    })


def pagamento_sucesso(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')

    if payment_id and status == 'approved':
        # Atualizar status do pedido
        pedido = Pedido.objects.get(payment_id=payment_id)
        pedido.status = 'pago'
        pedido.save()

    return render(request, 'loja/pagamento_sucesso.html')


def upload_comprovante(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        form = ComprovanteForm(request.POST, request.FILES)
        if form.is_valid():
            comprovante = form.save(commit=False)
            comprovante.pedido = pedido
            comprovante.save()
            messages.success(request, 'Comprovante enviado com sucesso!')
            return redirect('loja:sucesso')
    else:
        form = ComprovanteForm()

    return render(request, 'loja/upload_comprovante.html', {
        'form': form,
        'pedido': pedido
    })


def sucesso(request):
    return render(request, 'loja/sucesso.html')


def lista_pagamentos(request):
    pagamentos = Pedido.objects.filter(status='pago').order_by('-data')
    total_pago = sum(pedido.valor for pedido in pagamentos)

    context = {
        'pagamentos': pagamentos,
        'total_pago': total_pago,
        'quantidade_pagamentos': pagamentos.count()
    }
    return render(request, 'loja/lista_pagamentos.html', context)


def cadastrar_produto(request):
    if request.method == 'POST':
        try:
            produto = Produto.objects.create(
                nome=request.POST['nome'],
                preco=request.POST['preco'],
                descricao=request.POST['descricao'],
                estoque=request.POST['estoque']
            )
            return redirect('loja:lista_produtos')
        except Exception as e:
            print(f"Erro ao salvar produto: {str(e)}")
    return render(request, 'loja/cadastrar_produto.html')


def buscar_compradores(request):
    termo = request.GET.get('term', '')
    print(f"\n{Colors.CYAN}=== Buscando compradores ==={Colors.END}")
    print(f"{Colors.BLUE}Termo de busca: {termo}{Colors.END}")

    if termo:
        compradores = Comprador.objects.filter(nome__icontains=termo)
        resultados = [{'label': c.nome, 'value': c.nome} for c in compradores]
        print(
            f"{Colors.GREEN}Compradores encontrados: {[c.nome for c in compradores]}{Colors.END}")
        return JsonResponse(resultados, safe=False)
    return JsonResponse([], safe=False)


def verificar_cota(request, produto_id, cota):
    try:
        print(f"\n{Colors.CYAN}=== Iniciando verificação de cota ==={Colors.END}")
        print(f"{Colors.BLUE}Produto ID: {produto_id}, Cota: {cota}{Colors.END}")

        produto = get_object_or_404(Produto, pk=produto_id)
        cota = int(cota)
        print(f"{Colors.GREEN}Produto encontrado: {produto.nome}{Colors.END}")

        # Verifica se a cota está dentro do range permitido
        print(f"{Colors.YELLOW}Verificando range da cota: {produto.cota_inicial} - {produto.cota_final}{Colors.END}")
        if cota < produto.cota_inicial or cota > produto.cota_final:
            print(f"{Colors.RED}Cota fora do range permitido{Colors.END}")
            return JsonResponse({
                'cota_ocupada': True,
                'mensagem': 'Verifique o número da cota'
            })

        # Verifica se existe pedido pendente
        print(
            f"{Colors.YELLOW}Verificando pedidos PENDENTES para a cota {cota}{Colors.END}")
        pedido_pendente = Pedido.objects.filter(
            produto=produto,
            cota=cota,
            status='AGUARDANDO_PAGAMENTO'
        ).first()

        if pedido_pendente:
            print(
                f"{Colors.YELLOW}Pedido pendente encontrado: ID {pedido_pendente.id}{Colors.END}")
            return JsonResponse({
                'pedido_pendente': True,
                'mensagem': 'Falta o comprovante de pagamento, você será direcionado para lá',
                'pedido_id': pedido_pendente.id,
                'produto_id': produto.id
            })

        # Verifica se existe pedido pago para o comprador
        nome_comprador = request.GET.get('nome_comprador')
        if nome_comprador:
            pedido_pago = Pedido.objects.filter(
                produto=produto,
                nome_comprador=nome_comprador,
                status='PAGO'
            ).first()

            if pedido_pago:
                print(
                    f"{Colors.YELLOW}Pedido pago encontrado para o comprador: {nome_comprador}{Colors.END}")
                return JsonResponse({
                    'cota_ocupada': True,
                    'mensagem': 'Você já comprou essa cota'
                })

            # Verifica se existe comprovante para o comprador
            pedido_com_comprovante = Pedido.objects.filter(
                produto=produto,
                nome_comprador=nome_comprador,
                comprovantes__isnull=False
            ).first()

            if pedido_com_comprovante:
                print(
                    f"{Colors.YELLOW}Comprovante encontrado para o comprador: {nome_comprador}{Colors.END}")
                return JsonResponse({
                    'cota_ocupada': True,
                    'mensagem': 'Confirmação de pagamento'
                })

        print(f"{Colors.GREEN}Cota disponível para compra{Colors.END}")
        return JsonResponse({
            'cota_disponivel': True,
            'mensagem': 'Cota disponível'
        })

    except ValueError:
        print(f"{Colors.RED}Erro: Cota inválida{Colors.END}")
        return JsonResponse({
            'cota_ocupada': True,
            'mensagem': 'Cota inválida'
        })
    except Exception as e:
        print(f"{Colors.RED}Erro ao verificar cota: {str(e)}{Colors.END}")
        return JsonResponse({
            'cota_ocupada': True,
            'mensagem': 'Erro ao verificar cota'
        })


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    return render(request, 'loja/detalhe_produto.html', {'produto': produto})


def confirmar_compra(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        nome_comprador = request.POST.get('nome_comprador')
        cota = request.POST.get('cota')

        if nome_comprador and cota:
            try:
                cota = int(cota)
                # Cria o pedido com status AGUARDANDO_PAGAMENTO
                pedido = Pedido.objects.create(
                    produto=produto,
                    nome_comprador=nome_comprador,
                    cota=cota,
                    valor=produto.preco,
                    status='AGUARDANDO_PAGAMENTO'
                )
                return JsonResponse({
                    'status': 'success',
                    'redirect_url': reverse('loja:pagamento', kwargs={'produto_id': produto.id, 'pedido_id': pedido.id})
                })
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'A cota deve ser um número válido.'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Todos os campos são obrigatórios.'
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido.'
    })


def pagamento(request, produto_id, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, produto_id=produto_id)
    configuracao = ConfiguracaoPagamento.objects.first()

    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(configuracao.chave_pix)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Converter imagem para base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    qr_code_url = f"data:image/png;base64,{img_str}"

    context = {
        'pedido': pedido,
        'configuracao': configuracao,
        'qr_code_url': qr_code_url,
    }

    return render(request, 'loja/pagamento.html', context)


def buscar_pedido(request):
    if request.method == 'POST':
        nome_comprador = request.POST.get('nome_comprador')
        if nome_comprador:
            pedidos = Pedido.objects.filter(
                nome_comprador__icontains=nome_comprador,
                status='AGUARDANDO_PAGAMENTO'
            )
            return render(request, 'loja/buscar_pedido.html', {
                'pedidos': pedidos,
                'nome_buscado': nome_comprador
            })
    return render(request, 'loja/buscar_pedido.html')


def registrar_comprador_selecionado(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        print(f"\n{Colors.CYAN}=== Comprador Selecionado ==={Colors.END}")
        print(f"{Colors.GREEN}Nome: {nome}{Colors.END}")
    return JsonResponse({'status': 'success'})


@staff_member_required
def iniciar_contagem_compradores(request):
    if not request.user.is_superuser:
        messages.error(
            request, 'Você não tem permissão para realizar esta ação.')
        return redirect('admin:index')

    try:
        # Salva todos os compradores existentes
        compradores = []
        for comprador in Comprador.objects.all():
            comprador_data = {
                'id': comprador.id,
                'nome': comprador.nome,
                'email': comprador.email,
                'data_cadastro': comprador.data_cadastro
            }
            compradores.append(comprador_data)

        total_compradores = len(compradores)
        print(f"Total de compradores encontrados: {total_compradores}")

        # Deleta todos os compradores
        Comprador.objects.all().delete()
        print("Todos os compradores foram deletados")

        # Reseta o contador interno do SQLite
        with connection.cursor() as cursor:
            # Primeiro, verifica se a tabela existe
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='loja_comprador'")
            if cursor.fetchone():
                # Reseta o contador interno do SQLite
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name='loja_comprador'")
                cursor.execute(
                    "INSERT INTO sqlite_sequence (name, seq) VALUES ('loja_comprador', 0)")
                print("Contador interno do SQLite foi resetado")

        # Recria os compradores com IDs sequenciais começando do 1
        for i, comprador_data in enumerate(compradores, 1):
            Comprador.objects.create(
                id=i,
                nome=comprador_data['nome'],
                email=comprador_data['email'],
                data_cadastro=comprador_data['data_cadastro']
            )
            print(f"Comprador recriado com ID {i}")

        messages.success(
            request, f'Contagem reiniciada com sucesso. {total_compradores} compradores foram recriados.')
    except Exception as e:
        messages.error(request, f'Erro ao reiniciar contagem: {str(e)}')
        print(f"Erro: {str(e)}")

    return redirect('admin:loja_comprador_changelist')


def index(request):
    produtos = Produto.objects.filter(ativo=True)
    return render(request, 'loja/index.html', {'produtos': produtos})


def confirmacao_compra(request, pedido_id):
    print(f"\n{Colors.CYAN}=== Iniciando confirmação de compra ==={Colors.END}")
    print(f"{Colors.BLUE}Pedido ID: {pedido_id}{Colors.END}")

    pedido = get_object_or_404(Pedido, pk=pedido_id)
    print(f"{Colors.GREEN}Pedido encontrado: {pedido}{Colors.END}")

    return render(request, 'loja/confirmacao_compra.html', {'pedido': pedido})


def verificar_senha(request):
    print("\n=== DEBUG: Iniciando verificar_senha ===")

    # Limpar a sessão ao acessar a página de verificação de senha
    if 'tem_acesso' in request.session:
        del request.session['tem_acesso']
    if 'nome_usuario' in request.session:
        del request.session['nome_usuario']
    if 'moedas_disponiveis' in request.session:
        del request.session['moedas_disponiveis']

    print("Sessão limpa")
    print("Sessão atual:", request.session.items())

    if request.method == 'POST':
        senha = request.POST.get('senha')
        print("Senha recebida:", senha)

        try:
            # Busca a moeda com a senha fornecida
            moeda = Moeda.objects.get(senha=senha)
            print("Moeda encontrada:", moeda)

            # Verifica se a moeda tem saldo disponível
            if moeda.moedas_disponiveis > 0:
                print("Saldo disponível:", moeda.moedas_disponiveis)

                # Atualiza as moedas disponíveis e usadas
                moeda.moedas_disponiveis -= 1
                moeda.moedas_usadas += 1
                moeda.save()
                print("Moedas atualizadas - Disponíveis:",
                      moeda.moedas_disponiveis, "Usadas:", moeda.moedas_usadas)

                # Registra o acesso no log
                LogAcesso.objects.create(
                    usuario=moeda.usuario,
                    data_acesso=timezone.now() - timezone.timedelta(hours=4),  # Ajusta para UTC-4
                    moedas_disponiveis=moeda.moedas_disponiveis,
                    moedas_usadas=moeda.moedas_usadas
                )
                print("Log de acesso criado para:", moeda.usuario)

                # Armazena o nome do usuário e moedas disponíveis na sessão
                request.session['nome_usuario'] = moeda.usuario
                request.session['moedas_disponiveis'] = moeda.moedas_disponiveis
                print("Nome do usuário armazenado na sessão:", moeda.usuario)
                print("Moedas disponíveis armazenadas na sessão:",
                      moeda.moedas_disponiveis)

                # Define a permissão de acesso
                request.session['tem_acesso'] = True
                print("Permissão de acesso definida:",
                      request.session['tem_acesso'])

                # Redireciona para a página de visualização de pagamentos
                print("Redirecionando para visualizar_pagamentos")
                return redirect('loja:visualizar_pagamentos')
            else:
                print("Sem saldo disponível:", moeda.moedas_disponiveis)
                messages.error(request, 'Você não tem moedas disponíveis.')
        except Moeda.DoesNotExist:
            print("Moeda não encontrada")
            messages.error(request, 'Senha incorreta.')

    print("=== DEBUG: Renderizando template verificar_senha.html")
    return render(request, 'loja/verificar_senha.html')


@login_required
def logs_acesso_json(request):
    print("\n=== Iniciando logs_acesso_json ===")
    print(f"Usuário autenticado: {request.user.username}")

    try:
        # Busca todos os logs
        logs = LogAcesso.objects.all().order_by('data_acesso')
        print(f"Total de logs encontrados: {logs.count()}")

        # Prepara os dados para o JSON
        data = []
        for log in logs:
            # Ajusta o horário para GMT-4
            hora_correta = log.data_acesso - timezone.timedelta(hours=4)
            data_formatada = hora_correta.strftime('%d/%m/%Y %H:%M:%S')

            print(f"\nLog encontrado:")
            print(f"Usuário: {log.usuario}")
            print(f"Data original: {log.data_acesso}")
            print(f"Data ajustada: {data_formatada}")
            print(f"Moedas disponíveis: {log.moedas_disponiveis}")
            print(f"Moedas usadas: {log.moedas_usadas}")

            data.append({
                'usuario': log.usuario,
                'data_acesso': data_formatada,
                'moedas_disponiveis': log.moedas_disponiveis,
                'moedas_usadas': log.moedas_usadas
            })

        print("\n=== Dados enviados para o gráfico ===")
        print(f"Total de registros enviados: {len(data)}")
        print("=== Fim dos logs ===\n")

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"\n=== ERRO em logs_acesso_json ===")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem de erro: {str(e)}")
        print("=== Fim dos logs de erro ===\n")
        return JsonResponse({'error': str(e)}, status=500)


def grafico_logs(request):
    return render(request, 'loja/grafico_logs.html')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def limpar_logs(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                LogAcesso.objects.all().delete()
                messages.success(
                    request, 'Todos os logs de acesso foram removidos com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao remover logs: {str(e)}')
    return redirect('admin:loja_logacesso_changelist')


def processar_pagamento(request):
    print("\n=== DEBUG: Iniciando processar_pagamento ===")
    print(f"Sessão atual: {request.session.items()}")

    if request.method == 'POST':
        print("=== DEBUG: Método POST recebido")

        # Obtém os dados do formulário
        nome_comprador = request.POST.get('nome_comprador')
        cota = request.POST.get('cota')
        produto_id = request.POST.get('produto')

        print(
            f"=== DEBUG: Dados recebidos - Nome: {nome_comprador}, Cota: {cota}, Produto ID: {produto_id}")

        try:
            # Busca o produto
            produto = Produto.objects.get(id=produto_id)
            print(f"=== DEBUG: Produto encontrado: {produto.nome}")

            # Verifica se a cota está disponível
            if int(cota) < produto.cota_inicial or int(cota) > produto.cota_final:
                print(
                    f"=== DEBUG: Cota {cota} fora do intervalo válido ({produto.cota_inicial} - {produto.cota_final})")
                messages.error(request, 'Cota inválida para este produto.')
                return redirect('loja:lista_produtos')

            # Verifica se a cota já foi vendida
            if Pedido.objects.filter(produto=produto, cota=cota).exists():
                print(f"=== DEBUG: Cota {cota} já vendida")
                messages.error(request, 'Esta cota já foi vendida.')
                return redirect('loja:lista_produtos')

            # Cria o pedido
            pedido = Pedido.objects.create(
                nome_comprador=nome_comprador,
                produto=produto,
                cota=cota,
                data=timezone.now() - timezone.timedelta(hours=4)  # Ajusta para UTC-4
            )
            print(f"=== DEBUG: Pedido criado: {pedido}")

            messages.success(request, 'Pagamento processado com sucesso!')
            print("=== DEBUG: Mensagem de sucesso adicionada")

        except Produto.DoesNotExist:
            print("=== DEBUG: Produto não encontrado")
            messages.error(request, 'Produto não encontrado.')
        except Exception as e:
            print(f"=== DEBUG: Erro ao processar pagamento: {str(e)}")
            messages.error(request, 'Erro ao processar o pagamento.')

    print("=== DEBUG: Redirecionando para lista_produtos")
    return redirect('loja:lista_produtos')
