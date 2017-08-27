from django import forms
from django.utils.translation import ugettext_lazy as _

from compta.models import Budget, OperationEpargne, Operation, CategorieEpargne


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['categorie', 'compte_associe', 'budget', 'solde_en_une_fois']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['budget'].widget.attrs['autofocus'] = True


class OperationCategoriesForm(forms.Form):
    operation_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    categorie = forms.ChoiceField(required=False, choices=(("", ""),))
    redirect = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

    def __init__(self, post, render_initial=True):
        if render_initial:
            super().__init__()
        else:
            super().__init__(post)

        operation = post.get('operation')
        categories_epargne = post.get('categories_epargne')
        redirect = post.get('redirect')
        operation_id = post.get('operation_id')

        if redirect is not None:
            self.fields['redirect'].initial = redirect
            if redirect:
                self.fields['categorie'].widget = forms.HiddenInput()
                self.fields['categorie'].initial = ""

        if operation is None and operation_id is not None:
            if render_initial:
                self.fields['operation_id'].initial = post.get('operation_id')
            else:
                operation = Operation.objects.get(pk=int(operation_id))

        if operation is not None:
            operation.load_categorie()

            if operation.categorie_id is not None:
                self.fields['categorie'].initial = operation.categorie_id

            self.fields['operation_id'].initial = operation.pk
            if operation.compte.epargne:
                if operation.montant >= 0:
                    self.fields['categorie'].disabled = True
                    self.fields['categorie'].choices = (("", _("Partagé entre les différentes catégories")),)
                else:
                    if categories_epargne is None:
                        categories_epargne = CategorieEpargne.objects.all().order_by('libelle')
                    for categorie in categories_epargne:
                        self.fields['categorie'].choices += ((str(categorie.pk).replace(" ", ""), categorie.libelle),)
            else:
                self.fields['categorie'].choices += (("-1", _("Hors Budget")),)
                self.fields['categorie'].choices += (("-2", _("Revenue")),)
                self.fields['categorie'].choices += (("-3", _("Avance sur débit(s) futur(s)")),)
                if operation.compte.utilisateurs.count() > 1:
                    for utilisateur in operation.compte.utilisateurs.all():
                        self.fields['categorie'].choices += (("c" + str(-1000 - utilisateur.pk).replace(' ', ''),
                                                              _("Contribution") + " " + utilisateur.first_name),)
                    for utilisateur in operation.compte.utilisateurs.all():
                        self.fields['categorie'].choices += (("a" + str(-1000 - utilisateur.pk).replace(' ', ''), _(
                            "Contribution (avances)") + " " + utilisateur.first_name),)
                for budget in operation.compte.budget_set.all():
                    self.fields['categorie'].choices += ((budget.pk, budget.categorie.libelle),)
        else:
            self.fields['operation_id'].initial = post.get('operation_id')
