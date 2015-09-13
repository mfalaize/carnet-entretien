# Create your views here.
from datetime import date

from carnet.models import Voiture, OperationMaintenance
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView


class Home(ListView):
    template_name = 'home.html'
    paginate_by = 10
    context_object_name = 'dernieres_operations'

    def get_queryset(self):
        self.voitures = Voiture.objects.filter(proprietaire=self.request.user)
        return OperationMaintenance.objects.filter(voiture__in=self.voitures).order_by('effectue', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voitures'] = self.voitures
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AjoutVoiture(CreateView):
    model = Voiture
    template_name = 'voiture.html'
    fields = ['nom', 'modele', 'immatriculation', 'kilometrage', 'date_mise_circulation', 'moyenne_km_annuel',
              'photo']
    success_url = reverse_lazy('home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nom'].widget.attrs['autofocus'] = True
        form.fields['date_mise_circulation'].widget.attrs['class'] = 'datepicker'
        return form

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        form.instance.date_derniere_maj_km = date.today()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
