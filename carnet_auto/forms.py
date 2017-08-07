from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, ValidationError, CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _
from extra_views import InlineFormSet

from carnet_auto.models import Voiture, ProgrammeMaintenance, Revision, Operation



class VoitureForm(ModelForm):
    class Meta:
        model = Voiture
        fields = ['nom', 'modele', 'immatriculation', 'kilometrage', 'date_mise_circulation', 'moyenne_km_annuel',
                  'prix_achat', 'date_achat', 'kilometrage_achat', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs['autofocus'] = True
        self.fields['date_mise_circulation'].widget.attrs['class'] = 'datepicker'
        self.fields['date_achat'].widget.attrs['class'] = 'datepicker'

    def clean(self):
        cleaned_data = super().clean()

        # La date d'achat doit être inférieure à la date de mise en circulation
        if cleaned_data['date_achat'] is not None and cleaned_data['date_achat'] < cleaned_data['date_mise_circulation']:
            raise ValidationError(_("La date d'achat ne peut pas précéder la date de mise en circulation"))

        return cleaned_data


class ProgrammeMaintenanceForm(ModelForm):
    class Meta:
        model = ProgrammeMaintenance
        fields = ['periodicite_kilometres', 'periodicite_annees', 'delai_alerte', 'delai_rappel', 'types_operations']
        widgets = {
            'types_operations': CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['periodicite_kilometres'].widget.attrs['autofocus'] = True


class RevisionForm(ModelForm):
    class Meta:
        model = Revision
        fields = ['date', 'kilometrage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datepicker'


class OperationForm(ModelForm):
    id_operation_prevue = forms.IntegerField(required=False, min_value=0)

    class Meta:
        model = Operation
        fields = '__all__'


class AjoutOperationFormSet(InlineFormSet):
    form_class = OperationForm
    model = Operation
    extra = 1


class EditeOperationFormSet(AjoutOperationFormSet):
    extra = 0
