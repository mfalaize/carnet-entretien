from django.conf.urls import url, include

from assmat import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^$', views.home, name='home'),
    url(r'^valider$', views.valider, name='valider')

]
