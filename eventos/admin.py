from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Evento, ImagemEvento, Curso, ConvidadoEspecial, PublicoGeral, CadastroDosCursos, SenhaDeControle, LimiteCursosID, LimitePublicoGeralID, Certificacao
from django.db import connection
from django.views.generic import CreateView
from django.urls import reverse, path
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django import forms
from django.shortcuts import render, redirect
from .widgets import CoordenadorAutocompleteWidget

FONTS_DIR = '/home/FRANKPED2026/Sit-Pedagogia/static/fonts/'

FONTE_MAP = {
    'Arial':                FONTS_DIR + 'arial.ttf',
    'Arial Bold':           FONTS_DIR + 'arialbd.ttf',
    'Arial Italico':        FONTS_DIR + 'ariali.ttf',
    'Arial Bold Italico':   FONTS_DIR + 'arialbi.ttf',
    'Times New Roman':      FONTS_DIR + 'times.ttf',
    'Times New Roman Bold': FONTS_DIR + 'timesbd.ttf',
    'DejaVu Sans':          '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'DejaVu Sans Bold':     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'DejaVu Serif':         '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    'DejaVu Serif Bold':    '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
}


class ImagemEventoInline(admin.TabularInline):
    model = ImagemEvento
    extra = 1
    max_num = 10
    fields = ('imagem', 'legenda', 'ordem')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso_responsavel', 'tema', 'data', 'local')
    search_fields = ('titulo', 'curso_responsavel', 'tema', 'descricao', 'local')
    list_filter = ('curso_responsavel', 'data', 'local')
    fieldsets = [
        (None, {
            'fields': ('curso_responsavel', 'titulo', 'tema', 'data', 'local', 'descricao'),
            'description': 'Preencha todos os campos obrigatorios'
        }),
    ]
    inlines = [ImagemEventoInline]

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form._errors.update(e.message_dict)


def resetar_cadastros(modeladmin, request, queryset):
    from eventos.models import Curso
    Curso.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='eventos_curso';")
    modeladmin.message_user(request, "Todos os cadastros foram apagados e o ID reiniciado para 1.")

resetar_cadastros.short_description = "Resetar cadastros (apagar tudo e reiniciar ID)"


def resetar_convidados(modeladmin, request, queryset):
    from eventos.models import ConvidadoEspecial
    ConvidadoEspecial.objects.all().delete()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='eventos_convidadoespecial';")
    modeladmin.message_user(request, "Todos os convidados foram apagados e o ID reiniciado para 1.")

resetar_convidados.short_description = "Resetar convidados (apagar tudo e reiniciar ID)"


def resetar_publico_geral(modeladmin, request, queryset):
    from eventos.models import PublicoGeral
    PublicoGeral.objects.all().delete()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='eventos_publicogeral';")
    modeladmin.message_user(request, "Todos os registros de Publico Geral foram apagados e o ID reiniciado para 1.")

resetar_publico_geral.short_description = "Resetar Publico Geral (apagar tudo e reiniciar ID)"


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_curso', 'nome_completo', 'idade', 'matricula', 'email', 'ocupacao', 'coordenador')
    search_fields = ('nome_curso', 'nome_completo', 'matricula', 'email', 'coordenador')
    list_filter = ('coordenador', 'ocupacao', 'nome_curso')
    actions = [resetar_cadastros]
    fields = ('nome_curso', 'nome_completo', 'idade', 'matricula', 'email', 'ocupacao', 'coordenador')


@admin.register(ConvidadoEspecial)
class ConvidadoEspecialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'idade', 'formacao', 'ocupacao', 'email', 'recebeu_convite_de', 'senha_especial')
    search_fields = ('nome_completo', 'formacao', 'ocupacao', 'email', 'recebeu_convite_de')
    list_filter = ('formacao', 'ocupacao', 'email')
    actions = [resetar_convidados]


@admin.register(PublicoGeral)
class PublicoGeralAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'idade', 'ocupacao', 'email')
    search_fields = ('nome_completo', 'ocupacao', 'email')
    list_filter = ('ocupacao', 'email')
    actions = [resetar_publico_geral]


def resetar_cadastrodoscursos(modeladmin, request, queryset):
    from eventos.models import CadastroDosCursos
    from django.db import connection
    CadastroDosCursos.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='eventos_cadastrodoscursos';")
    modeladmin.message_user(request, "Todos os cadastros foram apagados e o ID reiniciado para 1.")

resetar_cadastrodoscursos.short_description = "Resetar Cadastro dos Cursos (apagar tudo e reiniciar ID)"


class CadastroDosCursosAdminForm(forms.ModelForm):
    class Meta:
        model = CadastroDosCursos
        fields = '__all__'
        widgets = {
            'coordenador': CoordenadorAutocompleteWidget,
        }


@admin.register(CadastroDosCursos)
class CadastroDosCursosAdmin(admin.ModelAdmin):
    form = CadastroDosCursosAdminForm
    list_display = ('id', 'nome', 'modalidade', 'coordenador')
    search_fields = ('nome', 'modalidade')
    fields = ('nome', 'modalidade', 'coordenador')
    actions = [resetar_cadastrodoscursos]


@admin.register(SenhaDeControle)
class SenhaDeControleAdmin(admin.ModelAdmin):
    list_display = ('senha', 'vaga', 'observacao')

    def changelist_view(self, request, extra_context=None):
        total_disponivel = self.model.objects.filter(vaga='disponivel').count()
        if extra_context is None:
            extra_context = {}
        extra_context['total_vagas_disponivel'] = total_disponivel
        return super().changelist_view(request, extra_context=extra_context)


class InscricaoCursoView(CreateView):
    model = Curso
    template_name = 'eventos/inscricao_curso.html'
    fields = ['nome_curso', 'nome_completo', 'idade', 'matricula', 'email', 'ocupacao', 'coordenador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nomes_cursos'] = CadastroDosCursos.objects.values_list('nome', flat=True)
        return context

    def get_success_url(self):
        return reverse('eventos:lista_eventos')

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@receiver(post_delete, sender=ConvidadoEspecial)
def liberar_vaga_senha(sender, instance, **kwargs):
    senha = instance.senha_especial
    if not ConvidadoEspecial.objects.filter(senha_especial__iexact=senha).exists():
        try:
            senha_controle = SenhaDeControle.objects.get(senha__iexact=senha)
            senha_controle.vaga = 'disponivel'
            senha_controle.save()
        except SenhaDeControle.DoesNotExist:
            pass


@admin.register(LimiteCursosID)
class LimiteCursosIDAdmin(admin.ModelAdmin):
    list_display = ('valor',)

    def changelist_view(self, request, extra_context=None):
        from .models import Curso
        limite = LimiteCursosID.objects.first()
        total_cursos = Curso.objects.count()
        vagas_disponiveis = (limite.valor - total_cursos) if limite else 0
        if extra_context is None:
            extra_context = {}
        extra_context['vagas_disponiveis'] = vagas_disponiveis
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(LimitePublicoGeralID)
class LimitePublicoGeralIDAdmin(admin.ModelAdmin):
    list_display = ('valor',)

    def changelist_view(self, request, extra_context=None):
        from .models import PublicoGeral
        limite = LimitePublicoGeralID.objects.first()
        total_publico = PublicoGeral.objects.count()
        vagas_disponiveis = (limite.valor - total_publico) if limite else 0
        if extra_context is None:
            extra_context = {}
        extra_context['vagas_disponiveis'] = vagas_disponiveis
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Certificacao)
class CertificacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'grupo', 'evento')
    fields = (
        'nome', 'evento', 'grupo', 'imagem_fundo',
        'nome_x', 'nome_y', 'nome_largura', 'nome_fonte', 'nome_tamanho', 'nome_cor', 'nome_alinhamento',
        'matricula_x', 'matricula_y', 'matricula_largura', 'matricula_fonte', 'matricula_tamanho', 'matricula_cor', 'matricula_alinhamento',
        'conclusao_x', 'conclusao_y', 'conclusao_largura', 'conclusao_fonte', 'conclusao_tamanho', 'conclusao_cor', 'conclusao_alinhamento', 'conclusao_texto',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:cert_id>/gerar/', self.admin_site.admin_view(self.gerar_certificados_view), name='gerar_certificados'),
            path('<int:cert_id>/editor/', self.admin_site.admin_view(self.editor_visual_view), name='editor_certificado'),
            path('<int:cert_id>/salvar-posicoes/', self.admin_site.admin_view(self.salvar_posicoes_view), name='salvar_posicoes_certificado'),
        ]
        return custom_urls + urls

    def editor_visual_view(self, request, cert_id):
        cert = Certificacao.objects.get(pk=cert_id)
        return render(request, 'admin/eventos/editor_certificado.html', {'cert': cert})

    def salvar_posicoes_view(self, request, cert_id):
        import json
        from django.http import JsonResponse
        if request.method == 'POST':
            cert = Certificacao.objects.get(pk=cert_id)
            data = json.loads(request.body)
            cert.nome_x = data.get('nome_x', cert.nome_x)
            cert.nome_y = data.get('nome_y', cert.nome_y)
            cert.nome_largura = data.get('nome_largura', cert.nome_largura)
            cert.nome_fonte = data.get('nome_fonte', cert.nome_fonte)
            cert.nome_tamanho = data.get('nome_tamanho', cert.nome_tamanho)
            cert.nome_cor = data.get('nome_cor', cert.nome_cor)
            cert.nome_alinhamento = data.get('nome_alinhamento', cert.nome_alinhamento)
            cert.matricula_x = data.get('matricula_x', cert.matricula_x)
            cert.matricula_y = data.get('matricula_y', cert.matricula_y)
            cert.matricula_largura = data.get('matricula_largura', cert.matricula_largura)
            cert.matricula_fonte = data.get('matricula_fonte', cert.matricula_fonte)
            cert.matricula_tamanho = data.get('matricula_tamanho', cert.matricula_tamanho)
            cert.matricula_cor = data.get('matricula_cor', cert.matricula_cor)
            cert.matricula_alinhamento = data.get('matricula_alinhamento', cert.matricula_alinhamento)
            cert.conclusao_x = data.get('conclusao_x', cert.conclusao_x)
            cert.conclusao_y = data.get('conclusao_y', cert.conclusao_y)
            cert.conclusao_largura = data.get('conclusao_largura', cert.conclusao_largura)
            cert.conclusao_fonte = data.get('conclusao_fonte', cert.conclusao_fonte)
            cert.conclusao_tamanho = data.get('conclusao_tamanho', cert.conclusao_tamanho)
            cert.conclusao_cor = data.get('conclusao_cor', cert.conclusao_cor)
            cert.conclusao_alinhamento = data.get('conclusao_alinhamento', cert.conclusao_alinhamento)
            cert.conclusao_texto = data.get('conclusao_texto', cert.conclusao_texto)
            cert.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'}, status=400)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['gerar_url_jpg'] = reverse('admin:gerar_certificados', args=[object_id]) + '?formato=jpg'
        extra_context['gerar_url_pdf'] = reverse('admin:gerar_certificados', args=[object_id]) + '?formato=pdf'
        extra_context['editor_url'] = reverse('admin:editor_certificado', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def gerar_certificados_view(self, request, cert_id):
        import zipfile
        import io
        from PIL import Image, ImageDraw, ImageFont
        from reportlab.lib.units import mm
        from reportlab.lib.pagesizes import landscape
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.utils import ImageReader
        from django.http import HttpResponse

        cert = Certificacao.objects.get(pk=cert_id)
        formato = request.GET.get('formato', 'jpg')

        if cert.grupo == 'cursos':
            inscritos = list(Curso.objects.values('nome_completo', 'matricula'))
        elif cert.grupo == 'convidados':
            inscritos = [{'nome_completo': c.nome_completo, 'matricula': ''} for c in ConvidadoEspecial.objects.all()]
        else:
            inscritos = [{'nome_completo': p.nome_completo, 'matricula': ''} for p in PublicoGeral.objects.all()]

        def get_font(fonte_nome, tamanho):
            try:
                font_path = FONTE_MAP.get(fonte_nome)
                if font_path:
                    return ImageFont.truetype(font_path, tamanho)
                return ImageFont.truetype(FONTE_MAP['Arial'], tamanho)
            except Exception:
                return ImageFont.load_default()

        def desenhar_texto_alinhado(draw, texto, x, y, fonte, cor, largura_max, alinhamento='left'):
            linhas_originais = texto.split('\n')
            todas_linhas = []
            for linha in linhas_originais:
                palavras = linha.split(' ')
                linha_atual = ''
                for palavra in palavras:
                    teste = (linha_atual + ' ' + palavra).strip()
                    bbox = draw.textbbox((0, 0), teste, font=fonte)
                    if (bbox[2] - bbox[0]) <= largura_max:
                        linha_atual = teste
                    else:
                        if linha_atual:
                            todas_linhas.append(linha_atual)
                        linha_atual = palavra
                if linha_atual:
                    todas_linhas.append(linha_atual)

            y_atual = y
            for i, linha in enumerate(todas_linhas):
                bbox = draw.textbbox((0, 0), linha, font=fonte)
                largura_linha = bbox[2] - bbox[0]
                altura_linha = bbox[3] - bbox[1]
                eh_ultima = (i == len(todas_linhas) - 1)

                if alinhamento == 'center':
                    x_draw = x + (largura_max - largura_linha) // 2
                elif alinhamento == 'right':
                    x_draw = x + largura_max - largura_linha
                elif alinhamento == 'justify' and not eh_ultima:
                    palavras_linha = linha.split(' ')
                    if len(palavras_linha) > 1:
                        bbox_sem = draw.textbbox((0, 0), linha.replace(' ', ''), font=fonte)
                        largura_texto = bbox_sem[2] - bbox_sem[0]
                        espaco_total = largura_max - largura_texto
                        espaco_por = espaco_total // (len(palavras_linha) - 1)
                        x_pos = x
                        for palavra in palavras_linha:
                            draw.text((x_pos, y_atual), palavra, font=fonte, fill=cor)
                            bp = draw.textbbox((0, 0), palavra, font=fonte)
                            x_pos += (bp[2] - bp[0]) + espaco_por
                        y_atual += altura_linha + 4
                        continue
                    x_draw = x
                else:
                    x_draw = x

                draw.text((x_draw, y_atual), linha, font=fonte, fill=cor)
                y_atual += altura_linha + 4

        def gerar_imagem(inscrito):
            img = Image.open(cert.imagem_fundo.path).convert('RGBA')
            draw = ImageDraw.Draw(img)
            escala = img.width / 900.0 if img.width > 900 else 1.0

            nome_x = int(cert.nome_x * escala)
            nome_y = int(cert.nome_y * escala)
            nome_tam = int(cert.nome_tamanho * escala)
            nome_larg = int(cert.nome_largura * escala)

            matricula_x = int(cert.matricula_x * escala)
            matricula_y = int(cert.matricula_y * escala)
            matricula_tam = int(cert.matricula_tamanho * escala)
            matricula_larg = int(cert.matricula_largura * escala)

            conclusao_x = int(cert.conclusao_x * escala)
            conclusao_y = int(cert.conclusao_y * escala)
            conclusao_tam = int(cert.conclusao_tamanho * escala)
            conclusao_larg = int(cert.conclusao_largura * escala)

            font_nome = get_font(cert.nome_fonte, nome_tam)
            desenhar_texto_alinhado(draw, inscrito['nome_completo'], nome_x, nome_y, font_nome, cert.nome_cor, nome_larg, getattr(cert, 'nome_alinhamento', 'left'))

            if inscrito.get('matricula'):
                font_mat = get_font(cert.matricula_fonte, matricula_tam)
                texto_matricula = u'Matr\u00edcula: ' + str(inscrito['matricula'])
                desenhar_texto_alinhado(draw, texto_matricula, matricula_x, matricula_y, font_mat, cert.matricula_cor, matricula_larg, getattr(cert, 'matricula_alinhamento', 'left'))

            font_conc = get_font(cert.conclusao_fonte, conclusao_tam)
            desenhar_texto_alinhado(draw, cert.conclusao_texto, conclusao_x, conclusao_y, font_conc, cert.conclusao_cor, conclusao_larg, getattr(cert, 'conclusao_alinhamento', 'left'))

            return img.convert('RGB')

        def imagem_para_pdf(img):
            img_width, img_height = img.size
            pdf_buffer = io.BytesIO()
            page_size = landscape((img_width * mm / 3.7795, img_height * mm / 3.7795))
            c = pdf_canvas.Canvas(pdf_buffer, pagesize=page_size)
            img_temp = io.BytesIO()
            img.save(img_temp, format='JPEG', quality=95)
            img_temp.seek(0)
            c.drawImage(ImageReader(img_temp), 0, 0, width=page_size[0], height=page_size[1])
            c.save()
            pdf_buffer.seek(0)
            return pdf_buffer

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for inscrito in inscritos:
                img = gerar_imagem(inscrito)
                nome_base = inscrito['nome_completo'].replace(' ', '_')

                if formato == 'pdf':
                    pdf_bytes = imagem_para_pdf(img)
                    zip_file.writestr('certificado_{}.pdf'.format(nome_base), pdf_bytes.read())
                else:
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='JPEG', quality=95)
                    img_buffer.seek(0)
                    zip_file.writestr('certificado_{}.jpg'.format(nome_base), img_buffer.read())

        zip_buffer.seek(0)
        nome_zip = 'certificados_{}_{}.zip'.format(cert.grupo, formato)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(nome_zip)
        return response
