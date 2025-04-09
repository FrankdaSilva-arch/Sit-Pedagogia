from django.utils import timezone
import pytz


def obter_fuso_horario():
    """Obtém o fuso horário configurado"""
    try:
        from .models import ConfiguracaoFusoHorario
        config = ConfiguracaoFusoHorario.objects.first()
        if config and config.fuso_horario:
            return pytz.timezone(config.fuso_horario)
    except Exception:
        pass
    return pytz.timezone('America/Manaus')  # UTC-4 como padrão


def ajustar_horario(data):
    """Ajusta a data/hora para o fuso horário configurado"""
    fuso_horario = obter_fuso_horario()
    if not timezone.is_aware(data):
        data = timezone.make_aware(data)
    return data.astimezone(fuso_horario)
