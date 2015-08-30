from carnet.models import Periodicite, TypeMaintenance, ModeleVoiture, Voiture, OperationMaintenance
from django.contrib import admin

admin.site.register(Periodicite)
admin.site.register(OperationMaintenance)
admin.site.register(TypeMaintenance)
admin.site.register(ModeleVoiture)
admin.site.register(Voiture)
