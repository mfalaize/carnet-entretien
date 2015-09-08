from datetime import datetime

from carnet.models import Voiture, OperationMaintenance
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand


def check_entretien():
    """
    Check le programme d'entretien de chaque voiture sauvegardé en base et envoi un mail aux propriétaires concernés
    lorsque cela est nécessaire.
    """
    voitures = Voiture.objects.all()
    for voiture in voitures:
        need_to_send_mail = False
        corps_mail = "<ul>"
        kilometrage = voiture.kilometrage
        # Si la date de mise à jour du kilométrage n'est pas la date du jour on l'ajuste avec l'estimation du kilométrage
        # annuel
        if voiture.date_derniere_maj_km < datetime.now().date():
            nb_jours = datetime.now().date() - voiture.date_derniere_maj_km
            estimation_km = voiture.moyenne_km_annuel / 365 * nb_jours.days
            kilometrage += estimation_km

        programmes = voiture.modele.programme_maintenance.all()
        effectues = voiture.operationmaintenance_set.all()
        for programme in programmes:
            dernier_kilometrage = 0
            derniere_date = voiture.date_mise_circulation

            # On cherche le dernier kilométrage et la dernière date de l'opération en question effectuée
            for effectue in effectues:
                if effectue.type == programme:
                    if derniere_date < effectue.date:
                        derniere_date = effectue.date
                        dernier_kilometrage = effectue.kilometrage

            # A ce stade, on a toutes les infos pour comparer les dates et le kilométrage au programme de maintenance
            new_date = derniere_date + relativedelta(years=programme.periodicite.nb_annees)
            new_kilometrage = dernier_kilometrage + programme.periodicite.nb_kilometres

            date_nok = False
            if programme.periodicite.nb_annees != -1:
                date_nok = new_date <= datetime.now().date()

            km_nok = False
            if programme.periodicite.nb_kilometres != -1:
                km_nok = new_kilometrage <= kilometrage

            # FIXME Ajouter la possibilité de prévoir une maintenance proche de l'échéance
            if date_nok or km_nok:
                need_to_send_mail = True
                corps_mail += "<li><strong>{}</strong> ({} - Dernière date : {}, {} Km)</li>".format(
                    programme.nom, programme.periodicite.nom, derniere_date.strftime('%d/%m/%Y'), dernier_kilometrage)
                # On ajoute l'opération dans la liste des opérations à effectuer pour la voiture afin d'éviter d'envoyer
                # un mail à chaque déclenchement du script
                operation = OperationMaintenance()
                operation.voiture = voiture
                operation.date = datetime.now().date()
                operation.effectue = False
                operation.kilometrage = kilometrage
                operation.type = programme
                operation.save()

        if need_to_send_mail:
            corps_mail += "</ui>"
            send_mail('[{}] Entretien à effectuer'.format(voiture.modele.nom), "",
                      settings.DEFAULT_FROM_EMAIL, [voiture.proprietaire.email], html_message=corps_mail)


class Command(BaseCommand):
    help = 'Déclenche le script d\'entretien qui envoi des mails lorsque des opérations de maintenance sont à effectuer'

    def handle(self, *args, **options):
        check_entretien()
