from django import forms
from eventos.models import CadastroDosCursos
from .models import Curso, ConvidadoEspecial, SenhaDeControle, PublicoGeral

class InscricaoCursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome_curso', 'nome_completo', 'idade', 'matricula', 'email', 'ocupacao', 'coordenador']

    def clean_nome_completo(self):
        nome = self.cleaned_data['nome_completo'].strip()
        if Curso.objects.filter(nome_completo__iexact=nome).exists():
            raise forms.ValidationError("Você já está inscrito com esse nome completo.")
        return nome

    # ... outros campos ...
    nome_curso = forms.CharField(
        label="Nome do Curso",
        widget=forms.TextInput(attrs={'list': 'lista_cursos'})
    )
    # ... outros campos ... 

class InscricaoConvidadoForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail", required=True)

    class Meta:
        model = ConvidadoEspecial
        fields = [
            'nome_completo', 'idade', 'formacao', 'ocupacao',
            'recebeu_convite_de', 'senha_especial', 'email'
        ]
        labels = {
            'nome_completo': 'Nome do Convidado',
            'idade': 'Idade',
            'formacao': 'Formação',
            'ocupacao': 'Ocupação',
            'recebeu_convite_de': 'Recebeu o convite de quem',
            'senha_especial': 'Senha especial',
            'email': 'E-mail',
        }

    def clean_senha_especial(self):
        senha = self.cleaned_data['senha_especial'].strip()
        # Verifica se a senha existe na tabela SenhaDeControle (case-insensitive)
        if not SenhaDeControle.objects.filter(senha__iexact=senha).exists():
            raise forms.ValidationError("senha incorreta")
        # Verifica se já existe um convidado com essa senha (impede duplicidade)
        if ConvidadoEspecial.objects.filter(senha_especial__iexact=senha).exists():
            raise forms.ValidationError("Usuário cadastrado")
        return senha 

    def save(self, commit=True):
        instance = super().save(commit)
        # Atualiza a vaga da senha de controle para "Indisponível"
        senha = self.cleaned_data['senha_especial'].strip()
        try:
            senha_controle = SenhaDeControle.objects.get(senha__iexact=senha)
            if senha_controle.vaga != 'indisponivel':
                senha_controle.vaga = 'indisponivel'
                senha_controle.save()
        except SenhaDeControle.DoesNotExist:
            pass  # Não faz nada se não encontrar (mas não deveria acontecer)
        return instance 

class InscricaoPublicoGeralForm(forms.ModelForm):
    class Meta:
        model = PublicoGeral
        fields = ['nome_completo', 'idade', 'ocupacao', 'email']

    def clean_nome_completo(self):
        nome = self.cleaned_data['nome_completo'].strip()
        if PublicoGeral.objects.filter(nome_completo__iexact=nome).exists():
            raise forms.ValidationError("Você já está inscrito com esse nome completo.")
        return nome 