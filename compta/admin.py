# Register your models here.
from django.contrib import admin

from compta.models import Compte, Categorie, Operation

admin.site.register(Compte)
admin.site.register(Categorie)
admin.site.register(Operation)
