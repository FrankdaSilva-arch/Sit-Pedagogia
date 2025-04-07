from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from .models import Produto, Pedido, ConfiguracaoPagamento, Comprador, Comprovante, Moeda, LogAcesso
import logging
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

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

try:
    admin.site.unregister(Comprovante)
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

    def has_module_permission(self, request):
        # Restringir acesso apenas para superusuários
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        # Restringir visualização apenas para superusuários
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Restringir edição apenas para superusuários
        return request.user.is_superuser


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'data_cadastro')
    search_fields = ('nome', 'email')
    list_filter = ('data_cadastro',)
    date_hierarchy = 'data_cadastro'
    ordering = ('id',)


@admin.register(Comprovante)
class ComprovanteAdmin(admin.ModelAdmin):
    list_display = ('pedido_link', 'nome_comprador', 'produto',
                    'cota', 'valor', 'status', 'data_envio', 'visualizar_arquivo')
    list_filter = ('data_envio', 'pedido__produto', 'pedido__status')
    search_fields = ('pedido__nome_comprador',
                     'pedido__produto__nome', 'pedido__cota')
    date_hierarchy = 'data_envio'
    readonly_fields = ('pedido', 'data_envio', 'visualizar_arquivo')
    ordering = ('-data_envio',)

    class Media:
        css = {
            'all': ('admin/css/comprovantes.css',)
        }

    def pedido_link(self, obj):
        url = reverse('admin:loja_pedido_change', args=[obj.pedido.id])
        return format_html('<a href="{}">{}</a>', url, obj.pedido)
    pedido_link.short_description = 'Pedido'

    def nome_comprador(self, obj):
        return obj.pedido.nome_comprador
    nome_comprador.short_description = 'Comprador'

    def produto(self, obj):
        return obj.pedido.produto
    produto.short_description = 'Produto'

    def cota(self, obj):
        return obj.pedido.cota
    cota.short_description = 'Cota'

    def valor(self, obj):
        return f'R$ {obj.pedido.valor}'
    valor.short_description = 'Valor'

    def status(self, obj):
        return obj.pedido.get_status_display()
    status.short_description = 'Status'

    def visualizar_arquivo(self, obj):
        if obj.arquivo:
            return obj.get_icon_html()
        return "Sem arquivo"
    visualizar_arquivo.short_description = "Visualizar"


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'moedas_disponiveis',
                    'moedas_usadas', 'data_acesso')
    list_filter = ('data_acesso',)
    search_fields = ('usuario',)
    date_hierarchy = 'data_acesso'
    ordering = ('-data_acesso',)
    change_list_template = 'admin/loja/logacesso/change_list.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('limpar/', self.admin_site.admin_view(self.limpar_logs),
                 name='limpar_logs'),
            path('grafico/', self.admin_site.admin_view(self.grafico_logs),
                 name='grafico_logs'),
        ]
        return custom_urls + urls

    def limpar_logs(self, request):
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    LogAcesso.objects.all().delete()
                    messages.success(
                        request, 'Todos os logs de acesso foram removidos com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao remover logs: {str(e)}')
        return redirect('admin:loja_logacesso_changelist')

    def grafico_logs(self, request):
        logs = LogAcesso.objects.all().order_by('data_acesso')
        logs_data = []
        for log in logs:
            logs_data.append({
                'usuario': log.usuario,
                'moedas_disponiveis': log.moedas_disponiveis,
                'moedas_usadas': log.moedas_usadas,
                'data_acesso': log.data_acesso.isoformat()
            })
        context = {
            'logs': logs_data,
            'title': 'Gráfico de Logs de Acesso',
        }
        return render(request, 'admin/loja/logacesso/grafico.html', context)

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['title'] = 'Logs de Acesso'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Moeda)
class MoedaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'senha', 'moedas_disponiveis',
                    'moedas_usadas', 'data_uso', 'data_criacao')
    search_fields = ('usuario', 'senha')
    list_filter = ('data_criacao', 'data_uso')
    readonly_fields = ('data_criacao', 'data_uso')
    change_list_template = 'admin/loja/moeda/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('logs/', self.admin_site.admin_view(self.logs_view),
                 name='moeda-logs'),
        ]
        return custom_urls + urls

    def logs_view(self, request):
        logs = LogAcesso.objects.all()[:50]  # Limita a 50 logs mais recentes
        context = {
            'logs': logs,
            'title': 'Logs de Acesso',
        }
        return render(request, 'admin/loja/moeda/logs.html', context)
