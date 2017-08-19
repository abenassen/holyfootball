from django.db import models
from pytz import timezone,utc
from django.conf import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Campionato(models.Model):
  """Si riferisce ad un campionato nazionale, e.g. Serie A, Liga..."""
  class Meta:
        verbose_name_plural = "Campionati"
  nome = models.CharField(max_length=50, unique=True) #nome del campionato
  datainizio = models.DateField() #data indicativa inizio campionato
  datafine = models.DateField() #data indicativa fine campionato
  totale_giornate = models.PositiveIntegerField(default=38)
  def __unicode__(self):
    return self.nome
  def giornate_disputate(self):
    try:
      val = self.giornata_set.filter(disputata='True').latest('numero').numero
    except ObjectDoesNotExist:
      val = 0
    return val
  def giornate_da_disputare(self):
    return self.totale_giornate - self.giornate_disputate()
  @staticmethod
  def lastCampionato():
        try:
         Campionato.objects.latest('id').id
        except Campionato.DoesNotExist:
         return 1





class SquadraCampionato(models.Model):
  """Si riferisce ad una vera squadra nel campionato"""
  nome = models.CharField(max_length=50) # nome della squadra
  campionato = models.ForeignKey(Campionato, on_delete = models.CASCADE) # campionato di appartenenza
  def __unicode__(self):
    return self.nome.title()


class Giornata(models.Model):
  """Si riferisce ad una giornata di un campionato reale"""
  campionato = models.ForeignKey(Campionato, on_delete = models.CASCADE)
  numero = models.PositiveSmallIntegerField() # numero della giornata nel campionato da 1,2,...
  data = models.DateTimeField(auto_now_add=True) # data indicativa della giornata
  disputata = models.BooleanField(default=False) # dice se la giornata e' stata disputata
  def aggiorna(self):
    if (self.disputata): #se e' gia' disputata non c'e' niente da fare
            return
    match_giornata = self.incontrocampionato_set # altri incontri della stessa giornata
    if (match_giornata.exists()):
      disputata = False
      try: # cerco la prossima giornata di campionato, se dista meno di due giorni all'inizio, questa la ritengo comunque disputata
        prox = self.campionato.giornata_set.get(numero=self.numero+1)
      except Giornata.DoesNotExist:
        prox = None
      if (prox):
        ore = (prox.data - datetime.datetime.now(utc))
        ore = ore.days*24 + ore.seconds//3600
        disputata = (ore < 40) # se mancano meno di quaranta ore alla prossima giornata, ritengo questa conclusa
      disputata = disputata or all(match_giornata.values_list('disputato', flat=True)) # controlla che tutti gli incontri della giornata sono stati disputati
      data = min(match_giornata.values_list('data', flat=True)) # prende la data del primo incontro
      self.disputata = disputata
      if (disputata):   # se questa e' diventata disputata, assegno eventuali premi
         premi = self.premiocompetizione_set.all() # premi da assegnare a questa giornata
         for pr in premi:
                pr.assegna_premio()
         if (prox):  # se la prossima non e' none, setto gli incontri della prossima
            prox.setta_incontri()
      self.data = data
      self.save()
  def setta_incontri(self):
      incontri = self.incontrolega_set.all() # tutti gli incontri che si disputano nella giornata
      inc_id = []
      inccoppa_id = []
      for inco in incontri:
         for inc in inco.fase.incontrocoppa_set.all():
                if inc.id in inccoppa_id:
                   continue
                inccoppa_id.append(inc.id)
                inc.setta_allenatori()
         for inc in inco.fase.incontrolega_set.all():
                if inc.id in inc_id:
                   continue
                inc_id.append(inc.id)
                inc.setta_allenatori()
  def __unicode__(self):
    return "Giornata %d" % self.numero


class IncontroCampionato(models.Model):
  """Si riferisce ad un vero incontro disputato tra due squadre del campionato"""
  class Meta:
        verbose_name_plural = "Incontri campionato"
  data = models.DateTimeField() #data d'inizio dell'incontro
  giornata = models.ForeignKey(Giornata, on_delete = models.CASCADE) # giornata a cui l'incontro appartiene
  squadracasa = models.ForeignKey(SquadraCampionato, related_name="IncontroCasa", on_delete = models.CASCADE) #squadra che gioca in casa
  squadratrasferta = models.ForeignKey(SquadraCampionato, related_name="IncontroTransferta", on_delete = models.CASCADE) #squadra che gioca in trasferta
  disputato = models.BooleanField(default=False) # se l'incontro e' gia' stato disputato
  golcasa = models.PositiveSmallIntegerField(default=0) # gol della squadra di casa
  goltrasferta = models.PositiveSmallIntegerField(default=0) # gol della squadra in trasferta
  def save(self, *args, **kwargs):
    super(IncontroCampionato, self).save(*args, **kwargs)
  def __unicode__(self):
    string = str(self.data.astimezone(timezone(settings.TIME_ZONE)).strftime('%d-%m-%Y %H:%M')) + ("\t %s-%s" % (self.squadracasa, self.squadratrasferta))
    if (self.disputato):
            string = string + (" %d-%d" % (self.golcasa, self.goltrasferta))
    return string
  @property
  def squadre(self):
    return (self.squadracasa, self.squadratrasferta)

class Calciatore(models.Model):
 """calciatore di una data squadra"""
 class Meta:
        verbose_name_plural = "Calciatori"
 nome = models.CharField(max_length=40)
 primavera = models.BooleanField(default=False)
 squadra = models.ForeignKey(SquadraCampionato, blank=True, null=True, on_delete = models.CASCADE)
 scorsoanno = models.ForeignKey('self',  blank=True, null=True, on_delete = models.CASCADE) # altro oggetto calciatore corrispondente a se stesso l'anno prima
 #i seguenti sono dati statistici relativi all'anno precedente, usati nella visualizzazione in fase d'asta
 exsquadra = models.CharField(max_length=40)
 quotazione = models.PositiveSmallIntegerField(blank=True, null=True)
 fantamedia = models.FloatField(blank=True, null=True)
 fantamediasq = models.FloatField(blank=True, null=True)
 mediavoto = models.FloatField(blank=True, null=True)
 presenze = models.IntegerField(blank=True, null=True)
 golfatti = models.IntegerField(blank=True, null=True)
 golsubiti = models.IntegerField(blank=True, null=True)
 rigoriparati = models.IntegerField(blank=True, null=True)
 ammonizioni = models.IntegerField(blank=True, null=True)
 espulsioni = models.IntegerField(blank=True, null=True)
 assist = models.IntegerField(blank=True, null=True)
 imageurl = models.TextField(max_length=500, blank=True, null=True) # url con un'immagine del giocatore
 def save(self, *args, **kwargs):
   if self.primavera:
       ru = self.ruolo.first().nome
       self.nome = 'Primavera '  + ru
       self.exsquadra = ''
       self.squadra = None
   return super(Calciatore, self).save(*args, **kwargs)
 def __unicode__(self):
    return self.nome.title()

