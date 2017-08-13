import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic import TemplateView

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
            context['today'] = context['today'].replace(month=int(self.request.GET['mois']), year=int(self.request.GET['annee']))
        context['available_years'] = range(2017, 2025)
        context['categories'] = Categorie.objects.all().order_by('libelle')
        context['categories_epargne'] = CategorieEpargne.objects.all().order_by('libelle')
        context['comptes'] = Compte.objects.filter(utilisateurs=self.request.user).order_by('libelle')
        context['budgets'] = Budget.objects.filter(compte_associe__utilisateurs=self.request.user).order_by('categorie__libelle')
        context['comptes_associes'] = Compte.objects.filter(utilisateurs=self.request.user, budget__isnull=False).distinct().order_by('libelle')
        context['total_budget'] = {}
        context['total_depenses'] = {}
        context['total_solde'] = {}
        for compte in context['comptes_associes']:
            context['total_budget'][compte.pk] = 0
            context['total_depenses'][compte.pk] = 0
            context['total_solde'][compte.pk] = 0

        for budget in context['budgets']:
            budget.calcule_solde(context['today'])
            context['total_budget'][budget.compte_associe_id] += budget.budget
            context['total_depenses'][budget.compte_associe_id] += budget.depenses
            context['total_solde'][budget.compte_associe_id] += budget.solde

        context['epargnes'] = Epargne.objects.filter(utilisateurs=self.request.user).order_by('categorie__libelle')
        context['total_epargnes'] = 0
        for epargne in context['epargnes']:
            context['total_epargnes'] += epargne.solde

        # Vérification que le total des comptes épargnes est égal au total_epargne
        context['total_epargne_reel'] = 0
        context['revenus_personnels_du_mois'] = next(iter(Operation.objects.filter(date_operation__month=context['today'].month, recette=True, compte__utilisateurs=self.request.user).aggregate(Sum('montant')).values()))
        if context['revenus_personnels_du_mois'] is None:
            context['revenus_personnels_du_mois'] = 0
        context['revenus_personnels_autres_utilisateurs'] = {}
        context['a_verser_sur_compte_joint'] = {}
        context['contributions'] = {}
        context['contributions_totales'] = {}
        context['contributions_pourcentages'] = {}
        for compte in context['comptes']:
            if compte.epargne:
                context['total_epargne_reel'] += compte.solde

            context['revenus_personnels_autres_utilisateurs'][compte.pk] = next(iter(Operation.objects.filter(date_operation__month=context['today'].month, recette=True).exclude(compte__utilisateurs=self.request.user).aggregate(Sum('montant')).values()))
            if context['revenus_personnels_autres_utilisateurs'][compte.pk] is None:
                context['revenus_personnels_autres_utilisateurs'][compte.pk] = 0
            part = 1 if context['revenus_personnels_autres_utilisateurs'][compte.pk] == 0 else context['revenus_personnels_du_mois'] / (context['revenus_personnels_du_mois'] + context['revenus_personnels_autres_utilisateurs'][compte.pk])
            try:
                context['a_verser_sur_compte_joint'][compte.pk] = int(part * context['total_budget'][compte.pk])
            except KeyError or ZeroDivisionError:
                context['a_verser_sur_compte_joint'][compte.pk] = 0

            context['contributions'][compte.pk] = 0
            context['contributions_totales'][compte.pk] = 0
            context['contributions_pourcentages'][compte.pk] = 0
            for operation in compte.operation_set.filter(contributeur_id__isnull=False):
                if operation.contributeur_id == self.request.user.pk:
                    context['contributions'][compte.pk] += operation.montant
                context['contributions_totales'][compte.pk] += operation.montant
            if context['contributions_totales'][compte.pk] > 0:
                context['contributions_pourcentages'][compte.pk] += int(int(context['contributions'][compte.pk]) / int(context['contributions_totales'][compte.pk]) * 100)

        return context


@login_required
def edit_categorie(request):
    if request.method == 'POST':
        operation_id = request.POST['operation_id']
        categorie_id = request.POST['categorie']

        try:
            operation = Operation.objects.get(pk=operation_id, compte__utilisateurs=request.user)
            if operation.compte.epargne:
                operation.hors_budget = True
                operation.recette = False
                operation.contributeur_id = None
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
                operation.save()
            elif categorie_id == '-2':
                operation.budget_id = None
                operation.hors_budget = False
                operation.recette = True
                operation.contributeur_id = None
                operation.save()
            elif int(categorie_id) < -1000:
                contributeur_id = -(int(categorie_id) + 1000)
                operation.budget_id = None
                operation.hors_budget = False
                operation.recette = False
                operation.contributeur_id = contributeur_id
                operation.save()
            else:
                operation.budget_id = categorie_id if categorie_id != '' else None
                operation.hors_budget = False
                operation.recette = False
                operation.contributeur_id = None
                operation.save()

        except Operation.DoesNotExist or OperationEpargne.DoesNotExist or Epargne.DoesNotExist:
            raise Http404()

        return HttpResponse("OK")

    return HttpResponse("NOK", status=400)

