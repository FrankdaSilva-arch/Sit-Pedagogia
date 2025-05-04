from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import Evento, Curso, CadastroDosCursos, ConvidadoEspecial, SenhaDeControle, LimiteCursosID, LimitePublicoGeralID, PublicoGeral
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import InscricaoCursoForm, InscricaoConvidadoForm, InscricaoPublicoGeralForm

class ListaEventosView(ListView):
    model = Evento
    template_name = 'eventos/lista_eventos.html'
    context_object_name = 'eventos'
    ordering = ['-data']  # Ordena do mais recente para o mais antigo

class DetalheEventoView(DetailView):
    model = Evento
    template_name = 'eventos/detalhe_evento.html'
    context_object_name = 'evento'

class InscricaoCursoView(CreateView):
    model = Curso
    form_class = InscricaoCursoForm
    template_name = 'eventos/inscricao_curso.html'

    def get(self, request, *args, **kwargs):
        # Se for uma requisição de autocomplete, retorna JSON
        if request.GET.get('autocomplete') == '1':
            termo = request.GET.get('q', '')
            print(f"[AUTOCOMPLETE] Usuário digitou: {termo}")
            cursos = CadastroDosCursos.objects.filter(nome__icontains=termo).values_list('nome', flat=True)
            return JsonResponse(list(cursos), safe=False)
        # Senão, segue o fluxo normal
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evento_id'] = self.kwargs.get('evento_id')
        nomes_cursos = CadastroDosCursos.objects.values_list('nome', flat=True)
        context['nomes_cursos'] = nomes_cursos
        # Pega o limite cadastrado (se não existir, define como None)
        limite = LimiteCursosID.objects.first()
        limite_valor = limite.valor if limite else None
        # Conta quantos cursos já existem
        total_inscritos = Curso.objects.count()
        # Passa para o template
        context['limite_cursos'] = limite_valor
        context['total_inscritos'] = total_inscritos
        context['esgotado'] = limite_valor is not None and total_inscritos >= limite_valor
        context['vagas_disponiveis'] = (limite_valor - total_inscritos) if limite_valor is not None else None
        return context

    def get_success_url(self):
        return reverse('eventos:lista_eventos')

    def form_valid(self, form):
        # Impede salvar se estiver esgotado
        limite = LimiteCursosID.objects.first()
        limite_valor = limite.valor if limite else None
        total_inscritos = Curso.objects.count()
        if limite_valor is not None and total_inscritos >= limite_valor:
            form.add_error(None, "Esgotado")
            return self.form_invalid(form)
        print(">>> form_valid chamado")
        print("Dados do formulário:", form.cleaned_data)
        response = super().form_valid(form)
        print("Objeto salvo:", self.object)
        messages.success(self.request, "Inscrição efetuada com sucesso")
        return response

    def form_invalid(self, form):
        print(">>> form_invalid chamado")
        print("Erros do formulário:", form.errors)
        return super().form_invalid(form)

def autocomplete_cursos(request):
    termo = request.GET.get('q', '')
    cursos = CadastroDosCursos.objects.filter(nome__icontains=termo)
    # Monta a string: NOME (MODALIDADE)
    sugestoes = [f"{curso.nome} ({curso.modalidade})" for curso in cursos]
    return JsonResponse(sugestoes, safe=False)

def inscricao_curso(request, curso_id):
    # ... seu código para buscar o curso ...
    vagas_disponiveis = curso.vagas_disponiveis  # ou como você calcula isso

    context = {
        'form': form,
        'vagas_disponiveis': vagas_disponiveis,
        # outros contextos...
    }
    return render(request, 'eventos/inscricao_curso.html', context)

def dados_curso(request):
    nome_curso = request.GET.get('nome_curso')
    print(f"[LOG] Usuário digitou no autocomplete: {nome_curso}")
    try:
        curso = CadastroDosCursos.objects.get(nome=nome_curso)
        print(f"[LOG] Curso encontrado: {curso.nome}")
        data = {
            'nome_completo': '',
            'idade': '',
            'matricula': '',
            'email': '',
            'ocupacao': '',
            'coordenador': '',
            'modalidade': curso.modalidade,
        }
        return JsonResponse(data)
    except CadastroDosCursos.DoesNotExist:
        print("[LOG] Curso NÃO encontrado!")
        return JsonResponse({}, status=404)

def autocomplete_convidados(request):
    termo = request.GET.get('q', '')
    print(f"[LOG] Autocomplete convidados chamado com termo: {termo}")
    convidados = ConvidadoEspecial.objects.filter(nome_completo__icontains=termo)
    sugestoes = [f"{convidado.nome_completo}" for convidado in convidados]
    print(f"[LOG] Sugestões retornadas: {sugestoes}")
    return JsonResponse(sugestoes, safe=False)

def inscricao_convidado(request, evento_id):
    print(f"[LOG] View 'inscricao_convidado' chamada para evento_id={evento_id}")
    print(f"[LOG] Método HTTP: {request.method}")

    if request.method == "POST":
        print(f"[LOG] Dados recebidos no POST: {request.POST}")
        form = InscricaoConvidadoForm(request.POST)
        if form.is_valid():
            print("[LOG] Formulário válido, salvando inscrição.")
            form.save()
            messages.success(request, "Inscrição efetuada com sucesso!")
            return redirect(reverse('eventos:lista_eventos'))
        else:
            print(f"[LOG] Erros do formulário: {form.errors}")
    else:
        form = InscricaoConvidadoForm()
    total_vagas_disponivel = SenhaDeControle.objects.filter(vaga='disponivel').count()
    print(f"[LOG] Total de vagas disponível para o modal: {total_vagas_disponivel}")
    print("[LOG] Renderizando template de inscrição de convidado.")
    return render(request, 'eventos/inscricao_convidado.html', {
        'evento_id': evento_id,
        'form': form,
        'total_vagas_disponivel': total_vagas_disponivel,
    })

def dados_convidado(request):
    nome_convidado = request.GET.get('nome_convidado')
    print(f"[LOG] Dados do convidado chamado para: {nome_convidado}")
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
        print(f"[LOG] Dados encontrados: {data}")
        return JsonResponse(data)
    except ConvidadoEspecial.DoesNotExist:
        print("[LOG] Convidado não encontrado!")
        return JsonResponse({}, status=404)

def autocomplete_coordenadores(request):
    termo = request.GET.get('q', '')
    print(f"[LOG] autocomplete_coordenadores chamado com termo: '{termo}'")
    coordenadores = (
        CadastroDosCursos.objects
        .filter(coordenador__icontains=termo)
        .values_list('coordenador', flat=True)
        .distinct()
    )
    sugestoes = [c for c in coordenadores if c]
    print(f"[LOG] Sugestões retornadas: {sugestoes}")
    return JsonResponse(sugestoes, safe=False)

def inscricao_publico(request, evento_id):
    # Busca o limite cadastrado (se não existir, define como None)
    limite = LimitePublicoGeralID.objects.first()
    limite_valor = limite.valor if limite else None
    total_inscritos = PublicoGeral.objects.count()
    esgotado = limite_valor is not None and total_inscritos >= limite_valor

    if request.method == "POST" and not esgotado:
        form = InscricaoPublicoGeralForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscrição efetuada com sucesso!")
            return redirect('eventos:lista_eventos')
    else:
        form = InscricaoPublicoGeralForm()

    return render(request, 'eventos/inscricao_publico.html', {
        'evento_id': evento_id,
        'form': form,
        'limite_publico_geral': limite_valor,
        'total_inscritos': total_inscritos,
        'vagas_disponiveis': (limite_valor - total_inscritos) if limite_valor is not None else None,
        'esgotado': esgotado,
    }) 