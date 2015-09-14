from carnet.models import Voiture
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs['autofocus'] = True


class VoitureForm(ModelForm):
    class Meta:
        model = Voiture
        fields = ['nom', 'modele', 'immatriculation', 'kilometrage', 'date_mise_circulation', 'moyenne_km_annuel',
                  'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs['autofocus'] = True
        self.fields['date_mise_circulation'].widget.attrs['class'] = 'datepicker'
