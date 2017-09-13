import calendar
import datetime
import locale

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from assmat.forms import JourTravailForm
from assmat.models import JourTravail, Contrat


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
def home(request):
    today = datetime.date.today()
    if request.GET and request.GET['mois'] and request.GET['annee']:
        today = today.replace(month=int(request.GET['mois']), year=int(request.GET['annee']))

    locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
    jours_semaines = list(calendar.day_name)
    available_years = range(2017, 2025)

    contrat = Contrat.objects.get(Q(date_debut_contrat__lte=today),
                                  Q(date_fin_contrat__gte=today) | Q(date_fin_contrat__isnull=True))

    jours = list(JourTravail.objects.filter(date__month=today.month, date__year=today.year).order_by('date'))

    if len(jours) == 0:
        nb_jours_dans_mois = calendar.monthrange(today.year, today.month)[1]
        for day in range(1, nb_jours_dans_mois+1):
            jour = JourTravail()
            jour.date = today.replace(day=int(day))
            if contrat is not None:
                week_day = 2 ** (6 - jour.date.weekday())
                if week_day & contrat.jours_normalement_travailles != 0:
                    # Si la condition est remplie, c'est que le jour est travaillé
                    jour.type = "T"
                    jour.heures_effectuees = contrat.nb_heures_accueil_jour
                else:
                    jour.type = "NT"
                    jour.heures_effectuees = 0

                if contrat.indemnite_repas > 0:
                    jour.repas = True
                if contrat.indemnite_gouter > 0:
                    jour.gouter = True
            jours.append(jour)

    for jour in jours:
        jour.jour_semaine = jours_semaines[jour.date.weekday()]
        jour.form = JourTravailForm(instance=jour, prefix=str(jour.date.day))

    return render(request, 'assmat/home.html', locals())
