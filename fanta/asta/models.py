from django.db import models
import datetime
from django.utils import timezone
from fantaapp.models import *
from pytz import utc

class ConfrontoCalciatori(models.Model):
  calciatore1 = models.ForeignKey(Calciatore, related_name='Calc1', on_delete = models.CASCADE)
  calciatore2 = models.ForeignKey(Calciatore, related_name='Calc2', on_delete = models.CASCADE)

class Asta(models.Model):
 lega = models.ForeignKey(Lega, on_delete = models.CASCADE)
 creata = models.DateTimeField(editable=False)
 modificata = models.DateTimeField()
 apertura = models.DateTimeField() # data di apertura dell'asta
 chiusura = models.DateTimeField() # data di chiusura dell'asta
 tipo = models.CharField(max_length=10, default="random") # tipo di asta: se asta iniziale random, se mercato...
 def save(self, *args, **kwargs):
   ''' On save, update timestamps '''
   adesso = datetime.datetime.now(utc)
   if not self.id:
        self.creata = adesso
   self.modificata = adesso
   return super(Asta, self).save(*args, **kwargs)

class Offerta(models.Model):
 asta = models.ForeignKey(Asta, on_delete = models.CASCADE) # asta di cui l'offerta fa parte
 allenatore = models.ForeignKey(Allenatore, on_delete = models.CASCADE) # allenatore che ha fatto l'offerta
 soldi = models.PositiveSmallIntegerField() # importo dell'offerta
 calciatore = models.ForeignKey(Calciatore, on_delete = models.CASCADE)
 calciatore_da_lasciare = models.ForeignKey(Calciatore, blank=True, null=True, related_name="LasciatiIn", on_delete = models.CASCADE)
 status = models.CharField(default="attiva", max_length=10)
 orario = models.DateTimeField(auto_now_add=True)
 def __unicode__(self):
    return "%s, %s: %s (%s) - %d milioni" % (self.orario.strftime("%H:%M"), self.allenatore, self.calciatore.nome, self.calciatore.squadra, self.soldi)


#class Acquisto(models.Model):
# offerta = models.ForeignKey(Offerta)
# def __unicode__(self):
#   return "%s da %s a %d" % (self.offerta.calciatore.nome,self.offerta.allenatore.nome, self.offerta.soldi)


class CalciatoreChiamato(models.Model):
 """contiene i calciatori dell'asta che sono gia' stati chiamati"""
 asta = models.ForeignKey(Asta, on_delete = models.CASCADE) # asta corrispondente alla lista dei giocatori chiamati
 calciatore = models.ForeignKey(Calciatore, on_delete = models.CASCADE) # giocatore chiamato
 def __unicode__(self):
   return self.calciatore.__unicode__()

