from django import forms

from assmat.models import JourTravail


class JourTravailForm(forms.ModelForm):
    class Meta:
        model = JourTravail
        fields = ["type", "heures_effectuees", "heures_complementaires", "heures_supplementaires", "repas", "gouter"]
