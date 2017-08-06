# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import carnet_auto.models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChampSupplementaire',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('libelle', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='ChampSupplementaireValeur',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('valeur', models.CharField(max_length=256)),
                ('champ', models.ForeignKey(to='carnet_auto.ChampSupplementaire')),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('prix', models.DecimalField(null=True, blank=True, max_digits=8, verbose_name='Prix', decimal_places=2)),
                ('effectue_par_garage', models.BooleanField(verbose_name='Effectué par un garage ?', default=True)),
                ('effectue', models.BooleanField(help_text="Est décoché si l'opération de maintenance n'a pas encore été effectué", verbose_name='Effectué ?', default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgrammeMaintenance',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('periodicite_kilometres', models.IntegerField(null=True, blank=True, verbose_name='Périodicité en Km')),
                ('periodicite_annees', models.IntegerField(null=True, blank=True, verbose_name='Périodicité en année')),
                ('delai_alerte', models.IntegerField(blank=True, help_text="Contrôle le délai d'alerte pour une opération à effectuer de façon à déclencher l'alerte plus tôt que le jour j (par défaut est déclenché le jour j)", verbose_name='Délai pour déclencher une alerte (en jours)', default=0)),
                ('delai_rappel', models.IntegerField(blank=True, help_text="Le rappel permet de renvoyer un mail lorsque les opérations du programme n'ont pas été encore effectués (par défaut 15 jours)", verbose_name='Délai pour déclencher un rappel (en jours)', default=15)),
            ],
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date', models.DateField(verbose_name='Date', default=django.utils.timezone.now)),
                ('kilometrage', models.IntegerField(verbose_name='Nombre de Km lors de la révision')),
            ],
        ),
        migrations.CreateModel(
            name='TypeOperation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('nom', models.CharField(max_length=256)),
                ('champs_supplementaires', models.ManyToManyField(blank=True, to='carnet_auto.ChampSupplementaire')),
            ],
        ),
        migrations.CreateModel(
            name='Voiture',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('nom', models.CharField(max_length=256, help_text='Ex : Voiture de Maxime', verbose_name='Nom de la voiture')),
                ('immatriculation', models.CharField(max_length=16, verbose_name='Immatriculation')),
                ('modele', models.CharField(max_length=256, help_text='Ex : RENAULT Mégane II 1.5 dCi 86cv', verbose_name='Modèle')),
                ('kilometrage', models.IntegerField(verbose_name='Nombre de Km au compteur')),
                ('date_mise_circulation', models.DateField(verbose_name='Date de mise en circulation')),
                ('moyenne_km_annuel', models.IntegerField(verbose_name='Nombre de Km effectués annuellement par la voiture')),
                ('date_derniere_maj_km', models.DateField(verbose_name='Date de dernière mise à jour du kilométrage')),
                ('photo', models.ImageField(upload_to=carnet_auto.models.get_image_user_path, blank=True, verbose_name='Photo')),
                ('prix_achat', models.DecimalField(null=True, blank=True, max_digits=10, verbose_name="Prix d'achat", decimal_places=2)),
                ('date_achat', models.DateField(null=True, blank=True, verbose_name="Date d'achat")),
                ('kilometrage_achat', models.IntegerField(null=True, blank=True, verbose_name="Nombre de Km à l'achat")),
                ('proprietaire', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Propriétaire')),
            ],
        ),
        migrations.AddField(
            model_name='revision',
            name='voiture',
            field=models.ForeignKey(to='carnet_auto.Voiture'),
        ),
        migrations.AddField(
            model_name='programmemaintenance',
            name='types_operations',
            field=models.ManyToManyField(to='carnet_auto.TypeOperation', verbose_name='Opérations du programme'),
        ),
        migrations.AddField(
            model_name='programmemaintenance',
            name='voiture',
            field=models.ForeignKey(to='carnet_auto.Voiture'),
        ),
        migrations.AddField(
            model_name='operation',
            name='revision',
            field=models.ForeignKey(to='carnet_auto.Revision', verbose_name='Révision'),
        ),
        migrations.AddField(
            model_name='operation',
            name='type',
            field=models.ForeignKey(to='carnet_auto.TypeOperation', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='champsupplementairevaleur',
            name='operation',
            field=models.ForeignKey(to='carnet_auto.Operation'),
        ),
    ]
