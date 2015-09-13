from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_image_user_path(instance, filename):
    """
    Utilisé par le modèle Voiture
    """
    user = instance.proprietaire
    return 'img/%s/%s' % (user.username, filename)


class Periodicite(models.Model):
    nom = models.CharField(max_length=128)
    nb_kilometres = models.IntegerField(verbose_name=_("Nombre de Km d'intervalle pour la périodicite"))
    nb_annees = models.IntegerField(verbose_name=_("Nombre d'années d'intervalle pour la périodicite"))

    def __str__(self):
        return self.nom


class TypeMaintenance(models.Model):
    nom = models.CharField(max_length=256)
    periodicite = models.ForeignKey(Periodicite)
    difficulte = models.IntegerField()
    confier_specialiste = models.BooleanField(default=False)

    def __str__(self):
        return '%s (%s)' % (self.nom, self.periodicite.nom)


class Voiture(models.Model):
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
    programme_maintenance = models.ManyToManyField(TypeMaintenance, verbose_name=_('Programme de maintenance'))

    def __str__(self):
        return self.nom + ' (' + self.modele.nom + ')'


class OperationMaintenance(models.Model):
    type = models.ForeignKey(TypeMaintenance, verbose_name=_('Type'))
    voiture = models.ForeignKey(Voiture, verbose_name=_('Voiture'))
    kilometrage = models.IntegerField(verbose_name=_("Nombre de Km lors de l'opération de maintenance"))
    date = models.DateField(verbose_name=_('Date'))
    effectue = models.BooleanField(default=False, verbose_name=_('Effectué ?'),
                                   help_text=_("Est décoché si l'opération de maintenance n'a pas encore été effectué"))

    def __str__(self):
        operation = _('%(nom)s du %(date)s') % {'nom': self.type.nom, 'date': self.date.strftime('%d/%m/%Y')}
        if not self.effectue:
            operation += '' + _('(à planifier)')
        return operation
