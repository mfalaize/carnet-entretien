# Create your views here.
from datetime import date

from carnet.forms import VoitureForm, ProgrammeMaintenanceForm, RevisionForm, OperationForm
from carnet.models import Voiture, Operation, ProgrammeMaintenance, Revision
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from extra_views import CreateWithInlinesView


class Home(ListView):
    model = Voiture
    template_name = 'home.html'
    paginate_by = 10
    context_object_name = 'dernieres_operations'

    def get_queryset(self):
        return Operation.objects.get_all_dernieres_operations(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voitures'] = Voiture.objects.get_voitures_for_user(self.request.user)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AjoutVoiture(CreateView):
    model = Voiture
    form_class = VoitureForm
    template_name = 'voiture.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['creation'] = True
        return context

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

    def get_queryset(self):
        # On vérifie que la voiture correspond bien à une voiture de l'utilisateur
        return super().get_queryset().filter(proprietaire=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edition'] = True
        return context

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
        # On charge la voiture en prenant soin de regarder si elle appartient à l'utilisateur
        voiture = get_object_or_404(Voiture, pk=kwargs['pk'], proprietaire=self.request.user)

        # Récupération des opérations à prévoir
        context['operations_a_prevoir'] = Operation.objects.get_operations_a_prevoir(voiture)

        # Récupération des dernières opérations
        context['dernieres_operations'] = Operation.objects.get_dernieres_operations(voiture)

        context['voiture'] = voiture
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ManageProgrammeMaintenance(ListView):
    model = ProgrammeMaintenance
    paginate_by = 20
    context_object_name = 'programmes'
    template_name = 'manage_programme.html'

    def get_queryset(self):
        return ProgrammeMaintenance.objects.get_programmes_for_voiture(voiture_pk=self.kwargs['pk'],
                                                                       user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voiture = get_object_or_404(Voiture, pk=self.kwargs['pk'], proprietaire=self.request.user)
        context['voiture'] = voiture
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AjoutProgrammeMaintenance(CreateView):
    model = ProgrammeMaintenance
    form_class = ProgrammeMaintenanceForm
    template_name = 'programme.html'
    context_object_name = 'programme'

    def get_success_url(self):
        return reverse_lazy('programme', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['creation'] = True
        context['pk_voiture'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.instance.voiture = Voiture.objects.get(pk=self.kwargs['pk'], proprietaire=self.request.user)
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class EditeProgrammeMaintenance(UpdateView):
    model = ProgrammeMaintenance
    form_class = ProgrammeMaintenanceForm
    template_name = 'programme.html'
    pk_url_kwarg = 'pk_programme'
    context_object_name = 'programme'

    def get_success_url(self):
        return reverse_lazy('programme', kwargs={'pk': self.kwargs['pk']})

    def get_queryset(self):
        # On vérifie que la voiture correspond bien à une voiture de l'utilisateur
        return super().get_queryset().filter(voiture__proprietaire=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edition'] = True
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SupprimeProgrammeMaintenance(DeleteView):
    model = ProgrammeMaintenance
    pk_url_kwarg = 'pk_programme'

    def get_success_url(self):
        return reverse_lazy('programme', kwargs={'pk': self.kwargs['pk']})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AjoutRevision(CreateWithInlinesView):
    model = Revision
    form_class = RevisionForm
    inlines = [OperationForm]
    template_name = 'revision.html'
    context_object_name = 'revision'

    def get_success_url(self):
        return reverse_lazy('voiture', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['creation'] = True
        context['pk_voiture'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.instance.voiture = Voiture.objects.get(pk=self.kwargs['pk'], proprietaire=self.request.user)
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)