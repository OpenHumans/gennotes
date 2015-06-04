from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from .views import RelationViewSet, VariantViewSet

router = routers.DefaultRouter()
router.register(r"relation", RelationViewSet)
router.register(r"variant", VariantViewSet)


urlpatterns = [
    # Examples:
    # url(r'^$', 'gennotes_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),

    url(r'^$',
        TemplateView.as_view(template_name='gennotes_server/home.html'),
        name='home'),

    url(r'^admin/', include(admin.site.urls)),

    # django-allauth URLs
    url(r'^accounts/', include('allauth.urls')),
]
