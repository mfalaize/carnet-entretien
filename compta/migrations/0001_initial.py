# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('budget', models.DecimalField(verbose_name='Valeur', decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=256, verbose_name='Libellé')),
            ],
        ),
        migrations.CreateModel(
            name='Compte',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('banque', models.CharField(max_length=128, choices=[('CM', 'Crédit Mutuel')], verbose_name='Banque')),
                ('numero_compte', models.CharField(max_length=127, verbose_name='Numéro de compte')),
                ('solde', models.DecimalField(verbose_name='Solde', decimal_places=2, null=True, max_digits=8)),
                ('login', models.CharField(max_length=128, verbose_name='Login')),
                ('mot_de_passe', models.CharField(max_length=128, verbose_name='Mot de passe')),
                ('utilisateurs', models.ManyToManyField(verbose_name='Utilisateurs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date_operation', models.DateField(verbose_name="Date d'opération")),
                ('date_valeur', models.DateField(verbose_name='Date de valeur')),
                ('montant', models.DecimalField(verbose_name='Montant', decimal_places=2, max_digits=8)),
                ('libelle', models.CharField(max_length=512, verbose_name='Libellé')),
                ('categorie', models.ForeignKey(null=True, to='compta.Categorie', verbose_name='Catégorie')),
                ('compte', models.ForeignKey(verbose_name='Compte', to='compta.Compte')),
            ],
        ),
        migrations.AddField(
            model_name='budget',
            name='categorie',
            field=models.ForeignKey(verbose_name='Catégorie', to='compta.Categorie'),
        ),
    ]
