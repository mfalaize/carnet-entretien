# Register your models here.
from django.contrib import admin

from compta.models import Compte, Categorie, Operation, Budget, CategorieEpargne, Epargne, OperationEpargne, Identifiant

admin.site.register(Compte)
admin.site.register(Categorie)
admin.site.register(Operation)
admin.site.register(Budget)
admin.site.register(CategorieEpargne)
admin.site.register(Epargne)
admin.site.register(OperationEpargne)
admin.site.register(Identifiant)
