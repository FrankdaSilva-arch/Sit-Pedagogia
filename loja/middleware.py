import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('loja')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        logger.debug(f'Requisição iniciada: {request.path}')
        logger.debug(f'Método: {request.method}')
        if request.method == 'POST':
            logger.debug(f'Dados POST: {request.POST}')

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.debug(f'Requisição finalizada: {request.path}')
        logger.debug(f'Duração: {duration:.2f} segundos')
        logger.debug(f'Status: {response.status_code}')

        return response


class RelogioDigitalMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Verifica se a resposta contém referência ao 'Relógio Digital'
        if 'Relógio Digital' in response.content.decode('utf-8'):
            logger.info(
                f"URL com referência ao Relógio Digital: {request.path}")
        return response
