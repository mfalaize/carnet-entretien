import decimal
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand

from compta.bank import get_bank_class
from compta.models import Compte, Epargne, OperationEpargne


def check_operations():
    """Récupère les dernières opérations bancaires en ligne, inscrit les nouvelles en base et les envoie par mail"""
    comptes = Compte.objects.all()
    for compte in comptes:
        epargnes = Epargne.objects.filter(utilisateurs__in=compte.utilisateurs.all())
        operations = compte.operation_set.all()
        bank_class = get_bank_class(compte.identifiant.banque)
        has_changed = False

        with bank_class(compte.identifiant.login, compte.identifiant.mot_de_passe, compte.numero_compte) as bank:
            new_operations = bank.fetch_last_operations()
            new_solde = bank.fetch_balance()

        for new_operation in new_operations:
            found = False
            for operation in operations:
                if operation.date_operation == new_operation.date_operation and operation.libelle == new_operation.libelle:
                    found = True
                    break
            if not found:
                new_operation.compte = compte
                new_operation.save()

                if compte.epargne:
                    if new_operation.montant >= 0:
                        for epargne in epargnes:
                            new_operation.categorie_id = 18  # = Hors Budget
                            new_operation.save()

                            op = OperationEpargne()
                            op.epargne = epargne
                            op.montant = decimal.Decimal(new_operation.montant * epargne.pourcentage_alloue / 100)
                            op.operation = new_operation
                            op.save()

                            epargne.solde += op.montant
                            epargne.save()
                    else:
                        op = OperationEpargne()
                        op.montant = new_operation.montant
                        op.operation = new_operation
                        op.save()
                        has_changed = True
                else:
                    has_changed = True

        if compte.solde != new_solde:
            compte.solde = new_solde
            compte.save()

        if has_changed:
            mails = []
            for user in compte.utilisateurs.all():
                if user.email is not None:
                    mails.append(user.email)
            if len(mails) > 0:
                send_mail(
                    '[Homelab] De nouvelles opérations sont à catégoriser sur {}'.format(str(compte)),
                    "",
                    settings.DEFAULT_FROM_EMAIL, mails)


class Command(BaseCommand):
    help = "Déclenche le script qui vérifie les nouvelles opérations bancaires et qui envoie des mails lorsqu'il y en a des nouvelles"

    def handle(self, *args, **options):
        check_operations()
