from django.conf import settings
from django.db import models


class Periodicite(models.Model):
    nom = models.CharField(max_length=128)
    nb_kilometres = models.IntegerField(help_text='Nombre de Km d\'intervalle pour la périodicite')
    nb_annees = models.IntegerField(help_text='Nombre d\'années d\'intervalle pour la périodicite')

    def __str__(self):
        return self.nom


class TypeMaintenance(models.Model):
    nom = models.CharField(max_length=256)
    periodicite = models.ForeignKey(Periodicite)
    difficulte = models.IntegerField()
    confier_specialiste = models.BooleanField(default=False)

    def __str__(self):
        return '{} ({})'.format(self.nom, self.periodicite.nom)


class ModeleVoiture(models.Model):
    nom = models.CharField(max_length=256, help_text='Nom du modèle de voiture (ex : RENAULT Mégane II 1.5 dCi 86cv)')
    programme_maintenance = models.ManyToManyField(TypeMaintenance)

    def __str__(self):
        return self.nom


class Voiture(models.Model):
    nom = models.CharField(max_length=256, help_text='Nom de la voiture (ex : Voiture de Maxime)')
    immatriculation = models.CharField(max_length=16)
    modele = models.ForeignKey(ModeleVoiture)
    kilometrage = models.IntegerField(help_text='Nombre de Km au compteur')
    date_mise_circulation = models.DateField(help_text='Date de mise en circulation')
    moyenne_km_annuel = models.IntegerField(help_text='Nombre de Km effectué annuellement par la voiture')
    date_derniere_maj_km = models.DateField(help_text='Date de dernière mise à jour du kilométrage')
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.nom + ' (' + self.modele.nom + ')'


class OperationMaintenance(models.Model):
    type = models.ForeignKey(TypeMaintenance)
    voiture = models.ForeignKey(Voiture)
    kilometrage = models.IntegerField(help_text='Nombre de Km lors de l\'opération de maintenance')
    date = models.DateField()
    effectue = models.BooleanField(default=False,
                                   help_text='Est décoché si l\'opération de maintenance n\'a pas encore été effectué')

    def __str__(self):
        operation = '{} du {}'.format(self.type.nom, self.date.strftime('%d/%m/%Y'))
        if not self.effectue:
            operation += ' (à planifier)'
        return operation
