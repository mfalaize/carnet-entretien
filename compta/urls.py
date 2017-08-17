from django.conf.urls import url, include
from rest_framework import routers

from compta import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^edit-categorie$', views.edit_categorie, name='edit-categorie'),
    url(r'^ajout-budget/$', views.AjoutBudget.as_view(), name='ajout-budget'),
    url(r'^edite-budget/(?P<pk>[0-9]+)/$', views.EditeBudget.as_view(), name='edite-budget'),
    url(r'^supprime-budget/(?P<pk>[0-9]+)/$', views.SupprimeBudget.as_view(), name='supprime-budget'),
    url(r'^apply-budget/$', views.apply_budget, name='apply-budget'),
    url(r'^compte/(?P<pk>[0-9]+)/details-calcule-a-verser$', views.details_calcule_a_verser, name='details-calcule-a-verser')
]
