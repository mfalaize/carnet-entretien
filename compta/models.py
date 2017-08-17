import base64
import datetime

from Crypto.Cipher import AES
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _


class Categorie(models.Model):
    libelle = models.CharField(max_length=256, verbose_name=_('Libellé'))

    def __str__(self):
        return self.libelle


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
    identifiant = models.ForeignKey(Identifiant, verbose_name=_("Identifiant"))
    numero_compte = models.CharField(max_length=128, verbose_name=_("Numéro de compte"))
    libelle = models.CharField(max_length=128, verbose_name=_("Libellé"), null=True, blank=True)
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateurs"))
    solde = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Solde"), null=True, blank=True)
    epargne = models.BooleanField(default=False, verbose_name=_("Le compte est un compte d'épargne"))

    def __str__(self):
        if self.libelle is not None:
            return self.libelle
        return self.banque + " " + self.numero_compte

    def calculer_parts(self, date=datetime.date.today()):
        """Remplis les propriétés total_budget, total_depenses, total_solde, total_salaire, total_part, total_a_verser, utilisateurs, budgets
        ainsi que les propriétés de chaque utilisateur du compte revenus_personnels, avances, part, a_verser et les propriétés de chaque
        budget depenses et solde"""
        self.budgets = Budget.objects.filter(compte_associe=self).order_by('categorie__libelle')
        self.utilisateurs_list = self.utilisateurs.all()

        self.total_budget = 0
        self.total_depenses = 0
        self.total_solde = 0
        self.total_contributions = 0
        self.total_part_contributions = 0
        self.total_avances = 0
        self.total_salaire = 0
        self.total_part = 0
        self.total_a_verser = 0

        for budget in self.budgets:
            budget.calcule_solde(date)
            self.total_budget += budget.budget
            self.total_depenses += budget.depenses
            self.total_solde += budget.solde

        if self.total_budget > 0:
            for utilisateur in self.utilisateurs_list:
                utilisateur.revenus_personnels = utilisateur.get_revenus_personnels(date)
                utilisateur.contributions = utilisateur.get_contributions(self)
                utilisateur.avances = utilisateur.get_avances(self, date)

                self.total_salaire += utilisateur.revenus_personnels
                self.total_contributions += utilisateur.contributions
                self.total_avances += utilisateur.avances

            if self.total_salaire > 0:
                for utilisateur in self.utilisateurs_list:
                    utilisateur.part = utilisateur.revenus_personnels / self.total_salaire
                    utilisateur.a_verser = utilisateur.part * (self.total_budget - self.solde) - utilisateur.avances
                    utilisateur.formule_calcule_a_verser = str(utilisateur.part) + ' [part utilisateur] x (' + str(self.total_budget) + ' [budget total] - ' + str(self.solde) + ' [solde du compte]) - ' + str(utilisateur.avances) + " [avances de l'utilisateur]"
                    if self.total_contributions > 0:
                        utilisateur.part_contribution = utilisateur.contributions / self.total_contributions
                        self.total_part_contributions += utilisateur.part_contribution

                    self.total_part += utilisateur.part
                    self.total_a_verser += utilisateur.a_verser


class Budget(models.Model):
    categorie = models.ForeignKey(Categorie, verbose_name=_('Catégorie'))
    budget = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Budget'))
    compte_associe = models.ForeignKey(Compte, verbose_name=_("Compte associé"))
    solde_en_une_fois = models.BooleanField(default=False, verbose_name=_("Soldé en une fois"))

    def __str__(self):
        return self.categorie.libelle

    def calcule_solde(self, date=datetime.date.today()):
        """Calcule les propriétés solde, operations et depenses de l'objet"""
        operations_mois_en_cours = Operation.objects.filter(compte_id=self.compte_associe.pk,
                                                            date_operation__month=date.month,
                                                            budget_id=self.pk)
        self.operations = operations_mois_en_cours
        self.solde = self.budget
        self.depenses = 0
        for operation in operations_mois_en_cours:
            self.solde += operation.montant
            self.depenses -= operation.montant


class Operation(models.Model):
    date_operation = models.DateField(verbose_name=_("Date d'opération"))
    date_valeur = models.DateField(verbose_name=_("Date de valeur"))
    montant = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Montant"))
    libelle = models.CharField(max_length=512, verbose_name=_("Libellé"))
    compte = models.ForeignKey(Compte, verbose_name=_("Compte"))
    budget = models.ForeignKey(Budget, verbose_name=_("Budget"), null=True, blank=True)
    hors_budget = models.BooleanField(default=False, verbose_name=_("Hors Budget"))
    recette = models.BooleanField(default=False, verbose_name=_("Recette"))
    contributeur = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Contributeur"), null=True, blank=True)
    avance = models.BooleanField(default=False, verbose_name=_("Avance"))

    def __str__(self):
        return self.libelle


class OperationEpargne(models.Model):
    operation = models.ForeignKey(Operation, verbose_name=_("Opération réelle initiale"))
    epargne = models.ForeignKey(Epargne, verbose_name=_("Epargne"), null=True, blank=True)
    montant = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Montant"))

    def __str__(self):
        return str(self.operation) + " " + str(self.epargne)


def get_revenus_personnels(utilisateur, date=datetime.date.today()):
    value = Operation.objects.filter(
        date_operation__month=date.month, recette=True,
        compte__utilisateurs=utilisateur).aggregate(
        revenus_personnels=Sum('montant'))['revenus_personnels']
    if value is None:
        return 0
    return value


def get_avances(utilisateur, compte, date=datetime.date.today()):
    value = Operation.objects.filter(
        date_operation__month=date.month, contributeur=utilisateur, avance=True,
        compte__utilisateurs=utilisateur, compte=compte).aggregate(
        avances=Sum('montant'))['avances']
    if value is None:
        return 0
    return value


def get_contributions(utilisateur, compte):
    value = Operation.objects.filter(
        contributeur=utilisateur,
        compte__utilisateurs=utilisateur, compte=compte).aggregate(
        contributions=Sum('montant'))['contributions']
    if value is None:
        return 0
    return value


UserModel = get_user_model()
UserModel.add_to_class('get_revenus_personnels', get_revenus_personnels)
UserModel.add_to_class('get_avances', get_avances)
UserModel.add_to_class('get_contributions', get_contributions)
