from django.contrib import admin
from django.contrib.admin import AdminSite
from django.conf import settings
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class CustomAdminSite(AdminSite):
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        logger.info("CSS do Admin sendo carregado")
        logger.info(f"ADMIN_SITE_CSS: {settings.ADMIN_SITE_CSS}")
        return app_list

    def each_context(self, request):
        context = super().each_context(request)
        logger.info("Contexto do Admin sendo carregado")
        logger.info(f"CSS no contexto: {context.get('css')}")
        return context


admin_site = CustomAdminSite(name='admin')
admin.site = admin_site
