from django.urls import reverse
from django.db import models
#from django.forms.widgets import TextInput, NumberInput
#from django.contrib.auth.models import User
import random
import string
#from django.utils.translation import ugettext_lazy as _
from roundrobin import *

import sys
if sys.version[0]=='3':
   izip = zip
   from . import fantafun
else:
   from itertools import izip
   import fantafun



#from asta.models import Asta
from django.forms import ModelChoiceField,IntegerField

import datetime
import sys



from django.forms import ModelForm, NumberInput, Form
from django.utils.translation import ugettext_lazy as _






from .campionatoreale import Campionato
from .campionatoreale import SquadraCampionato
from .campionatoreale import Giornata
from .campionatoreale import IncontroCampionato
from .campionatoreale import Calciatore

from .lega import Redazione
from .lega import Lega
from .lega import Competizione
from .lega import FaseCompetizione
from .lega import PremioCompetizione
from .lega import Allenatore
from .lega import Ruolo
from .lega import Formazione
from .lega import GiornataLega
from .lega import IncontroLega
from .lega import IncontroCoppa
from .lega import Referto, Voto
from .lega import Messaggio









class VotoForm(ModelForm):
    """ Edit a house """
    class Meta:
        model = Voto
        fields = ['ha_giocato','votopuro', 'assist',
        'golsuazione', 'golsurigore', 'ammo', 'espu', 'autogol', 'golsubiti', 'rigorisbagliati', 'rigoriparati', 'goldellavittoria',
        'goldelpareggio']
        widgets = {'votopuro': NumberInput(attrs={'step': '0.5'})}
        labels = {
            'votopuro': _('Voto puro'),
            'assist': _('Numero di assist'),
            'golsuazione': _('Gol su azione'),
            'golsurigore': _('Rigori segnati'),
            'ammo': _('Ammonizioni'),
            'espu': _('Espulsioni'),
            'autogol': _('Autogol'),
            'golsubiti': _('Gol subiti'),
            'rigorisbagliati': _('Rigori sbagliati'),
            'rigoriparati': _('Rigori parati'),
            'goldellavittoria': _('Gol decisivi per la vittoria'),
            'goldelpareggio': _('Gol decisivi per il pareggio'),
            'ha_giocato': _("E' entrato in campo?")
        }


class RefertoForm(ModelForm):
    """ Edit a person and her house """
    class Meta:
        model = Referto
        fields = ['non_ha_giocato', 'fantavoto_db', 'votopuro_db']
        labels = {'non_ha_giocato': _('Imponi SV'),'fantavoto_db': _('Fantavoto'),'votopuro_db': _('Voto Puro')}
        widgets = {'fantavoto_db': NumberInput(attrs={'step': 0.5}), 'votopuro_db': NumberInput(attrs={'step': 0.5})}



class TrasferimentoRosa(models.Model):
  """acquisto/cessione di un calciatore da parte di un allenatore"""
  class Meta:
         verbose_name_plural = "Trasferimento Rose"
  from asta.models import Asta
  calciatore = models.ForeignKey(Calciatore, on_delete = models.CASCADE) # il calciatore acquistato
  valore = models.PositiveSmallIntegerField() # importo dell'acquisto/cessione (nel secondo caso sono i soldi recuperati
  acquisto = models.BooleanField(default=True) # se e' un acquisto o una cessione
  allenatore = models.ForeignKey(Allenatore, on_delete = models.CASCADE) # l'allenatore che ha fatto il trasferimento
  asta = models.ForeignKey(Asta, blank=True, null=True, on_delete = models.CASCADE) # asta da cui proviene l'acquisto
  def save(self, *args, **kwargs):
        redazione = self.allenatore.lega.redazione
        print >>sys.stderr, redazione.nome + " "+ self.calciatore.nome + " " + str(self.calciatore.id)
        ru = self.calciatore.ruolo.get(redazione=redazione).nome
        segno = 1 if self.acquisto else -1
        self.allenatore.budget = self.allenatore.budget - segno*self.valore
        if (self.acquisto):
            self.allenatore.decresci_ruolo(ru)
        else:
            self.allenatore.cresci_ruolo(ru)
        self.allenatore.full_clean(exclude=['logourl'])
        self.allenatore.save()
        super(TrasferimentoRosa, self).save(*args, **kwargs)
  def delete(self, *args, **kwargs):
        redazione = self.allenatore.lega.redazione
        ru = self.calciatore.ruolo.get(redazione=redazione).nome
        segno = 1 if self.acquisto else -1
        self.allenatore.budget = self.allenatore.budget + self.valore*segno
        if (self.acquisto):
            self.allenatore.cresci_ruolo(ru)
        else:
            self.allenatore.decresci_ruolo(ru)
        self.allenatore.full_clean(exclude=['logourl'])
        self.allenatore.save()
        super(TrasferimentoRosa, self).delete(*args, **kwargs)
  def __unicode__(self):
        return "%s da %s a %d" % (self.calciatore.nome,self.allenatore.nome, self.valore)



class TrasferimentoRosaForm(ModelForm):
          def __init__(self, *args, **kwargs):
                lega = kwargs.pop('lega')
                super(TrasferimentoRosaForm, self).__init__(*args, **kwargs)
                self.fields['calciatore'] = ModelChoiceField(queryset=Calciatore.objects.filter(squadra__campionato=lega.campionato).order_by('nome'))
                self.fields['allenatore'] = ModelChoiceField(queryset=lega.allenatore_set)
          class Meta:
            fields = ['calciatore', 'valore', 'acquisto', 'allenatore']
            labels = {
              'calciatore': _("Calciatore coinvolto nell'acquisto"),
              'valore': _("Importo (spesa o crediti ottenuti"),
              'allenatore': _('Allenatore del trasferimento'),
            }
            model = TrasferimentoRosa

class ScambioForm(Form):
          def __init__(self, *args, **kwargs):
                lega = kwargs.pop('lega')
                super(ScambioForm, self).__init__(*args, **kwargs)
                self.fields['allenatore1'] = ModelChoiceField(queryset=lega.allenatore_set, error_messages={'required': 'Non puoi lasciare in bianco questo campo'})
                self.fields['allenatore1'].label = 'Allenatore 1'
                self.fields['calciatore1'] = ModelChoiceField(queryset=Calciatore.objects.filter(squadra__campionato=lega.campionato).order_by('nome'), error_messages={'required': 'Non puoi lasciare in bianco questo campo'})
                self.fields['calciatore1'].label = 'Calciatore 1'
                self.fields['allenatore2'] = ModelChoiceField(queryset=lega.allenatore_set, error_messages={'required': 'Non puoi lasciare in bianco questo campo'})
                self.fields['allenatore2'].label = 'Allenatore 2'
                self.fields['calciatore2'] = ModelChoiceField(queryset=Calciatore.objects.filter(squadra__campionato=lega.campionato).order_by('nome'), error_messages={'required': 'Non puoi lasciare in bianco questo campo'})
                self.fields['calciatore2'].label = 'Calciatore 2'
                self.fields['contropartita'] = IntegerField(min_value=-1000, max_value=1000)
                self.fields['contropartita'].label = 'Contropartita (da 1 a 2)'
                self.fields['contropartita'].initial = 0
          def clean(self): # controllo che lo scambio fosse possibile
                cleaned_data = super(ScambioForm, self).clean()
                if self._errors: # ci sono gia' errori nel form
                        return cleaned_data
                allenatore1 = cleaned_data['allenatore1']
                allenatore2 = cleaned_data['allenatore2']
                if allenatore1 == allenatore2:
                        raise ValidationError(_('I due allenatori non possono essere uguali!'))
                rosa1 = allenatore1.ottieni_rosa()
                rosa2 = allenatore2.ottieni_rosa()
                contropartita = cleaned_data.get('contropartita',0)
                calciatore1 = None
                calciatore2 = None
                for ruolo in rosa1.keys():
                        lst1 = [x for x in rosa1[ruolo] if x[0] == cleaned_data['calciatore1']]
                        lst2 = [x for x in rosa2[ruolo] if x[0] == cleaned_data['calciatore2']]
                        if len(lst1)==1: # ho trovato il calciatore nella rosa dell'allenatore 1
                                if len(lst2)!=1:
                                        raise ValidationError(_('I due giocatori non hanno lo stesso ruolo'))
                                (calciatore1, costo1) = lst1[0]
                                (calciatore2, costo2) = lst2[0]
                                break
                if calciatore1 is None:
                        raise ValidationError(_('L\'allenatore dei %(all)s non possiede %(cal)s'), params={'all': allenatore1, 'cal': cleaned_data['calciatore1']})
                if calciatore2 is None:
                        raise ValidationError(_('L\'allenatore dei %(all)s non possiede %(cal)s'), params={'all': allenatore2, 'cal': cleaned_data['calciatore2']})
                if (contropartita>0 and allenatore1.budget < contropartita) or (contropartita<0 and allenatore2.budget < -contropartita):
                        raise ValidationError(_('Crediti insufficienti all\'acquisto.'))
                cleaned_data['costo1'] = costo1
                cleaned_data['costo2'] = costo2
                return cleaned_data
