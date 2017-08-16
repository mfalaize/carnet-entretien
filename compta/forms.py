from django.forms import ModelForm

from compta.models import Budget


class BudgetForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['categorie', 'compte_associe', 'budget', 'solde_en_une_fois']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['budget'].widget.attrs['autofocus'] = True