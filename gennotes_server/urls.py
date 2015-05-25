from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    # Examples:
    # url(r'^$', 'gennotes_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$',
        TemplateView.as_view(template_name='gennotes_server/home.html'),
        name='home'),

    url(r'^admin/', include(admin.site.urls)),

    # django-allauth URLs
    url(r'^accounts/', include('allauth.urls')),
]
