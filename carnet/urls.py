from django.conf.urls import url
from carnet import views

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^ajout_voiture/$', views.AjoutVoiture.as_view(), name='ajout_voiture'),
    url(r'^edite_voiture/(?P<pk>[0-9]+)/$', views.EditeVoiture.as_view(), name='edite_voiture'),
    url(r'^supprime_voiture/(?P<pk>[0-9]+)/$', views.SupprimeVoiture.as_view(), name='supprime_voiture'),
    url(r'^voiture/(?P<pk>[0-9]+)/$', views.ManageVoiture.as_view(), name='voiture'),
    url(r'^voiture/(?P<pk>[0-9]+)/programme/$', views.ManageProgrammeMaintenance.as_view(), name='programme'),
    url(r'^voiture/(?P<pk>[0-9]+)/ajout_programme/$', views.AjoutProgrammeMaintenance.as_view(),
        name='ajout_programme'),
    url(r'^voiture/(?P<pk>[0-9]+)/edite_programme/(?P<pk_programme>[0-9]+)$', views.EditeProgrammeMaintenance.as_view(),
        name='edite_programme'),
    url(r'^voiture/(?P<pk>[0-9]+)/supprime_programme/(?P<pk_programme>[0-9]+)$',
        views.SupprimeProgrammeMaintenance.as_view(), name='supprime_programme'),
    url(r'^voiture/(?P<pk>[0-9]+)/ajout_revision/$', views.AjoutRevision.as_view(),
        name='ajout_revision'),
    url(r'^voiture/(?P<pk>[0-9]+)/edite_revision/(?P<pk_revision>[0-9]+)$', views.EditeProgrammeMaintenance.as_view(),
        name='edite_revision'),
    url(r'^voiture/(?P<pk>[0-9]+)/supprime_revision/(?P<pk_revision>[0-9]+)$',
        views.SupprimeProgrammeMaintenance.as_view(), name='supprime_revision'),
]
