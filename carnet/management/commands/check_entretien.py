from carnet.models import Voiture, Operation, Revision
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone


def check_entretien():
    """Check le programme d'entretien de chaque voiture sauvegardée en base et envoie un mail aux propriétaires concernés
    lorsque cela est nécessaire"""
    voitures = Voiture.objects.all()
    for voiture in voitures:
        need_to_send_mail = False
        revision_a_prevoir = None
        corps_mail = "<ul>"
        kilometrage = voiture.get_estimation_kilometrage()

        programmes = voiture.programmemaintenance_set.all()
        revisions = voiture.revision_set.all()
        for programme in programmes:
            for prog_operation in programme.types_operations.all():
                dernier_prix = None
                dernier_kilometrage = 0
                derniere_date = voiture.date_mise_circulation
                derniere_operation_effectue = False

                # On cherche le dernier kilométrage et la dernière date de l'opération en question effectuée
                for revision in revisions:
                    for effectue in revision.operation_set.all():
                        if effectue.type in prog_operation:
                            if derniere_date < revision.date:
                                derniere_date = revision.date
                                dernier_kilometrage = revision.kilometrage
                                derniere_operation_effectue = effectue.effectue
                                if effectue.prix is not None:
                                    dernier_prix = effectue.prix

                # A ce stade, on a toutes les infos pour comparer les dates et le kilométrage au programme de maintenance
                date_nok = False
                if programme.periodicite_annees is not None:
                    new_date = derniere_date + relativedelta(years=programme.periodicite_annees)
                    date_nok = new_date <= (timezone.now().date() - relativedelta(day=programme.delai_alerte))

                km_nok = False
                if programme.periodicite_kilometres is not None:
                    new_kilometrage = dernier_kilometrage + programme.periodicite_kilometres
                    # On calcule un kilométrage différent en fonction du délai d'alerte paramétré
                    estimation_km_delai = 0
                    if programme.delai_alerte != 0:
                        estimation_km_delai = voiture.moyenne_km_annuel / 365 * programme.delai_alerte
                    km_nok = new_kilometrage <= (kilometrage - estimation_km_delai)

                rappel_nok = False
                if not derniere_operation_effectue:
                    new_date = derniere_date + relativedelta(day=programme.delai_rappel)
                    rappel_nok = new_date <= timezone.now().date()

                if date_nok or km_nok or rappel_nok:
                    need_to_send_mail = True
                    corps_mail += "<li><strong>{}</strong> ({} - Dernière date : {}, {} Km, {}€)</li>".format(
                        prog_operation.nom, programme, derniere_date.strftime('%d/%m/%Y'),
                        dernier_kilometrage, dernier_prix if dernier_prix is not None else '?')

                    if not rappel_nok:
                        # On ajoute l'opération dans la liste des opérations à effectuer pour la voiture afin d'éviter
                        # d'envoyer un mail à chaque déclenchement du script
                        if revision_a_prevoir is None:
                            revision_a_prevoir = Revision()
                            revision_a_prevoir.voiture = voiture
                            revision_a_prevoir.date = timezone.now().date() + relativedelta(day=programme.delai_alerte)
                            revision_a_prevoir.kilometrage = kilometrage
                            revision_a_prevoir.save()

                        op = Operation()
                        op.revision = revision_a_prevoir
                        op.effectue = False
                        op.type = prog_operation
                        if dernier_prix is not None:
                            op.prix = dernier_prix
                        op.save()

        if need_to_send_mail:
            corps_mail += "</ui>"
            send_mail('[{}] Entretien à effectuer'.format(voiture.nom), "",
                      settings.DEFAULT_FROM_EMAIL, [voiture.proprietaire.email], html_message=corps_mail)


class Command(BaseCommand):
    help = "Déclenche le script d'entretien qui envoie des mails lorsque des opérations de maintenance sont à effectuer"

    def handle(self, *args, **options):
        check_entretien()
