from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from django.contrib.auth import logout

print("CARREGANDO URLS PRINCIPAIS")


def logout_view(request):
    logout(request)
    return RedirectView.as_view(url='/')(request)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('eventos/', include('eventos.urls')),
    path('', include('loja.urls')),
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
