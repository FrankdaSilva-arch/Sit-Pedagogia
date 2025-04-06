from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

print("CARREGANDO URLS DA LOJA")

app_name = 'loja'

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('produto/<int:produto_id>/',
         views.detalhe_produto, name='detalhe_produto'),
    path('produto/<int:produto_id>/confirmar-compra/',
         views.confirmar_compra, name='confirmar_compra'),
    path('produto/<int:produto_id>/verificar-cota/<int:cota>/',
         views.verificar_cota, name='verificar_cota'),
    path('produto/<int:produto_id>/pagamento/<int:pedido_id>/',
         views.pagamento, name='pagamento'),
    path('pedido/<int:pedido_id>/enviar-comprovante/',
         views.enviar_comprovante, name='enviar_comprovante'),
    path('pedido/<int:pedido_id>/confirmacao/',
         views.confirmacao_compra, name='confirmacao_compra'),
    path('visualizar-pagamentos/', views.visualizar_pagamentos,
         name='visualizar_pagamentos'),
    path('verificar-senha/', views.verificar_senha, name='verificar_senha'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar-ao-carrinho/<int:produto_id>/',
         views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover-do-carrinho/<int:produto_id>/',
         views.remover_do_carrinho, name='remover_do_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('iniciar-contagem/', views.iniciar_contagem, name='iniciar_contagem'),
    path('iniciar-contagem-compradores/', views.iniciar_contagem_compradores,
         name='iniciar_contagem_compradores'),
    path('buscar-compradores/', views.buscar_compradores,
         name='buscar_compradores'),
    path('registrar-comprador-selecionado/', views.registrar_comprador_selecionado,
         name='registrar_comprador_selecionado'),
    path('buscar-pedido/', views.buscar_pedido, name='buscar_pedido'),
    path('logs-acesso-json/', views.logs_acesso_json, name='logs_acesso_json'),
    path('grafico-logs/', views.grafico_logs, name='grafico_logs'),
    path('admin/loja/logacesso/limpar/', views.limpar_logs, name='limpar_logs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
