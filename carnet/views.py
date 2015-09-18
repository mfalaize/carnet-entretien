# Create your views here.
from datetime import date

from carnet.forms import VoitureForm
from carnet.models import Voiture, Operation
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView


class Home(ListView):
    template_name = 'home.html'
    paginate_by = 10
    context_object_name = 'dernieres_operations'

    def get_queryset(self):
        self.voitures = Voiture.objects.filter(proprietaire=self.request.user)
        return Operation.objects.filter(voiture__in=self.voitures).order_by('effectue', '-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voitures'] = self.voitures
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def add_previous_link_in_context(request, context):
    if request.GET:
        context['previous'] = request.GET['previous']
    return context


class AjoutVoiture(CreateView):
    model = Voiture
    form_class = VoitureForm
    template_name = 'voiture.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['creation'] = True
        return add_previous_link_in_context(self.request, context)

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        form.instance.date_derniere_maj_km = date.today()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class EditeVoiture(UpdateView):
    model = Voiture
    form_class = VoitureForm
    template_name = 'voiture.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edition'] = True
        return add_previous_link_in_context(self.request, context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SupprimeVoiture(DeleteView):
    model = Voiture
    success_url = reverse_lazy('home')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ManageVoiture(TemplateView):
    template_name = 'manage_voiture.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voiture = get_object_or_404(Voiture, pk=kwargs['pk'])

        # Récupération des opérations à prévoir
        context['operations_a_prevoir'] = Operation.objects.filter(voiture=voiture, effectue=False).order_by(
            '-date')

        # Récupération des dernières opérations
        context['dernieres_operations'] = Operation.objects.filter(voiture=voiture, effectue=True).order_by(
            '-date')

        context['voiture'] = voiture
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
