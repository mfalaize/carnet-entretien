from carnet.models import TypeOperation, ChampSupplementaire
from django.contrib import admin


class TypeOperationAdmin(admin.ModelAdmin):
    filter_horizontal = ('champs_supplementaires',)


admin.site.register(TypeOperation, TypeOperationAdmin)
admin.site.register(ChampSupplementaire)
