import os
import tempfile
from typing import List

import ezodf
import requests
import shutil

from decimal import Decimal
from django.conf import settings

import assmat
from assmat.models import BulletinSalaire, JourTravail


def fill_with_ods_template(bulletin: BulletinSalaire, jours: List[JourTravail]) -> BulletinSalaire:
    ods = ezodf.opendoc(os.path.join(os.path.dirname(assmat.__file__), 'media', 'template.ods'))
    sheet = SheetWrapper(ods.sheets[0])  # onglet Identification
    sheet['H3'].set_value(bulletin.contrat.nom_prenom_employeur)
    sheet['H4'].set_value(bulletin.contrat.adresse_1_employeur)
    sheet['H5'].set_value(bulletin.contrat.adresse_2_employeur)
    sheet['H6'].set_value(bulletin.contrat.code_postal_employeur)
    sheet['H7'].set_value(bulletin.contrat.ville_employeur)
    sheet['L8'].set_value(bulletin.contrat.numero_immatriculation_urssaf_employeur)
    sheet['I9'].set_value(bulletin.contrat.numero_pajemploi_employeur)
    sheet['F10'].set_value(bulletin.contrat.urssaf_de_employeur)
    sheet['H13'].set_value(bulletin.contrat.date_debut_contrat, value_type='date')
    sheet['K14'].set_value(bulletin.contrat.nom_prenom_enfant)
    sheet['I17'].set_value(bulletin.contrat.nom_prenom_salarie)
    sheet['I18'].set_value(bulletin.contrat.adresse_1_salarie)
    sheet['I19'].set_value(bulletin.contrat.adresse_2_salarie)
    sheet['I20'].set_value(bulletin.contrat.code_postal_salarie)
    sheet['I21'].set_value(bulletin.contrat.ville_salarie)
    sheet['I22'].set_value(bulletin.contrat.numero_securite_sociale_salarie)
    if bulletin.contrat.haut_rhin_bas_rhin_moselle:
        sheet['BC19'].set_value('OUI')
    else:
        sheet['BC19'].set_value('NON')

    sheet = SheetWrapper(ods.sheets[2])  # onglet Bulletin de salaire
    sheet['L4'].set_value(bulletin.date_debut, value_type='date')
    sheet['AK4'].set_value(bulletin.date_fin, value_type='date')
    sheet['L20'].set_value(bulletin.contrat.nb_semaines_programmees, value_type='float')
    sheet['W20'].set_value(bulletin.contrat.nb_heures_semaine, value_type='float')
    sheet['L22'].set_value(bulletin.contrat.nb_heures_accueil_jour, value_type='float')
    sheet['AR22'].set_value(bulletin.nb_semaines_travailles_mois, value_type='float')
    sheet['AW22'].set_value(bulletin.cumul_nb_semaines_travaillees, value_type='float')
    sheet['U29'].set_value(bulletin.contrat.remuneration_horaire_brute, value_type='float')
    sheet['N30'].set_value(bulletin.contrat.majoration_heures_supps_contractuelles / 100, value_type='percentage')
    sheet['Q30'].set_value(bulletin.contrat.nb_heures_supps_contractuelles_mois, value_type='float')
    sheet['N32'].set_value(bulletin.contrat.majoration_heures_supps_non_contractuelles / 100, value_type='percentage')
    sheet['N33'].set_value(bulletin.contrat.majoration_heures_complementaires / 100, value_type='percentage')
    # TODO ajouter indemnités congés payés Q34 et U34
    # TODO ajouter indemnités compensatrices congés payés Q35 et U35
    # TODO ajouter absence du salarié Q36 et U36
    # TODO ajouter justifiée de l'enfant Q37 et U37
    sheet['U73'].set_value(bulletin.contrat.indemnite_entretien, value_type='float')
    # TODO ajouter nombre d'heures indemnités entretien heures supp Q75
    sheet['U75'].set_value(bulletin.contrat.indemnite_entretien_heures_supps, value_type='float')
    sheet['Q81'].set_value(len([x for x in jours if x.repas]), value_type='float')
    sheet['U81'].set_value(bulletin.contrat.indemnite_repas, value_type='float')
    sheet['Q83'].set_value(len([x for x in jours if x.gouter]), value_type='float')
    sheet['U83'].set_value(bulletin.contrat.indemnite_gouter, value_type='float')
    # TODO indemnités déplacement Q87 et U87
    if bulletin.indemnite_rupture > 0:
        sheet['Y91'].set_value(bulletin.indemnite_rupture, value_type='float')
    sheet['U100'].set_value(bulletin.date_paiement, value_type='date')
    sheet['K104'].set_value(bulletin.numero_cheque_virement)
    sheet['T104'].set_value(bulletin.contrat.banque_employeur)
    sheet['AH87'].set_value(bulletin.commentaire)
    sheet['AU102'].set_value(bulletin.nb_jours_plus_8h, value_type='float')
    sheet['AT104'].set_value(bulletin.cumul_nb_jours_plus_8h, value_type='float')
    sheet['AU108'].set_value(bulletin.nb_jours_moins_8h, value_type='float')
    sheet['AT110'].set_value(bulletin.cumul_nb_jours_moins_8h, value_type='float')
    sheet['O120'].set_value(bulletin.cp_nb_semaines_travailles, value_type='float')
    sheet['AB119'].set_value(bulletin.cp_nb_jours_enfants, value_type='float')
    sheet['AN119'].set_value(bulletin.cp_nb_fractionnement, value_type='float')
    sheet['AS119'].set_value(bulletin.cp_nb_pris, value_type='float')
    sheet['O123'].set_value(bulletin.cp1_nb_semaines_travailles, value_type='float')
    sheet['AB122'].set_value(bulletin.cp1_nb_jours_enfants, value_type='float')
    sheet['AN122'].set_value(bulletin.cp1_nb_fractionnement, value_type='float')
    sheet['AS122'].set_value(bulletin.cp1_nb_pris, value_type='float')

    # Remplissage des jours
    row = 29
    for jour in jours:
        if jour.type == 'T':
            sheet['AP' + str(row)].set_value(jour.heures_effectuees, value_type='float')
            if jour.heures_complementaires > 0:
                sheet['AS' + str(row)].set_value(jour.heures_complementaires, value_type='float')
            if jour.heures_supplementaires > 0:
                sheet['AW' + str(row)].set_value(jour.heures_supplementaires, value_type='float')
            sheet['AV' + str(row)].set_value(1)

        elif jour.type != 'NT':
            sheet['AP' + str(row)].set_value(jour.type)
        row += 1

    # On sauvegarde le fichier dans un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(suffix='.ods', delete=True)
    ods.saveas(temp_file.name)

    # Une fois que tout est remplis on recalcule les formules du fichier en utilisant un webservice
    res = requests.post(settings.LIBREOFFICE_URL_WS + '/ods/calculate_all', files={'file': open(temp_file.name, 'rb')},
                        stream=True)

    if res is not None:
        if res.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(suffix='.ods', delete=True)
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, temp_file)

            # Enfin on copie les données manquantes calculées par l'ODS
            ods = ezodf.opendoc(temp_file.name)
            sheet = ods.sheets[2]
            bulletin.net_a_payer = Decimal(sheet['I100'].value)
            bulletin.net_imposable = Decimal(sheet['AB113'].value)

    return bulletin


class SheetWrapper(object):
    def __init__(self, sheet):
        super().__init__()
        self.sheet = sheet

    def __getitem__(self, key):
        return CellWrapper(self.sheet.__getitem__(key))


class CellWrapper(object):
    def __init__(self, cell):
        super().__init__()
        self.cell = cell

    def set_value(self, value, value_type=None, currency=None):
        if value is None:
            value = ''
        self.cell.set_value(value, value_type, currency)