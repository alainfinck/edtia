"""
URLs principales pour Edtia
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Interface publique
    path('', include('apps.public.urls')),
    
    # Applications internes
    path('accounts/', include('apps.accounts.urls')),
    path('etablissements/', include('apps.etablissements.urls')),
    path('emplois-temps/', include('apps.emplois_temps.urls')),
    path('remplacements/', include('apps.remplacements.urls')),
    path('notifications/', include('apps.notifications.urls')),
    
    # API
    path('api/', include('apps.core.urls')),
    path('api/etablissements/', include('apps.etablissements.urls')),
    path('api/emplois-temps/', include('apps.emplois_temps.urls')),
    path('api/remplacements/', include('apps.remplacements.urls')),
    path('api/ia/', include('apps.ia_optimisation.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
