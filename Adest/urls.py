from django.conf import settings
from django.contrib import admin
from django.urls import include, path
import debug_toolbar
from django.conf.urls.static import static


urlpatterns = [
    # url(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,{'document_root':settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('users/', include('users.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    