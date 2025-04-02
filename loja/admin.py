from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from .models import Produto, Pedido, ConfiguracaoPagamento, Comprador, Comprovante
import logging
from django.contrib import messages

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Removendo registros anteriores (caso existam)
try:
    admin.site.unregister(Produto)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Pedido)
except admin.sites.NotRegistered:
    pass

# Registrando novamente


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'data_cadastro')
    search_fields = ('nome',)
    list_filter = ('data_cadastro',)
    date_hierarchy = 'data_cadastro'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'preco', 'estoque', 'data_cadastro')
        }),
        ('Configurações de Cotas', {
            'fields': ('cota_inicial', 'cota_final')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'imagem')
        }),
    )


class ComprovanteInline(admin.TabularInline):
    model = Comprovante
    extra = 0
    readonly_fields = ['visualizar_arquivo', 'data_envio']
    fields = ['arquivo', 'data_envio', 'visualizar_arquivo']

    class Media:
        css = {
            'all': ('admin/css/comprovantes.css',)
        }

    def visualizar_arquivo(self, obj):
        if obj.arquivo:
            return obj.get_icon_html()
        return "Sem arquivo"
    visualizar_arquivo.short_description = "Visualizar"


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_comprador', 'produto',
                    'cota', 'valor', 'status', 'data', 'icone_comprovante')
    list_filter = ('status', 'data')
    search_fields = ('nome_comprador', 'produto__nome')
    date_hierarchy = 'data'
    list_editable = ('status',)
    inlines = [ComprovanteInline]

    def icone_comprovante(self, obj):
        comprovantes = obj.comprovantes.all()
        if comprovantes:
            return format_html(
                '<a href="{}" target="_blank" style="color: #447e9b; text-decoration: none;">Comprovante ({})</a>',
                comprovantes.first().arquivo.url,
                comprovantes.count()
            )
        return format_html('<span style="color: #999;">Sem comprovante</span>')

    icone_comprovante.short_description = 'Comprovante'

    class Media:
        css = {
            'all': ('admin/css/pedidos.css',)
        }

    def nome_comprador_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.id, obj.nome_comprador)
    nome_comprador_link.short_description = 'Nome do Comprador'

    def visualizar_comprovante(self, obj):
        comprovantes = obj.comprovantes.all()
        if comprovantes:
            return format_html('<a href="{}">Ver Comprovantes ({})</a>', obj.id, comprovantes.count())
        return "Sem comprovantes"
    visualizar_comprovante.short_description = 'Comprovantes'

    fieldsets = (
        ('Informações do Comprador', {
            'fields': ('nome_comprador', 'produto', 'cota')
        }),
        ('Informações do Pagamento', {
            'fields': ('valor', 'status')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('produto')


@admin.register(ConfiguracaoPagamento)
class ConfiguracaoPagamentoAdmin(admin.ModelAdmin):
    list_display = ['chave_pix']

    def has_add_permission(self, request):
        # Impedir criação de múltiplas configurações
        return not ConfiguracaoPagamento.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Impedir exclusão da configuração
        return False


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'data_cadastro')
    search_fields = ('nome', 'email')
    list_filter = ('data_cadastro',)
    date_hierarchy = 'data_cadastro'
    ordering = ('id',)


@admin.register(Comprovante)
class ComprovanteAdmin(admin.ModelAdmin):
    list_display = ('pedido_link', 'data_envio', 'visualizar_arquivo')
    list_filter = ('data_envio',)
    search_fields = ('pedido__nome_comprador', 'pedido__produto__nome')
    date_hierarchy = 'data_envio'

    class Media:
        css = {
            'all': ('admin/css/comprovantes.css',)
        }

    def pedido_link(self, obj):
        url = reverse('admin:loja_pedido_change', args=[obj.pedido.id])
        return format_html(
            '<a href="{}">{} - {}</a>',
            url,
            obj.pedido.nome_comprador,
            obj.pedido.cota
        )
    pedido_link.short_description = 'Pedido (Comprador - Cota)'

    def visualizar_arquivo(self, obj):
        if not obj.arquivo:
            return "Sem arquivo"

        # Verifica se é PDF
        ext = obj.arquivo.name.split('.')[-1].lower()
        if ext == 'pdf':
            return format_html(
                '<a href="{}" target="_blank" class="comprovante-link">'
                '<div class="pdf-icon">'
                '<div class="pdf-icon-corner"></div>'
                '<div class="pdf-icon-text">PDF</div>'
                '</div>'
                '<span class="pdf-label">Visualizar PDF</span></a>',
                obj.arquivo.url
            )
        # Se for imagem
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html(
                '<a href="{}" target="_blank" class="comprovante-link">'
                '<img src="{}" class="comprovante-imagem"/></a>',
                obj.arquivo.url,
                obj.arquivo.url
            )
        # Para outros tipos de arquivo
        return format_html(
            '<a href="{}" target="_blank">Visualizar arquivo</a>',
            obj.arquivo.url
        )
    visualizar_arquivo.short_description = "Comprovante"
