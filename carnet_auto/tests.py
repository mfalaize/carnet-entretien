from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from carnet_auto.models import Voiture


class TestCheckEntretien(TestCase):
    fixtures = ["initial"]

    def setUp(self):
        user = User.objects.create(username="test", email="test@test.com")
        Voiture.objects.create(nom="Voiture test", kilometrage=100000, proprietaire=user,
                               date_mise_circulation="01/01/2008", moyenne_km_annuel=10000,
                               date_derniere_maj_km=datetime.now().date())

    def test_ne_fait_rien(self):
        """Vérifie que le script ne fait rien lorsque tout va bien"""

    def test_declenchement_alerte(self):
        """Vérifie que le script déclenche bien une alerte"""
