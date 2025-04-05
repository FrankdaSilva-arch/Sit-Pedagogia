from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Produto, Pedido, Comprovante, ConfiguracaoPagamento, Comprador
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
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST' and request.FILES.get('comprovante'):
        Comprovante.objects.create(
            pedido=pedido,
            arquivo=request.FILES['comprovante']
        )
        # Atualiza o status do pedido para Confirmação de Pagamento
        pedido.status = 'AGUARDANDO_CONFIRMACAO'
        pedido.save()
        messages.success(request, 'Comprovante enviado com sucesso!')
        return render(request, 'loja/confirmacao_compra.html', {'pedido': pedido})
    return redirect('loja:pagamento', produto_id=pedido.produto.id, pedido_id=pedido_id)


def visualizar_pagamentos(request):
    pedidos = Pedido.objects.all().order_by('-data')
    configuracao = ConfiguracaoPagamento.objects.first()
    return render(request, 'loja/visualizar_pagamentos.html', {
        'pedidos': pedidos,
        'configuracao': configuracao
    })


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
