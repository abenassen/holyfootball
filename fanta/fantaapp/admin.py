from django.contrib import admin

# Register your models here.
from fantaapp.models import IncontroCampionato
from fantaapp.models import TrasferimentoRosa
from fantaapp.models import Ruolo


admin.site.register(IncontroCampionato)
admin.site.register(TrasferimentoRosa)
admin.site.register(Ruolo)