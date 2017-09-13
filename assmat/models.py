from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _


# Create your models here.
class Contrat(models.Model):
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Utilisateurs"))
    nom_prenom_employeur = models.CharField(max_length=256, verbose_name=_("Employeur : Nom et Prénom"))
    adresse_1_employeur = models.CharField(max_length=256, verbose_name=_("Employeur : Adresse 1"))
    adresse_2_employeur = models.CharField(max_length=256, verbose_name=_("Employeur : Adresse 2"), null=True, blank=True)
    code_postal_employeur = models.CharField(max_length=6, verbose_name=_("Employeur : Code postal"))
    ville_employeur = models.CharField(max_length=128, verbose_name=_("Employeur : Ville"))
    numero_immatriculation_urssaf_employeur = models.CharField(max_length=128, verbose_name=_(
        "Employeur : N° d'immatriculation URSSAF"), null=True, blank=True)
    numero_pajemploi_employeur = models.CharField(max_length=128, verbose_name=_("Employeur : N° PAJEMPLOI"), null=True, blank=True)
    urssaf_de_employeur = models.CharField(max_length=128, verbose_name=_("Employeur : URSSAF de"), null=True, blank=True)
    banque_employeur = models.CharField(max_length=128, verbose_name=_("Employeur : Banque"))
    jour_paiement = models.IntegerField(verbose_name=_("Jour de paiement du salaire dans le mois"))
    date_debut_contrat = models.DateField(verbose_name=_("Date début du contrat"))
    date_fin_contrat = models.DateField(verbose_name=_("Date fin du contrat"), null=True, blank=True)
    nom_prenom_enfant = models.CharField(max_length=256, verbose_name=_("Nom et Prénom de l'enfant"))
    haut_rhin_bas_rhin_moselle = models.BooleanField(default=False, verbose_name=_(
        "L'ass mat réside en Haut Rhin - Bas Rhin - Moselle"))
    nom_prenom_salarie = models.CharField(max_length=256, verbose_name=_("Salarié : Nom et Prénom"))
    adresse_1_salarie = models.CharField(max_length=256, verbose_name=_("Salarié : Adresse 1"))
    adresse_2_salarie = models.CharField(max_length=256, verbose_name=_("Salarié : Adresse 2"), null=True, blank=True)
    code_postal_salarie = models.CharField(max_length=6, verbose_name=_("Salarié : Code postal"))
    ville_salarie = models.CharField(max_length=128, verbose_name=_("Salarié : Ville"))
    numero_securite_sociale_salarie = models.CharField(max_length=15, verbose_name=_("Salarié : N° Sécurité Sociale"))
    nb_semaines_programmees = models.DecimalField(max_digits=4, decimal_places=2,
                                                  verbose_name=_("Nombre de semaines programmées"))
    nb_heures_semaine = models.DecimalField(max_digits=4, decimal_places=2,
                                            verbose_name=_("Nombre d'heures par semaine"))
    nb_heures_supps_contractuelles_mois = models.DecimalField(default=0, max_digits=4, decimal_places=2,
                                                              verbose_name=_(
                                                                  "Nombre d'heures supplémentaires contractuelles par mois"))
    nb_heures_accueil_jour = models.DecimalField(max_digits=4, decimal_places=2,
                                                 verbose_name=_("Nombre d'heures d'accueil par jour"))
    remuneration_horaire_brute = models.DecimalField(max_digits=4, decimal_places=2,
                                                     verbose_name=_("Rémunération horaire brute"))
    majoration_heures_supps_contractuelles = models.DecimalField(default=100, max_digits=5, decimal_places=2, verbose_name=_(
        "Majoration des heures supplémentaires contractuelles"))
    majoration_heures_supps_non_contractuelles = models.DecimalField(default=100, max_digits=5, decimal_places=2, verbose_name=_(
        "Majoration des heures supplémentaires non contractuelles"))
    majoration_heures_complementaires = models.DecimalField(default=0, max_digits=5, decimal_places=2,
                                                            verbose_name=_("Majoration des heures complémentaires"))
    indemnite_entretien = models.DecimalField(default=0, max_digits=4, decimal_places=2, verbose_name=_("Indemnité d'entretien"))
    indemnite_entretien_heures_supps = models.DecimalField(default=0, max_digits=4, decimal_places=2, verbose_name=_(
        "Indemnité d'entretien par heure supplémentaire"))
    indemnite_repas = models.DecimalField(default=0, max_digits=4, decimal_places=2, verbose_name=_("Indemnité de repas"))
    indemnite_gouter = models.DecimalField(default=0, max_digits=4, decimal_places=2, verbose_name=_("Indemnité de goûter"))
    indemnite_km = models.DecimalField(default=0, max_digits=4, decimal_places=2,
                                       verbose_name=_("Indemnité de déplacement kilométrique"))
    jours_normalement_travailles = models.PositiveIntegerField(default=int(0b1111100), verbose_name=_("Jours de la semaine normalement travaillés"))


def repertoire_upload_bulletin_salaire_pdf(instance, filename):
    return "{0}/assmat/bs/{1}".format(instance.contrat.utilisateurs.pk, filename)


class BulletinSalaire(models.Model):
    contrat = models.ForeignKey(Contrat, verbose_name=_("Contrat"))
    date_debut = models.DateField(verbose_name=_("Date début"))
    date_fin = models.DateField(verbose_name=_("Date fin"))
    accomptes_verses = models.DecimalField(default=0, max_digits=6, decimal_places=2,
                                           verbose_name=_("Accomptes versés dans le mois"))
    nb_km = models.DecimalField(default=0, max_digits=6, decimal_places=2,
                                verbose_name=_("Nombre de km pour l'indemnité de déplacement"))
    indemnite_rupture = models.DecimalField(default=0, max_digits=6, decimal_places=2,
                                            verbose_name=_("Indemnités de rupture ou de licenciement"))
    commentaire = models.CharField(max_length=1024, verbose_name=_("Commentaire"), null=True, blank=True)
    cp_nb_mois_travailles = models.IntegerField(default=0, verbose_name=_("CP (N) : Nombre de mois travaillés"))
    cp_nb_semaines_travailles = models.IntegerField(default=0, verbose_name=_("CP (N) : Nombre de semaines travaillées"))
    cp_nb_jours_enfants = models.IntegerField(default=0, verbose_name=_("CP (N) : Nombre de jours enfants de - de 15 ans"))
    cp_nb_fractionnement = models.IntegerField(default=0, verbose_name=_("CP (N) : Nombre de jours de fractionnement"))
    cp_nb_pris = models.IntegerField(default=0, verbose_name=_("CP (N) : Nombre de jours pris"))
    cp1_nb_mois_travailles = models.IntegerField(default=0, verbose_name=_("CP (N-1) : Nombre de mois travaillés"))
    cp1_nb_semaines_travailles = models.IntegerField(default=0, verbose_name=_("CP (N-1) : Nombre de semaines travaillées"))
    cp1_nb_jours_enfants = models.IntegerField(default=0, verbose_name=_("CP (N-1) : Nombre de jours enfants de - de 15 ans"))
    cp1_nb_fractionnement = models.IntegerField(default=0, verbose_name=_("CP (N-1) : Nombre de jours de fractionnement"))
    cp1_nb_pris = models.IntegerField(default=0, verbose_name=_("CP (N-1) : Nombre de jours pris"))
    net_a_payer = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Net à payer"))
    net_imposable = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Net imposable"))
    cumul_net_imposable = models.DecimalField(max_digits=7, decimal_places=2,
                                              verbose_name=_("Cumul annuel net imposable"))
    date_paiement = models.DateField(verbose_name=_("Date de paiement"))
    numero_cheque_virement = models.CharField(max_length=256, verbose_name=_("Numéro du chèque ou virement"), null=True, blank=True)
    cumul_nb_semaines_travaillees = models.IntegerField(
        verbose_name=_("Nombre de semaines travaillées depuis le 1er janvier"))
    cumul_nb_jours_plus_8h = models.IntegerField(
        verbose_name=_("Cumul annuel du nombre de jours travaillés de 8h et plus"))
    cumul_nb_jours_moins_8h = models.IntegerField(
        verbose_name=_("Cumul annuel du nombre de jours travaillés de moins de 8h"))
    pdf = models.FileField(upload_to=repertoire_upload_bulletin_salaire_pdf, verbose_name=_("Fichier PDF"), null=True)


class JourTravail(models.Model):
    CHOIX_TYPES = (
        ("T", "Travaillé"),
        ("NT", "Non Travaillé (week end)"),
        ("A.A.M.S.S.", "Absence Ass.Mat.Sans Solde"),
        ("A.J.E.", "Absence justifiée Enfant"),
        ("A.I.E.", "Absence injustifiée Enfant"),
        ("C.S.S.", "Congés sans solde"),
        ("C.P.", "Congés payés"),
        ("S.D.A.M.", "Semaine déduite Parents Empl."),
        ("F.", "Jour Férié chomé payé"),
    )
    bulletin_salaire = models.ForeignKey(BulletinSalaire, verbose_name=_("Bulletin de salaire"))
    date = models.DateField(verbose_name=_("Date"))
    heures_effectuees = models.DecimalField(max_digits=4, decimal_places=2,
                                           verbose_name=_("Heures effectuées (hors complémentaires/supps)"))
    heures_complementaires = models.DecimalField(default=0, max_digits=4, decimal_places=2,
                                                 verbose_name=_("Heures complémentaires"))
    heures_supplementaires = models.DecimalField(default=0, max_digits=4, decimal_places=2,
                                                 verbose_name=_("Heures supplémentaires"))
    type = models.CharField(max_length=64, choices=CHOIX_TYPES, verbose_name=_("Type"))
    repas = models.BooleanField(default=False, verbose_name=_("L'enfant a eu un repas"))
    gouter = models.BooleanField(default=False, verbose_name=_("L'enfant a eu un goûter"))
