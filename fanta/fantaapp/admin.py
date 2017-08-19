from django.contrib import admin

from django.utils.translation import ugettext_lazy as _
# Register your models here.
from fantaapp.models import IncontroCampionato
from fantaapp.models import TrasferimentoRosa
from fantaapp.models import Ruolo, Allenatore, Calciatore, Campionato, Lega


class IncontroCampionatoAdmin(admin.ModelAdmin):
    list_display = ('data', 'giornata', 'squadracasa', 'squadratrasferta', 'golcasa', 
                    'goltrasferta', 'get_campionato')
    list_filter = ('giornata__campionato', 'giornata__numero')
    def get_campionato(self, obj):
        return obj.giornata.campionato
        
class AllenatoreAdmin(admin.ModelAdmin):
    list_display = ('utente', 'lega', 'nomesquadra')
    list_filter = ('lega',)

class CalciatoreAdmin(admin.ModelAdmin):
    list_display = ('nome', 'squadra', 'squadracampionato')
    list_filter = ('squadra__campionato',)
    def squadracampionato(self, obj):
        return obj.squadra.campionato

class AllenatoreListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Allenatore')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'allenatore'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        lega = request.GET.get('allenatore__lega__id__exact', '')
        if lega:
            allenatori = Allenatore.objects.filter(lega__id__exact=lega)
        else:
            allenatori = Allenatore.objects.none()
        print allenatori
        return allenatori.values_list('id', 'nomesquadra')

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        return queryset.filter(allenatore_id=self.value())

class TrasferimentoRosaAdmin(admin.ModelAdmin):
    list_display = ('calciatore', 'valore', 'acquisto', 'allenatore')
    list_filter = ('allenatore__lega', AllenatoreListFilter)
    def get_campionato(self, obj):
        return obj.giornata.campionato
        


admin.site.register(IncontroCampionato, IncontroCampionatoAdmin)
admin.site.register(TrasferimentoRosa, TrasferimentoRosaAdmin)
admin.site.register(Ruolo)
admin.site.register(Allenatore, AllenatoreAdmin)
admin.site.register(Calciatore, CalciatoreAdmin)
admin.site.register(Campionato)
admin.site.register(Lega)