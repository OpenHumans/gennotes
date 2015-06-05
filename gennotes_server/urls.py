from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from .views import RelationViewSet, VariantViewSet

router = routers.DefaultRouter()
router.register(r"relation", RelationViewSet)
router.register(r"variant", VariantViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    url(r'^$',
        TemplateView.as_view(template_name='gennotes_server/home.html'),
        name='home'),

    url(r'^admin/', include(admin.site.urls)),

    # django-allauth URLs
    url(r'^accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
