from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from .views import (CurrentUserView,
                    EditingAppRegistration,
                    EditingAppUpdate,
                    RelationViewSet,
                    VariantViewSet)

router = routers.DefaultRouter()

router.register(r'relation', RelationViewSet)
router.register(r'variant', VariantViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^oauth2-app/applications/register', EditingAppRegistration.as_view(),
        name='oauth2_provider:register'),
    url(r'^oauth2-app/applications/(?P<pk>\d+)/update/$',
        EditingAppUpdate.as_view(), name="update"),
    url(r'^oauth2-app/', include('oauth2_provider.urls',
        namespace='oauth2_provider')),

    url(r'^api/', include(router.urls)),
    url(r'^api/me/$', CurrentUserView.as_view(), name='current-user'),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url(r'^api-guide/?',
        TemplateView.as_view(template_name='api_guide/guide.html'),
        name='api-guide'),

    url(r'^$',
        TemplateView.as_view(template_name='gennotes_server/home.html'),
        name='home'),

    # django-allauth URLs
    url(r'^accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
