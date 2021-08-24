from .api_urls import urlpatterns as api_urlpatterns
from .yasg import urlpatterns as doc_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns))
]

# swagger
urlpatterns += doc_urls

# debug toolbar
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
