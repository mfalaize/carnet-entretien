from django.utils import timezone
from django.utils.formats import localize
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class VoitureManager(models.Manager):
    """Manager pour le modèle Voiture"""

    def get_voitures_for_user(self, user):
        """Récupère les voitures de l'utilisateur"""
        return self.filter(proprietaire=user)


class OperationManager(models.Manager):
    """Manager pour le modèle Operation"""

    def get_all_dernieres_operations(self, voitures=None, user=None):
        """Récupère la liste des dernières opérations pour les voitures de l'utilisateur. Cette liste est triée dans
        un premier temps par opérations effectués ou non (les opérations non effectuées sortant en premier) puis par
        date de révision"""
        if voitures is None:
            if user is None:
                raise Exception("L'un des deux paramètres voitures ou user doit être renseigné")
            voitures = Voiture.objects.get_voitures_for_user(user)
        return self.filter(revision__voiture__in=voitures).order_by('effectue', '-revision__date')

    def get_operations_a_prevoir(self, voiture):
        """Récupère la liste des opérations à prévoir pour la voiture en paramètre triée par date"""
        return self.filter(revision__voiture=voiture, effectue=False).order_by('-revision__date')

    def get_dernieres_operations(self, voiture):
        """Récupère la liste des dernières opérations effectuées pour la voiture en paramètre. La liste est triée par
        date"""
        return self.filter(revision__voiture=voiture, effectue=True).order_by('-revision__date')


class ProgrammeMaintenanceManager(models.Manager):
    """Manager pour le modèle ProgrammeMaintenance"""

    def get_programmes_for_voiture(self, voiture=None, voiture_pk=None, user=None):
        """Récupère tous les programmes de maintenance pour la voiture en paramètre. La liste est triée par périodicité"""
        if voiture is None:
            if voiture_pk is None or user is None:
                raise Exception(
                    "Les deux paramètres voiture_pk et user doivent être renseignés lorsque voiture est null")
            queryset = self.filter(voiture__pk=voiture_pk, voiture__proprietaire=user)
        else:
            queryset = self.filter(voiture=voiture)

        return queryset.order_by('periodicite_kilometres', 'periodicite_annees')


def get_image_user_path(instance, filename):
    """Utilisé par le modèle Voiture"""
    user = instance.proprietaire
    return 'img/%s/%s' % (user.username, filename)


class ChampSupplementaire(models.Model):
    """Représente un champ supplémentaire spécifique pour un type d'opération"""
    libelle = models.CharField(max_length=128)

    def __str__(self):
        return self.libelle


class TypeOperation(models.Model):
    """Représente un type d'opération unitaire à effectuer sur une voiture"""
    nom = models.CharField(max_length=256)
    champs_supplementaires = models.ManyToManyField(ChampSupplementaire, blank=True)

    def __str__(self):
        return self.nom


class Voiture(models.Model):
    """Représente une voiture"""
    objects = VoitureManager()
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
    prix_achat = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10,
                                     verbose_name=_("Prix d'achat"))
    date_achat = models.DateField(null=True, blank=True, verbose_name=_("Date d'achat"))
    kilometrage_achat = models.IntegerField(null=True, blank=True, verbose_name="Nombre de Km à l'achat")

    def get_estimation_kilometrage(self):
        """Calcule une estimation du kilométrage actuel à l'aide du dernier kilométrage renseigné, de la moyenne annuelle
        renseignée au prorata du nombre de jours qui sépare la date du jour de la date de dernière mise à jour du
        kilométrage"""
        if self.date_derniere_maj_km < timezone.now().date():
            nb_jours = timezone.now().date() - self.date_derniere_maj_km
            estimation_km = self.moyenne_km_annuel / 365 * nb_jours.days
            return self.kilometrage + round(estimation_km)
        return self.kilometrage


class ProgrammeMaintenance(models.Model):
    """Représente une liste d'opérations pour un programme de maintenance pour une voiture"""
    objects = ProgrammeMaintenanceManager()
    types_operations = models.ManyToManyField(TypeOperation, verbose_name=_("Opérations du programme"))
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

    def get_periodicite(self):
        """Génère le libellé pour la périodicité (années + km si renseignés)"""
        if self.periodicite_kilometres is not None:
            if self.periodicite_annees is not None:
                return _("Tous les %(kilometres)s Km / %(annees)s an(s)") % {
                    'kilometres': localize(self.periodicite_kilometres, True),
                    'annees': self.periodicite_annees}
            return _("Tous les %(kilometres)s Km") % {
                'kilometres': localize(self.periodicite_kilometres, True)}
        elif self.periodicite_annees is not None:
            return _("Tous les %(annees)s an(s)") % {'annees': self.periodicite_annees}
        return None


class Revision(models.Model):
    """Représente une révision d'une voiture"""
    voiture = models.ForeignKey(Voiture)
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    kilometrage = models.IntegerField(verbose_name=_("Nombre de Km lors de la révision"))


class Operation(models.Model):
    """Représente une opération unitaire"""
    objects = OperationManager()
    type = models.ForeignKey(TypeOperation, verbose_name=_('Type'))
    revision = models.ForeignKey(Revision, verbose_name=_('Révision'))
    prix = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=8, verbose_name=_("Prix"))
    effectue_par_garage = models.BooleanField(default=True, verbose_name=_("Effectué par un garage ?"))
    effectue = models.BooleanField(default=False, verbose_name=_('Effectué ?'),
                                   help_text=_("Est décoché si l'opération de maintenance n'a pas encore été effectué"))


class ChampSupplementaireValeur(models.Model):
    """Représente la valeur d'un champ supplémentaire pour une opération donnée"""
    champ = models.ForeignKey(ChampSupplementaire)
    operation = models.ForeignKey(Operation)
    valeur = models.CharField(max_length=256)
