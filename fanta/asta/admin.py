from django.contrib import admin
from asta.models import *

class AstaAdmin(admin.ModelAdmin):
    list_display = ('lega', 'apertura', 'tipo')

admin.site.register(Asta, AstaAdmin)
admin.site.register(Offerta)
#admin.site.register(Acquisto)
admin.site.register(CalciatoreChiamato)


