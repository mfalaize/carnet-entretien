from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Budget(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))


class Categorie(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))
    libelle = models.CharField(max_length=256, verbose_name=_('Libellé'))


class BudgetCategorie(models.Model):
    categorie = models.ForeignKey(Categorie, verbose_name=_('Catégorie'))
    budget = models.ForeignKey(Budget, verbose_name=_('Budget'))
    valeur = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Valeur'))


