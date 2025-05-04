from django.urls import path
from .views import (
    ListaEventosView, DetalheEventoView, InscricaoCursoView,
    autocomplete_cursos, dados_curso, autocomplete_convidados,
    inscricao_convidado, dados_convidado, autocomplete_coordenadores,
    inscricao_publico
)
from django.http import HttpResponse, JsonResponse

# Views de exemplo só para não dar erro


app_name = 'eventos'

urlpatterns = [
    path('', ListaEventosView.as_view(), name='lista_eventos'),
    path('<int:pk>/', DetalheEventoView.as_view(), name='detalhe_evento'),
    path('<int:evento_id>/inscricao/curso/',
         InscricaoCursoView.as_view(), name='inscricao_curso'),
    path('<int:evento_id>/inscricao/convidado/',
         inscricao_convidado, name='inscricao_convidado'),
    path('<int:evento_id>/inscricao/publico/',
         inscricao_publico, name='inscricao_publico'),
    path('autocomplete/cursos/', autocomplete_cursos, name='autocomplete_cursos'),
    path('dados_curso/', dados_curso, name='dados_curso'),
    path('autocomplete/convidados/', autocomplete_convidados,
         name='autocomplete_convidados'),
    path('dados_convidado/', dados_convidado, name='dados_convidado'),
    path('autocomplete/coordenadores/', autocomplete_coordenadores,
         name='autocomplete_coordenadores'),
]


def dados_convidado(request):
    nome_convidado = request.GET.get('nome_convidado')
    try:
        convidado = ConvidadoEspecial.objects.get(nome_completo=nome_convidado)
        data = {
            'idade': convidado.idade,
            'formacao': convidado.formacao,
            'ocupacao': convidado.ocupacao,
            'recebeu_convite_de': convidado.recebeu_convite_de,
            'senha_especial': convidado.senha_especial,
            'email': convidado.email,
        }
        return JsonResponse(data)
    except ConvidadoEspecial.DoesNotExist:
        return JsonResponse({}, status=404)


def autocomplete_convidados(request):
    termo = request.GET.get('q', '')
    convidados = ConvidadoEspecial.objects.filter(
        nome_completo__icontains=termo)
    sugestoes = [f"{convidado.nome_completo}" for convidado in convidados]
    return JsonResponse(sugestoes, safe=False)
