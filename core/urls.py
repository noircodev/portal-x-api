from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('event.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/system/', include('sys_monitor.urls')),

]
# handler404 = 'event.views.custom_page_not_found_view'
# handler500 = 'web.views.custom_server_error_view'
PROD_ENV = getattr(settings, 'PROD_ENV', False)
if not PROD_ENV:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    from event.utils.permissions import StaffOnlySwaggerView
    from event.utils.permissions import IsAdminUserOrStaff

    doc_url_patterns = [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[IsAdminUserOrStaff]),
            name="swagger-ui"
        ),
        path(
            "api/docs/redoc/",
            SpectacularRedocView.as_view(url_name="schema", permission_classes=[IsAdminUserOrStaff]),
            name="redoc-ui"
        ),
        path('api/docs/', StaffOnlySwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    ]
    urlpatterns += doc_url_patterns

    # Custom preprocessing hook example

    def custom_preprocessing_hook(result, generator, request, public):
        """
        Custom preprocessing hook to modify the schema.
        """
        # Add custom server information
        result['servers'] = [
            {
                'url': 'https://api.yourapp.com/api/v1',
                'description': 'Production server'
            },
            {
                'url': 'https://staging-api.yourapp.com/api/v1',
                'description': 'Staging server'
            },
            {
                'url': 'http://localhost:8000/api/v1',
                'description': 'Development server'
            }
        ]

        # Add global security schemes
        result['components']['securitySchemes'] = {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            },
            'apiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key'
            }
        }

        # Add contact information
        result['info']['contact'] = {
            'name': 'API Support',
            'email': 'api-support@yourapp.com',
            'url': 'https://yourapp.com/support'
        }

        return result


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Portal-X Events"
admin.site.site_title = "Portal-X Events"
admin.site.index_title = "Portal-X Events"
