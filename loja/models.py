from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validar_cpf, validar_telefone
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.utils import timezone


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    cota_inicial = models.IntegerField(default=1)
    cota_final = models.IntegerField()
    data_cadastro = models.DateTimeField(
        'Data de Cadastro', null=True, blank=True)

    def __str__(self):
        return self.nome

    def cotas_disponiveis(self):
        # Retorna lista de cotas já utilizadas
        cotas_usadas = Pedido.objects.filter(
            produto=self,
            status__in=['AGUARDANDO_PAGAMENTO',
                        'AGUARDANDO_CONFIRMACAO', 'PAGO']
        ).values_list('cota', flat=True)

        # Retorna lista de cotas disponíveis
        return [
            cota for cota in range(self.cota_inicial, self.cota_final + 1)
            if cota not in cotas_usadas
        ]


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento'),
        ('AGUARDANDO_CONFIRMACAO', 'Confirmação de Pagamento'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]

    id = models.AutoField(primary_key=True)
    nome_comprador = models.CharField(max_length=200)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    cota = models.IntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=25, choices=STATUS_CHOICES, default='AGUARDANDO_PAGAMENTO')
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.id} - {self.nome_comprador}'

    def visualizar_comprovante(self):
        comprovantes = self.comprovantes.all()
        if comprovantes:
            comprovante = comprovantes.first()  # Pega o primeiro comprovante
            if comprovante.arquivo.name.lower().endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" class="comprovante-link">'
                    '<div class="pdf-icon">'
                    '<div class="pdf-icon-corner"></div>'
                    '<div class="pdf-icon-text">PDF</div>'
                    '</div>'
                    '<span class="pdf-label">Visualizar PDF</span></a>',
                    comprovante.arquivo.url
                )
            elif comprovante.arquivo.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return format_html(
                    '<a href="{}" target="_blank" class="comprovante-link">'
                    '<img src="{}" class="comprovante-imagem"/></a>',
                    comprovante.arquivo.url,
                    comprovante.arquivo.url
                )
            return format_html(
                '<a href="{}" target="_blank">Visualizar arquivo</a>',
                comprovante.arquivo.url
            )
        return "Sem comprovante"
    visualizar_comprovante.short_description = "Comprovante"


class Comprovante(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='comprovantes')
    arquivo = models.FileField(upload_to='comprovantes/')
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comprovante do Pedido #{self.pedido.id}'

    def get_icon_html(self):
        ext = self.arquivo.name.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html(
                '<a href="{}" target="_blank" class="comprovante-link">'
                '<img src="{}" class="comprovante-imagem"/></a>',
                self.arquivo.url, self.arquivo.url
            )
        elif ext == 'pdf':
            return format_html(
                '<a href="{}" target="_blank" class="comprovante-link">'
                '<div class="pdf-icon">'
                '<div class="pdf-icon-corner"></div>'
                '<div class="pdf-icon-text">PDF</div>'
                '</div>'
                '<span class="pdf-label">Visualizar PDF</span></a>',
                self.arquivo.url
            )
        return format_html(
            '<a href="{}" target="_blank">Visualizar arquivo</a>',
            self.arquivo.url
        )


class ConfiguracaoPagamento(models.Model):
    qr_code = models.ImageField(upload_to='qr_codes/', verbose_name='QR Code')
    instrucoes = models.TextField(verbose_name='Instruções de Pagamento',
                                  help_text='Instruções que aparecerão na página de pagamento')
    chave_pix = models.CharField(max_length=255, verbose_name='Chave PIX')

    class Meta:
        verbose_name = 'Configuração de Pagamento'
        verbose_name_plural = 'Configurações de Pagamento'

    def __str__(self):
        return 'Configurações de Pagamento'

    def save(self, *args, **kwargs):
        # Garantir que só existe uma configuração
        if ConfiguracaoPagamento.objects.exists() and not self.pk:
            raise ValueError('Já existe uma configuração de pagamento')
        return super().save(*args, **kwargs)


class Comprador(models.Model):
    nome = models.CharField('Nome', max_length=100)
    email = models.EmailField('E-mail', blank=True, null=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    class Meta:
        verbose_name = 'Comprador'
        verbose_name_plural = 'Compradores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Moeda(models.Model):
    senha = models.CharField(max_length=50, unique=True, verbose_name="Senha")
    usuario = models.CharField(max_length=100, verbose_name="Usuário")
    moedas_disponiveis = models.IntegerField(
        default=0, verbose_name="Moedas Disponíveis")
    moedas_usadas = models.IntegerField(
        default=0, verbose_name="Moedas Usadas")
    data_uso = models.DateTimeField(
        null=True, blank=True, verbose_name="Data de Uso")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.senha}"

    class Meta:
        verbose_name = "Moeda"
        verbose_name_plural = "Moedas"
        ordering = ['-data_criacao']


class LogAcesso(models.Model):
    usuario = models.CharField(max_length=100)
    moedas_disponiveis = models.IntegerField()
    moedas_usadas = models.IntegerField()
    data_acesso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Ajusta o horário para GMT-4
        hora_correta = self.data_acesso - timezone.timedelta(hours=4)
        return f"{self.usuario} - {hora_correta.strftime('%d/%m/%Y %H:%M:%S')} (GMT-4)"

    def get_data_acesso_ajustada(self):
        # Ajusta o horário para GMT-4
        return self.data_acesso - timezone.timedelta(hours=4)

    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-data_acesso']
