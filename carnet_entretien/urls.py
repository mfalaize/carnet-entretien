"""carnet_entretien URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from carnet.forms import BootstrapAuthenticationForm
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth

urlpatterns = [
    url(r'^carnet_auto/', include('carnet.urls')),
    url(r'^compta/', include('compta.urls')),
    url(r'^login/$', auth.login, {'authentication_form': BootstrapAuthenticationForm}, name='login'),
    url(r'^logout/$', auth.logout, {'next_page': 'login'}, name='logout'),
    url(r'^password_change/$', auth.password_change, name='password_change'),
    url(r'^password_change/done/$', auth.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth.password_reset_complete, name='password_reset_complete'),
    url(r'^admin/', include(admin.site.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
