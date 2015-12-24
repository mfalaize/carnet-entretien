from django.contrib import admin

from carnet_auto.models import TypeOperation, ChampSupplementaire


class TypeOperationAdmin(admin.ModelAdmin):
    filter_horizontal = ('champs_supplementaires',)


admin.site.register(TypeOperation, TypeOperationAdmin)
admin.site.register(ChampSupplementaire)
