from django.core.exceptions import ValidationError
import re


def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')


def validar_telefone(telefone):
    telefone = ''.join(filter(str.isdigit, telefone))
    if len(telefone) < 10 or len(telefone) > 11:
        raise ValidationError('Telefone deve ter 10 ou 11 dígitos')
