from django.utils import timezone
from .models import ConfiguracaoFusoHorario
import pytz
from django.core.exceptions import ValidationError


def get_fuso_horario_configurado():
    """
    Retorna o fuso horário configurado no sistema.
    Se não houver configuração, retorna o fuso horário padrão (America/Porto_Velho).
    """
    try:
        config = ConfiguracaoFusoHorario.objects.first()
        if config:
            return pytz.timezone(config.fuso_horario)
    except:
        pass
    return pytz.timezone('America/Porto_Velho')


def ajustar_horario(data):
    """
    Ajusta a data para o fuso horário configurado no sistema.
    """
    fuso_horario = get_fuso_horario_configurado()
    if data.tzinfo is None:
        data = timezone.make_aware(data)
    return data.astimezone(fuso_horario)


def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido')

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[9]):
        raise ValidationError('CPF inválido')

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[10]):
        raise ValidationError('CPF inválido')

    return cpf


def validar_telefone(telefone):
    # Remove caracteres não numéricos
    telefone = ''.join(filter(str.isdigit, telefone))

    # Verifica se tem 10 ou 11 dígitos
    if len(telefone) not in [10, 11]:
        raise ValidationError('Telefone deve ter 10 ou 11 dígitos')

    return telefone
