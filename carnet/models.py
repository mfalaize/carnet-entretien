from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_image_user_path(instance, filename):
    """Utilisé par le modèle Voiture"""
    user = instance.proprietaire
    return 'img/%s/%s' % (user.username, filename)


class ChampSupplementaire(models.Model):
    """Représente un champ supplémentaire spécifique pour un type d'opération"""
    libelle = models.CharField(max_length=128)


class TypeOperation(models.Model):
    """Représente un type d'opération unitaire à effectuer sur une voiture"""
    nom = models.CharField(max_length=256)
    champs_supplementaires = models.ManyToManyField(ChampSupplementaire)


class Voiture(models.Model):
    """Représente une voiture"""
    nom = models.CharField(max_length=256, verbose_name=_('Nom de la voiture'), help_text=_("Ex : Voiture de Maxime"))
    immatriculation = models.CharField(max_length=16, verbose_name=_('Immatriculation'))
    modele = models.CharField(max_length=256, verbose_name=_('Modèle'),
                              help_text=_('Ex : RENAULT Mégane II 1.5 dCi 86cv'))
    kilometrage = models.IntegerField(verbose_name=_('Nombre de Km au compteur'))
    date_mise_circulation = models.DateField(verbose_name=_('Date de mise en circulation'))
    moyenne_km_annuel = models.IntegerField(verbose_name=_('Nombre de Km effectués annuellement par la voiture'))
    date_derniere_maj_km = models.DateField(verbose_name=_('Date de dernière mise à jour du kilométrage'))
    photo = models.ImageField(upload_to=get_image_user_path, blank=True, verbose_name="Photo")
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Propriétaire'))
    prix_achat = models.DecimalField(null=True, decimal_places=2, max_digits=10, verbose_name=_("Prix d'achat"))
    date_achat = models.DateField(null=True, verbose_name=_("Date d'achat"))
    kilometrage_achat = models.IntegerField(null=True, verbose_name="Nombre de Km à l'achat")


class ProgrammeMaintenance(models.Model):
    """Représente une liste d'opérations pour un programme de maintenance pour une voiture"""
    types_operations = models.ManyToManyField(TypeOperation)
    periodicite_kilometres = models.IntegerField(null=True, blank=True, verbose_name=_("Périodicité en Km"))
    periodicite_annees = models.IntegerField(null=True, blank=True, verbose_name=_("Périodicité en année"))
    delai_alerte = models.IntegerField(default=0, blank=True,
                                       verbose_name=_("Délai pour déclencher une alerte (en jours)"),
                                       help_text=_("Contrôle le délai d'alerte pour une opération à effectuer " +
                                                   "de façon à déclencher l'alerte plus tôt que le jour j (par " +
                                                   "défaut est déclenché le jour j)"))
    delai_rappel = models.IntegerField(default=15, blank=True,
                                       verbose_name=_("Délai pour déclencher un rappel (en jours)"),
                                       help_text=_(
                                           "Le rappel permet de renvoyer un mail lorsque les opérations du programme " +
                                           "n'ont pas été encore effectués (par défaut 15 jours)"))
    voiture = models.ForeignKey(Voiture)


class Revision(models.Model):
    """Représente une révision d'une voiture"""
    voiture = models.ForeignKey(Voiture)
    date = models.DateField(verbose_name=_('Date'))
    kilometrage = models.IntegerField(verbose_name=_("Nombre de Km lors de la révision"))


class Operation(models.Model):
    """Représente une opération unitaire"""
    type = models.ForeignKey(TypeOperation, verbose_name=_('Type'))
    revision = models.ForeignKey(Revision, verbose_name=_('Révision'))
    prix = models.DecimalField(null=True, decimal_places=2, max_digits=8, verbose_name=_("Prix"))
    effectue_par_garage = models.BooleanField(default=True, verbose_name=_("Effectué par un garage ?"))
    effectue = models.BooleanField(default=False, verbose_name=_('Effectué ?'),
                                   help_text=_("Est décoché si l'opération de maintenance n'a pas encore été effectué"))


class ChampSupplementaireValeur(models.Model):
    """Représente la valeur d'un champ supplémentaire pour une opération donnée"""
    champ = models.ForeignKey(ChampSupplementaire)
    operation = models.ForeignKey(Operation)
    valeur = models.CharField(max_length=256)
