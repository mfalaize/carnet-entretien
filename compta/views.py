import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic import TemplateView

from compta.models import Operation, Categorie, Compte, Budget
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
        return Operation.objects.filter(compte__utilisateurs=self.request.user, categorie__isnull=True).order_by(
            'date_operation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = datetime.date.today()
        if self.request.GET and self.request.GET['mois'] and self.request.GET['annee']:
            context['today'] = context['today'].replace(month=int(self.request.GET['mois']), year=int(self.request.GET['annee']))
        context['available_years'] = range(2017, 2025)
        context['categories'] = Categorie.objects.all().order_by('libelle')
        context['comptes'] = Compte.objects.filter(utilisateurs=self.request.user).order_by('libelle')
        context['budgets'] = Budget.objects.filter(utilisateurs=self.request.user).order_by('categorie__libelle')
        context['total_budget'] = 0
        context['total_depenses'] = 0
        context['total_solde'] = 0
        for budget in context['budgets']:
            budget.calcule_solde(context['today'])
            context['total_budget'] += budget.budget
            context['total_depenses'] += budget.depenses
            context['total_solde'] += budget.solde
        return context


@login_required
def edit_categorie(request):
    if request.method == 'POST':
        operation_id = request.POST['operation_id']
        categorie_id = request.POST['categorie']

        try:
            operation = Operation.objects.get(pk=operation_id, compte__utilisateurs=request.user)
            operation.categorie_id = categorie_id if categorie_id != '' else None
            operation.save()
        except Operation.DoesNotExist:
            raise Http404()

        return HttpResponse("OK")

    return HttpResponse("NOK", status=400)

