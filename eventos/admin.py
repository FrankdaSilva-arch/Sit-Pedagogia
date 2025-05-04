from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Evento, ImagemEvento, Curso, ConvidadoEspecial, PublicoGeral, CadastroDosCursos, SenhaDeControle, LimiteCursosID, LimitePublicoGeralID
from django.db import connection
from django.views.generic import CreateView
from django.urls import reverse, path
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django import forms
from django.shortcuts import render, redirect
from .widgets import CoordenadorAutocompleteWidget


class ImagemEventoInline(admin.TabularInline):
    model = ImagemEvento
    extra = 1
    max_num = 10
    fields = ('imagem', 'legenda', 'ordem')


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso_responsavel', 'tema', 'data', 'local')
    search_fields = ('titulo', 'curso_responsavel',
                     'tema', 'descricao', 'local')
    list_filter = ('curso_responsavel', 'data', 'local')

    fieldsets = [
        (None, {
            'fields': ('curso_responsavel', 'titulo', 'tema', 'data', 'local', 'descricao'),
            'description': 'Preencha todos os campos obrigatórios'
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
    # Apaga todos os registros
    from eventos.models import Curso
    Curso.objects.all().delete()
    # Reseta o autoincremento do ID (para SQLite)
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name='eventos_curso';")
    modeladmin.message_user(
        request, "Todos os cadastros foram apagados e o ID reiniciado para 1.")


resetar_cadastros.short_description = "Resetar cadastros (apagar tudo e reiniciar ID)"


def resetar_convidados(modeladmin, request, queryset):
    from eventos.models import ConvidadoEspecial
    ConvidadoEspecial.objects.all().delete()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name='eventos_convidadoespecial';")
    modeladmin.message_user(
        request, "Todos os convidados foram apagados e o ID reiniciado para 1.")


resetar_convidados.short_description = "Resetar convidados (apagar tudo e reiniciar ID)"


def resetar_publico_geral(modeladmin, request, queryset):
    from eventos.models import PublicoGeral
    PublicoGeral.objects.all().delete()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name='eventos_publicogeral';")
    modeladmin.message_user(
        request, "Todos os registros de Público Geral foram apagados e o ID reiniciado para 1.")


resetar_publico_geral.short_description = "Resetar Público Geral (apagar tudo e reiniciar ID)"


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_curso', 'nome_completo', 'idade',
                    'matricula', 'email', 'ocupacao', 'coordenador')
    search_fields = ('nome_curso', 'nome_completo',
                     'matricula', 'email', 'coordenador')
    list_filter = ('coordenador', 'ocupacao', 'nome_curso')
    actions = [resetar_cadastros]
    fields = ('nome_curso', 'nome_completo', 'idade',
              'matricula', 'email', 'ocupacao', 'coordenador')


@admin.register(ConvidadoEspecial)
class ConvidadoEspecialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'idade', 'formacao',
                    'ocupacao', 'email', 'recebeu_convite_de', 'senha_especial')
    search_fields = ('nome_completo', 'formacao', 'ocupacao',
                     'email', 'recebeu_convite_de')
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
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name='eventos_cadastrodoscursos';")
    modeladmin.message_user(
        request, "Todos os cadastros foram apagados e o ID reiniciado para 1.")


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
    fields = ['nome_curso', 'nome_completo', 'idade',
              'matricula', 'email', 'ocupacao', 'coordenador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nomes_cursos'] = CadastroDosCursos.objects.values_list(
            'nome', flat=True)
        return context

    def get_success_url(self):
        return reverse('eventos:lista_eventos')

    def form_valid(self, form):
        print(">>> form_valid chamado")
        print("Dados do formulário:", form.cleaned_data)
        response = super().form_valid(form)
        print("Objeto salvo:", self.object)
        return response

    def form_invalid(self, form):
        print(">>> form_invalid chamado")
        print("Erros do formulário:", form.errors)
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
        from .models import Curso  # Importa aqui para evitar import circular
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
        from .models import PublicoGeral  # Importa aqui para evitar import circular
        limite = LimitePublicoGeralID.objects.first()
        total_publico = PublicoGeral.objects.count()
        vagas_disponiveis = (limite.valor - total_publico) if limite else 0
        if extra_context is None:
            extra_context = {}
        extra_context['vagas_disponiveis'] = vagas_disponiveis
        return super().changelist_view(request, extra_context=extra_context)
