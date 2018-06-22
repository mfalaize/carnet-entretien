# Register your models here.
from django.contrib import admin

from compta.models import Compte, Categorie, Operation, Budget, CategorieEpargne, Epargne, OperationEpargne, Identifiant


class OperationAdmin(admin.ModelAdmin):
    list_display = ('date_operation', 'date_valeur', 'libelle', 'montant')
    list_filter = ('date_operation', 'date_valeur')
    search_fields = ('libelle',)


admin.site.register(Compte)
admin.site.register(Categorie)
admin.site.register(Operation, OperationAdmin)
admin.site.register(Budget)
admin.site.register(CategorieEpargne)
admin.site.register(Epargne)
admin.site.register(OperationEpargne)
admin.site.register(Identifiant)
