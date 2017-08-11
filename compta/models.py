import base64
import datetime

from Crypto.Cipher import AES
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Categorie(models.Model):
    libelle = models.CharField(max_length=256, verbose_name=_('Libellé'))

    def __str__(self):
        return self.libelle


class Budget(models.Model):
    categorie = models.ForeignKey(Categorie, verbose_name=_('Catégorie'))
    budget = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Budget'))
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateurs"))
    solde_en_une_fois = models.BooleanField(default=False, verbose_name=_("Soldé en une fois"))

    def __str__(self):
        return self.categorie.libelle

    def calcule_solde(self, date=datetime.date.today()):
        """Calcule les propriétés solde et depenses de l'objet"""
        operations_mois_en_cours = Operation.objects.filter(compte__utilisateurs__in=self.utilisateurs.all(),
                                                            date_operation__month=date.month,
                                                            categorie_id=self.categorie_id)
        self.solde = self.budget
        self.depenses = 0
        for operation in operations_mois_en_cours:
            self.solde += operation.montant
            self.depenses -= operation.montant


class CategorieEpargne(models.Model):
    """Catégories spécifiques à l'épargne"""
    libelle = models.CharField(max_length=256, verbose_name=_("Libellé"))

    def __str__(self):
        return self.libelle


class Epargne(models.Model):
    """Sorte de compte virtuel qui permet d'allouer à une catégorie un solde disponible"""
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateurs"))
    solde = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Solde"))
    categorie = models.ForeignKey(CategorieEpargne, verbose_name=_("Catégorie"))
    pourcentage_alloue = models.IntegerField(verbose_name=_("Pourcentage des versements d'épargne alloué"))

    def __str__(self):
        return self.categorie.libelle


class Identifiant(models.Model):
    CREDIT_MUTUEL = "CM"
    CHOIX_BANQUES = (
        (CREDIT_MUTUEL, "Crédit Mutuel"),
    )
    banque = models.CharField(max_length=128, verbose_name=_("Banque"), choices=CHOIX_BANQUES)
    login = models.CharField(max_length=128, verbose_name=_("Login"))
    mot_de_passe = models.CharField(max_length=128, verbose_name=_("Mot de passe"))
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateur"))
    encrypted = models.BooleanField(default=False, verbose_name=_("Le mot de passe a été crypté"))

    def clean(self):
        super().clean()
        if not self.encrypted:
            obj = AES.new(settings.SECRET_KEY[:32])
            self.mot_de_passe = base64.b64encode(obj.encrypt(self.mot_de_passe)).decode()
            self.encrypted = True


class Compte(models.Model):
    identifiant = models.ForeignKey(Identifiant, verbose_name=_("Identifiant"), null=True)
    numero_compte = models.CharField(max_length=128, verbose_name=_("Numéro de compte"))
    libelle = models.CharField(max_length=128, verbose_name=_("Libellé"), null=True)
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateurs"))
    solde = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Solde"), null=True)
    epargne = models.BooleanField(default=False, verbose_name=_("Le compte est un compte d'épargne"))

    def __str__(self):
        if self.libelle is not None:
            return self.libelle
        return self.banque + " " + self.numero_compte


class Operation(models.Model):
    date_operation = models.DateField(verbose_name=_("Date d'opération"))
    date_valeur = models.DateField(verbose_name=_("Date de valeur"))
    montant = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Montant"))
    libelle = models.CharField(max_length=512, verbose_name=_("Libellé"))
    compte = models.ForeignKey(Compte, verbose_name=_("Compte"))
    categorie = models.ForeignKey(Categorie, verbose_name=_("Catégorie"), null=True)

    def __str__(self):
        return self.libelle


class OperationEpargne(models.Model):
    operation = models.ForeignKey(Operation, verbose_name=_("Opération réelle initiale"))
    epargne = models.ForeignKey(Epargne, verbose_name=_("Epargne"), null=True)
    montant = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Montant"))

    def __str__(self):
        return str(self.operation) + " " + str(self.epargne)
