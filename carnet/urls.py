from django.conf.urls import url
from carnet import views

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^ajout_voiture/$', views.AjoutVoiture.as_view(), name='ajout_voiture'),
    url(r'^edite_voiture/(?P<pk>[0-9]+)/$', views.EditeVoiture.as_view(), name='edite_voiture'),
    url(r'^supprime_voiture/(?P<pk>[0-9]+)/$', views.SupprimeVoiture.as_view(), name='supprime_voiture'),
    url(r'^voiture/(?P<pk>[0-9]+)/$', views.ManageVoiture.as_view(), name='voiture'),
]
