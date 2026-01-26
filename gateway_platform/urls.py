"""
URL configuration for gateway_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Favicon redirect - browsers look for /favicon.ico
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.svg', permanent=True)),
    
    # Gateway web routes (QR codes, activation, etc.)
    path('gateways/', include('apps.gateways.urls')),
    
    # Account web routes (login, dashboard, wallet, etc.)
    path('accounts/', include('apps.accounts.urls')),
    
    # API routes
    path('api/v1/routing/', include('apps.routing.urls')),
    path('api/v1/interactions/', include('apps.interactions.urls')),
    path('api/v1/communications/', include('apps.communications.urls')),
    
    # Core routes (home, etc.)
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers for production
handler404 = 'apps.core.error_handlers.handler404'
handler500 = 'apps.core.error_handlers.handler500'
handler403 = 'apps.core.error_handlers.handler403'
handler400 = 'apps.core.error_handlers.handler400'