from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class ImagemEvento(models.Model):
    evento = models.ForeignKey(
        'Evento', on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(
        upload_to='eventos/imagens/%Y/%m/',
        verbose_name='Imagem',
        help_text='Selecione uma imagem'
    )
    legenda = models.CharField(
        max_length=200,
        blank=True,
        help_text='Descrição opcional da imagem'
    )
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'
        ordering = ['ordem']

    def __str__(self):
        return f"Imagem {self.ordem} do evento {self.evento.titulo}"


class Evento(models.Model):
    curso_responsavel = models.CharField(
        max_length=200,
        verbose_name='Curso responsável',
        help_text='Nome do curso responsável pelo evento'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título do evento',
        help_text='Título do evento'
    )
    tema = models.CharField(
        max_length=200,
        help_text='Tema principal do evento'
    )
    data = models.DateTimeField(
        verbose_name='Data do evento',
        help_text='Data e hora do evento'
    )
    local = models.CharField(
        max_length=200,
        verbose_name='Local do evento',
        help_text='Endereço ou local onde será realizado o evento'
    )
    descricao = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição detalhada do evento'
    )

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.titulo

    def clean(self):
        # Validar se a data não é no passado
        if self.data and self.data < timezone.now():
            raise ValidationError(
                {'data': 'A data do evento não pode ser no passado'})

    def limite_imagens(self):
        if self.imagens.count() >= 10:
            raise ValidationError(
                'Não é possível adicionar mais de 10 imagens por evento.')


class Curso(models.Model):
    nome_curso = models.CharField(
        "Nome do Curso", max_length=200, blank=True, null=True)
    nome_completo = models.CharField("Nome completo", max_length=200)
    idade = models.PositiveIntegerField("Idade")
    matricula = models.CharField("Matrícula", max_length=20)
    email = models.EmailField("E-mail")
    ocupacao = models.CharField("Ocupação", max_length=100)
    coordenador = models.CharField("Coordenador(a)", max_length=200)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.nome_completo


class ConvidadoEspecial(models.Model):
    nome_completo = models.CharField("Nome completo", max_length=200)
    idade = models.PositiveIntegerField("Idade")
    formacao = models.CharField("Formação", max_length=200)
    ocupacao = models.CharField("Ocupação", max_length=100)
    recebeu_convite_de = models.CharField(
        "Recebeu o convite de quem", max_length=200)
    senha_especial = models.CharField("Senha especial", max_length=100)
    email = models.EmailField("E-mail", max_length=254, blank=True, null=True)

    class Meta:
        verbose_name = "Convidado(a) Especial"
        verbose_name_plural = "Convidados(as) Especiais"

    def __str__(self):
        return self.nome_completo


class PublicoGeral(models.Model):
    nome_completo = models.CharField("Nome completo", max_length=200)
    idade = models.PositiveIntegerField("Idade")
    ocupacao = models.CharField("Ocupação", max_length=100)
    email = models.EmailField("E-mail", max_length=254, blank=True, null=True)

    class Meta:
        verbose_name = "Público Geral"
        verbose_name_plural = "Público Geral"

    def __str__(self):
        return self.nome_completo


class CadastroDosCursos(models.Model):
    nome = models.CharField(max_length=255)
    modalidade = models.CharField(max_length=100)
    coordenador = models.CharField("Coordenador(a)", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Cadastro dos Cursos"
        verbose_name_plural = "Cadastro dos Cursos"

    def __str__(self):
        return self.nome


class SenhaDeControle(models.Model):
    senha = models.CharField("Senha de controle", max_length=100, unique=True)
    observacao = models.TextField("Observação", blank=True)
    VAGA_CHOICES = [
        ('disponivel', 'Disponível'),
        ('indisponivel', 'Indisponível'),
    ]
    vaga = models.CharField("Vaga", max_length=20,
                            choices=VAGA_CHOICES, default='disponivel')

    class Meta:
        verbose_name = "Senha de controle"
        verbose_name_plural = "Senhas de controle"

    def __str__(self):
        return self.senha


class LimiteCursosID(models.Model):
    valor = models.PositiveIntegerField("Valor do limite")

    class Meta:
        verbose_name = "Limite cursos ID"
        verbose_name_plural = "Limite cursos ID"

    def __str__(self):
        return f"Limite cursos ID: {self.valor}"


class LimitePublicoGeralID(models.Model):
    valor = models.PositiveIntegerField("Valor do limite")

    class Meta:
        verbose_name = "Limite público geral ID"
        verbose_name_plural = "Limite público geral ID"

    def __str__(self):
        return f"Limite público geral ID: {self.valor}"
