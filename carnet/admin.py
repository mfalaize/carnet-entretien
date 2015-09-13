from carnet.models import Periodicite, TypeMaintenance, Voiture, OperationMaintenance
from django.contrib import admin


class OperationMaintenanceEffectueInline(admin.TabularInline):
    model = OperationMaintenance
    extra = 0
    can_delete = False
    fields = ('type', 'kilometrage', 'date', 'effectue')
    readonly_fields = ('type', 'date', 'kilometrage')
    verbose_name = 'Dernière opération de maintenance effectuée'
    verbose_name_plural = 'Dernières opérations de maintenance effectuées'

    def get_queryset(self, request):
        """
        On ne récupère que les dernières opérations de maintenance
        """
        qs = super().get_queryset(request)

        l = list(qs.filter(effectue__exact=True).order_by('-date').values_list('pk', 'type_id'))
        type_ids = []
        pks = []
        for pk, type_id in l:
            if type_id not in type_ids:
                pks.append(pk)
                type_ids.append(type_id)

        return qs.filter(pk__in=pks).order_by('-date', 'pk')


class OperationMaintenanceNonEffectueInline(admin.TabularInline):
    model = OperationMaintenance
    extra = 0
    can_delete = False
    fields = ('type', 'kilometrage', 'date', 'effectue')
    readonly_fields = ('type',)
    verbose_name = 'Opération de maintenance en attente'
    verbose_name_plural = 'Opérations de maintenance en attente'

    def get_queryset(self, request):
        """
        On ne récupère que les dernières opérations de maintenance
        """
        qs = super().get_queryset(request)

        l = list(qs.filter(effectue__exact=False).order_by('-date').values_list('pk', 'type_id'))
        type_ids = []
        pks = []
        for pk, type_id in l:
            if type_id not in type_ids:
                pks.append(pk)
                type_ids.append(type_id)

        return qs.filter(pk__in=pks).order_by('-date', 'pk')


class OperationMaintenanceCreationInline(admin.TabularInline):
    model = OperationMaintenance
    extra = 0
    can_delete = True
    fields = ('type', 'kilometrage', 'date', 'effectue')
    verbose_name = 'Opération de maintenance à créer'
    verbose_name_plural = 'Opérations de maintenance à créer'

    def get_queryset(self, request):
        """
        Cette classe n'est que pour la création. On ne retourne donc rien.
        """
        qs = super().get_queryset(request)
        return qs.none()


class VoitureAdmin(admin.ModelAdmin):
    inlines = [OperationMaintenanceNonEffectueInline, OperationMaintenanceEffectueInline,
               OperationMaintenanceCreationInline]


admin.site.register(Periodicite)
admin.site.register(TypeMaintenance)
admin.site.register(Voiture, VoitureAdmin)
