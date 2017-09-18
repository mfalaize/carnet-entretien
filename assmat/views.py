import calendar
import datetime
import locale

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from workalendar.europe import France

from assmat.forms import JourTravailForm
from assmat.models import JourTravail, Contrat, BulletinSalaire
from assmat.services import fill_with_ods_template


def test(request):
    # ods = ezodf.opendoc(os.path.join(os.path.dirname(assmat.__file__), 'media', 'template.ods'))
    # sheet = ods.sheets[2]
    # debut = date.today()
    # debut = debut.replace(month=11, day=1)
    # fin = date.today()
    # fin = fin.replace(month=11, day=30)
    # sheet['L4'].set_value(debut, value_type='date')
    # sheet['AK4'].set_value(fin, value_type='date')
    # sheet['Q33'].set_value(value=4)
    # ods.save()
    #
    # with open(os.path.join(settings.MEDIA_ROOT, 'template.pdf'), 'rb') as f:
    #     response = HttpResponse(f.read(), content_type='application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('template.pdf')
    #     return response

    raise Http404


@login_required
def valider(request):
    if request.method == 'POST':
        today = datetime.date.today()
        if request.POST and request.POST['mois'] and request.POST['annee']:
            today = today.replace(month=int(request.POST['mois']), year=int(request.POST['annee']))

        db_jours = list(JourTravail.objects.filter(date__month=today.month, date__year=today.year).order_by('date'))
        jours = []

        nb_jours_dans_mois = calendar.monthrange(today.year, today.month)[1]
        for day in range(1, nb_jours_dans_mois + 1):
            form = JourTravailForm(request.POST, prefix=str(day))
            form.instance.date = today.replace(day=day)
            if not form.is_valid():
                return HttpResponse(form.errors, 400)
            for jour in db_jours:
                if form.instance.date == jour.date:
                    form.instance.pk = jour.pk
                    break
            jours.append(form.instance)

        # Calcul des données du bulletin de salaire à partir des informations renseignées dans le contrat et les jours
        contrat = Contrat.objects.get(Q(date_debut_contrat__lte=today),
                                      Q(date_fin_contrat__gte=today) | Q(date_fin_contrat__isnull=True))

        bulletin = BulletinSalaire.objects.get(date_debut__year=today.year, date_debut__month=today.month)
        if bulletin is None:
            bulletin = BulletinSalaire()
        bulletin.contrat = contrat
        bulletin.date_debut = today.replace(day=1)
        bulletin.date_fin = today.replace(day=nb_jours_dans_mois)
        bulletin.date_paiement = today.replace(day=contrat.jour_paiement) + relativedelta(months=1)

        # Calcul des dates pour le calcul des congés payés (calcul des périodes N et N-1)
        n_debut = today.replace(day=1, month=6)
        n_fin = today.replace(day=31, month=5, year=today.year + 1)
        if today.month < 6:
            n_debut = n_debut.replace(year=n_debut.year - 1)
            n_fin = n_fin.replace(year=n_fin.year - 1)
        n1_debut = n_debut.replace(year=n_debut.year - 1)
        n1_fin = n_fin.replace(year=n_fin.year - 1)

        list_jours_annee = list(JourTravail.objects.filter(date__gte=n_debut, date__lte=n_fin))
        list_lundi_annee = []

        for date in rrule.rrule(rrule.WEEKLY, dtstart=n_debut, until=n_fin, byweekday=0):
            if len(list_lundi_annee) == 0 and date.day > 1:
                list_lundi_annee.append(
                    datetime.date(year=date.year, month=date.month, day=date.day) - datetime.timedelta(days=7))
            list_lundi_annee.append(datetime.date(year=date.year, month=date.month, day=date.day))

        # Calcul du nombre de semaines travaillées
        for lundi in list_lundi_annee:
            if len([x for x in list_jours_annee if
                    lundi <= x.date < (lundi + datetime.timedelta(days=7)) and x.type in ['T', 'A.I.E.', 'C.P.']]) > 0:
                bulletin.cp_nb_semaines_travailles += 1

        # Calcul du nombre de jours enfants
        if contrat.nb_enfants_moins_15_ans > 0:
            bulletin.cp_nb_jours_enfants += contrat.nb_enfants_moins_15_ans
            bulletin.cp1_nb_jours_enfants += contrat.nb_enfants_moins_15_ans

        # Calcul du nombre de congés pris
        bulletin.cp_nb_pris = len([x for x in list_jours_annee if x.type == 'C.P.'])

        list_jours_annee = list(JourTravail.objects.filter(date__gte=n1_debut, date__lte=n1_fin))
        list_lundi_annee = []

        for date in rrule.rrule(rrule.WEEKLY, dtstart=n1_debut, until=n1_fin, byweekday=0):
            if len(list_jours_annee) == 0 and date.day > 1:
                list_lundi_annee.append(
                    datetime.date(year=date.year, month=date.month, day=date.day) - datetime.timedelta(days=7))
            list_lundi_annee.append(datetime.date(year=date.year, month=date.month, day=date.day))

        for lundi in list_lundi_annee:
            if len([x for x in list_jours_annee if
                    lundi <= x.date < (lundi + datetime.timedelta(days=7)) and x.type in ['T', 'A.I.E.', 'C.P.']]) > 0:
                bulletin.cp1_nb_semaines_travailles += 1

        # Calcul du nombre de congés pris
        bulletin.cp1_nb_pris = len([x for x in list_jours_annee if x.type == 'C.P.'])

        bulletin.nb_jours_moins_8h = 0
        bulletin.nb_jours_plus_8h = 0
        for jour in jours:
            if jour.get_heures_total() > 0:
                if jour.get_heures_total() >= 8:
                    bulletin.nb_jours_plus_8h += 1
                else:
                    bulletin.nb_jours_moins_8h += 1

        # Calcul du cumul de nombre de jours de plus et moins de 8h depuis le 1er janvier
        sum_plus_8h = \
        BulletinSalaire.objects.filter(date_debut__year=today.year).aggregate(sum=Sum('nb_jours_plus_8h'))['sum']
        if sum_plus_8h is None:
            sum_plus_8h = 0
        sum_moins_8h = \
        BulletinSalaire.objects.filter(date_debut__year=today.year).aggregate(sum=Sum('nb_jours_moins_8h'))['sum']
        if sum_moins_8h is None:
            sum_moins_8h = 0
        bulletin.cumul_nb_jours_plus_8h = sum_plus_8h + bulletin.nb_jours_plus_8h
        bulletin.cumul_nb_jours_moins_8h = sum_moins_8h + bulletin.nb_jours_moins_8h

        # L'objet bulletin a toutes les infos pour calculer les montants. Le calcul est effectué par le template au format ODS
        # On remplit donc l'ODS avec les infos du bulletins et on collecte ensuite les informations restantes
        bulletin = fill_with_ods_template(bulletin, jours)

        # Une fois qu'on a les calcules du template ODS, on calcule les cumuls
        sum_net_imposable = \
        BulletinSalaire.objects.filter(date_debut__year=today.year).aggregate(sum=Sum('net_imposable'))['sum']
        if sum_net_imposable is None:
            sum_net_imposable = 0
        bulletin.cumul_net_imposable = sum_net_imposable + bulletin.net_imposable

        bulletin.save()

        for jour in jours:
            jour.bulletin_salaire = bulletin
            jour.save()

        return redirect('assmat:home')

    return HttpResponse("NOK", status=400)


@login_required
def home(request):
    today = datetime.date.today()
    if request.GET and request.GET['mois'] and request.GET['annee']:
        today = today.replace(month=int(request.GET['mois']), year=int(request.GET['annee']))

    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
    cal = France()
    jours_semaines = list(calendar.day_name)
    available_years = range(2017, 2025)

    contrat = Contrat.objects.get(Q(date_debut_contrat__lte=today),
                                  Q(date_fin_contrat__gte=today) | Q(date_fin_contrat__isnull=True))

    jours = list(JourTravail.objects.filter(date__month=today.month, date__year=today.year).order_by('date'))

    if len(jours) == 0:
        nb_jours_dans_mois = calendar.monthrange(today.year, today.month)[1]
        for day in range(1, nb_jours_dans_mois + 1):
            jour = JourTravail()
            jour.date = today.replace(day=int(day))
            if contrat is not None:
                week_day = 2 ** (6 - jour.date.weekday())
                if week_day & contrat.jours_normalement_travailles != 0:
                    # Si la condition est remplie, c'est que le jour est travaillé
                    jour.type = "T"
                    jour.heures_effectuees = contrat.nb_heures_accueil_jour
                    if cal.is_holiday(jour.date):
                        jour.type = "F."
                        jour.heures_effectuees = 0
                else:
                    jour.type = "NT"
                    jour.heures_effectuees = 0

                if contrat.indemnite_repas > 0 and jour.type == 'T':
                    jour.repas = True
                if contrat.indemnite_gouter > 0 and jour.type == 'T':
                    jour.gouter = True
            jours.append(jour)

    for jour in jours:
        jour.jour_semaine = jours_semaines[jour.date.weekday()]
        jour.is_travaille = jour.type == 'T'
        jour.form = JourTravailForm(instance=jour, prefix=str(jour.date.day))

    return render(request, 'assmat/home.html', locals())
