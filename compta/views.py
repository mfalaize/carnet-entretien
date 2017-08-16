import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from compta.forms import BudgetForm
from compta.models import Operation, Categorie, Compte, Budget, CategorieEpargne, OperationEpargne, Epargne
from compta.serializers import UserSerializer, GroupSerializer
from django.contrib.auth.models import User, Group
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class Index(TemplateView):
    template_name = 'index.html'

    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required
def apply_budget(request):
    if request.method == 'POST':
        budget_id = request.POST['budget_id']
        budget_value = request.POST['budget_value'].replace(',', '.')

        try:
            if budget_value is not None:
                budget = Budget.objects.get(pk=budget_id)
                budget.budget = budget_value
                budget.save()
        except Budget.DoesNotExist:
            raise Http404()

        return redirect('compta:home')

    return HttpResponse("NOK", status=400)


@method_decorator(login_required, name='dispatch')
class EditeBudget(UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'compta/budget.html'
    success_url = reverse_lazy('compta:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edition'] = True
        return context


@method_decorator(login_required, name='dispatch')
class Home(ListView):
    model = Operation
    template_name = 'compta/home.html'
    paginate_by = 10
    context_object_name = 'operations_a_categoriser'

    def get_queryset(self):
        return Operation.objects.filter(compte__utilisateurs=self.request.user, budget__isnull=True, hors_budget=False,
                                        recette=False, contributeur_id__isnull=True).order_by('date_operation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = datetime.date.today()
        if self.request.GET and self.request.GET['mois'] and self.request.GET['annee']:
            context['today'] = context['today'].replace(month=int(self.request.GET['mois']),
                                                        year=int(self.request.GET['annee']))
        context['available_years'] = range(2017, 2025)
        context['categories'] = Categorie.objects.all().order_by('libelle')
        context['categories_epargne'] = CategorieEpargne.objects.all().order_by('libelle')
        context['comptes'] = Compte.objects.filter(utilisateurs=self.request.user).order_by('libelle')
        context['epargnes'] = Epargne.objects.filter(utilisateurs=self.request.user).order_by('categorie__libelle')

        self.request.user.revenus_personnels = self.request.user.get_revenus_personnels(context['today'])

        context['total_epargnes'] = 0
        context['total_epargne_reel'] = 0

        for epargne in context['epargnes']:
            context['total_epargnes'] += epargne.solde

        for compte in context['comptes']:
            compte.calculer_parts(context['today'])

            for user in compte.utilisateurs_list:
                if user.pk == self.request.user.pk:
                    compte.utilisateur = user
                    break

            # Vérification que le total des comptes épargnes est égal au total_epargne
            if compte.epargne:
                context['total_epargne_reel'] += compte.solde

            for budget in compte.budgets:
                budget.hidden = budget.solde == 0 or budget.solde_en_une_fois and budget.depenses == 0
                budget.warning = budget.solde_en_une_fois and budget.depenses > 0 and budget.solde > 0
                budget.danger = budget.solde_en_une_fois and budget.depenses > 0 and budget.solde < 0

        return context


@login_required
def edit_categorie(request):
    if request.method == 'POST':
        operation_id = request.POST['operation_id']
        categorie_id = request.POST['categorie']
        try:
            want_redirect = request.POST['redirect'] == 'true'
        except KeyError:
            want_redirect = False

        try:
            operation = Operation.objects.get(pk=operation_id, compte__utilisateurs=request.user)
            if operation.compte.epargne:
                operation.hors_budget = True
                operation.recette = False
                operation.contributeur_id = None
                operation.avance = False
                operation.save()

                op_epargne = OperationEpargne.objects.get(operation_id=operation_id)
                op_epargne.epargne_id = categorie_id
                op_epargne.save()

                epargne = Epargne.objects.get(pk=categorie_id, utilisateurs=request.user)
                epargne.solde += op_epargne.montant
                epargne.save()

            elif categorie_id == '-1':
                operation.budget_id = None
                operation.hors_budget = True
                operation.recette = False
                operation.contributeur_id = None
                operation.avance = False
                operation.save()
            elif categorie_id == '-2':
                operation.budget_id = None
                operation.hors_budget = False
                operation.recette = True
                operation.contributeur_id = None
                operation.avance = False
                operation.save()
            elif categorie_id != '' and int(categorie_id[1:]) < -1000:
                contributeur_id = -(int(categorie_id[1:]) + 1000)
                operation.budget_id = None
                operation.hors_budget = False
                operation.recette = False
                operation.contributeur_id = contributeur_id
                operation.avance = True if categorie_id[0:1] == 'a' else False
                operation.save()
            else:
                operation.budget_id = categorie_id if categorie_id != '' else None
                operation.hors_budget = False
                operation.recette = False
                operation.contributeur_id = None
                operation.avance = False
                operation.save()

        except Operation.DoesNotExist or OperationEpargne.DoesNotExist or Epargne.DoesNotExist:
            raise Http404()

        if want_redirect:
            return redirect('compta:home')
        return HttpResponse("OK")

    return HttpResponse("NOK", status=400)
