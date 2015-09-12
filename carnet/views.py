# Create your views here.
from carnet.models import Voiture, OperationMaintenance
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render


@login_required
def home(request):
    voitures = Voiture.objects.filter(proprietaire=request.user)
    dernieres_operations = OperationMaintenance.objects.filter(voiture__in=voitures).order_by('effectue', '-date')
    paginator = Paginator(dernieres_operations, 10)

    page = request.GET.get('page')
    try:
        dernieres_operations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dernieres_operations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        dernieres_operations = paginator.page(paginator.num_pages)

    return render(request, 'home.html', locals())
