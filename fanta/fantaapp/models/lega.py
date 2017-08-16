from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list

from django.forms import ModelForm, Textarea, TextInput
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelChoiceField, Form, IntegerField, ValidationError
from django.conf import settings


from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import transaction

from auxfun import *
from pytz import timezone

from .campionatoreale import Campionato, Calciatore, Giornata

import math
import simplejson as json
import datetime


import fantafun

nome_turni_coppa = [u'Finale', u'Semifinale', u'Quarti', u'Ottavi', u'Sedicesimi', u'Trentaduesimi', u'Sessantaquattresimi', u'Turno Preliminare']
votoprimavera = {'P': 3.5, 'D':4.5, 'C':4.5, 'A':4.5}
ruoli_lunghi = {'P': "Portiere", 'D':"Difensore", 'C':"Centrocampista", 'A':"Attaccante"}
ruoli_lunghi_plurali = {'P': "Portieri", 'D':"Difensori", 'C':"Centrocampisti", 'A':"Attaccanti"}






class Redazione(models.Model):
 nome = models.CharField(max_length=50) # nome della redazione
 descrizione = models.TextField() # descrizione del funzionamento della redazione
 def __unicode__(self):
    return self.nome


class Lega(models.Model):
 nome = models.CharField(max_length=50) # nome della lega
 descrizione = models.TextField(blank=True) # descrizione della lega
 numeropartecipanti = models.PositiveIntegerField(default=10, validators=[MaxValueValidator(20)]) # descrizione della lega
 codice = models.CharField(max_length=20, default=randomHash, unique = True, db_index=True)
 calcolo_voto = models.CharField(max_length=100, default='votostd') # contiene il riferimento alla funzione di un oggetto della classe Voto per il calcolo del voto, inserita nel modulo funzioni_voto.py
 budgetiniziale = models.PositiveIntegerField(default=1000)
 numeroportieri = models.PositiveIntegerField(default=3)
 numerodifensori = models.PositiveIntegerField(default=8)
 numerocentrocampisti = models.PositiveIntegerField(default=8)
 numeroattaccanti = models.PositiveIntegerField(default=6)
 redazione = models.ForeignKey(Redazione, on_delete = models.CASCADE)
 campionato = models.ForeignKey(Campionato, default=Campionato.lastCampionato, on_delete = models.CASCADE)
 numero_gironi = models.PositiveIntegerField(default=4)
 def get_absolute_url(self):
        return reverse('aprilega', kwargs={'legahash': self.codice})
 def nuovo_allenatore(self, utente, is_amministratore=False):
        if (self.allenatore_set.count() >= self.numeropartecipanti):
                raise ValueError("Lega gia' completa!")
        return Allenatore(lega=self, utente=utente, amministratore=is_amministratore, budget=self.budgetiniziale,
                          numeroportieri=self.numeroportieri,numerodifensori=self.numerodifensori,
                          numerocentrocampisti=self.numerocentrocampisti,numeroattaccanti=self.numeroattaccanti)
 def limite_ruolo(self, ruolo):
        """restituisce il numero di calciatori per rosa in un dato ruolo dato da 'P','D'... """
        return getattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower())
 @property
 def limite_tesserati(self):
    tot = 0
    for r in ruoli_lunghi.keys():
            tot = tot + self.limite_ruolo(r)
    return tot
 def totale_giornate(self):
   return self.numero_gironi*(self.numeropartecipanti-1)

 def __unicode__(self):
   return self.nome

class LegaForm(ModelForm):
    class Meta:
        fields = ['nome','numeropartecipanti',  'descrizione', 'redazione']
        labels = {
            'nome': _('Nome della lega'),
        }
        #help_texts = {
        #    'name': _('Some useful help text.'),
        #}
        error_messages = {
            'nome': {
                'max_length': _("Il nome della lega e' troppo lungo."),
            },
        }
        model = Lega
        widgets = {
            'nome': TextInput(attrs={'placeholder': 'Nome Lega'}),
            'descrizione': Textarea(attrs={'rows': '2'}),
        }


class Allenatore(models.Model):
 """si riferisce ad un allenatore/squadra presente in una lega associato ad un dato utente"""
 utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE) #utente corrispondente a quest'allenatore/squadra
 lega = models.ForeignKey(Lega, on_delete = models.CASCADE)
 budget = models.PositiveSmallIntegerField(editable=False,  validators=[MinValueValidator(0)])
 numeroportieri = models.PositiveIntegerField(editable=False,  validators=[MinValueValidator(0)]) #numero di portieri da acquistare
 numerodifensori = models.PositiveIntegerField(editable=False,  validators=[MinValueValidator(0)])
 numerocentrocampisti = models.PositiveIntegerField(editable=False,  validators=[MinValueValidator(0)])
 numeroattaccanti = models.PositiveIntegerField(editable=False,  validators=[MinValueValidator(0)])
 nomesquadra = models.CharField(max_length=200)
 amministratore = models.BooleanField(default=False) # dice se l'allenatore e' uno degli amministratori della lega
 logourl = models.URLField(default='/static/fantaapp/images/savona.png')
 editabili = ['nomesquadra', 'logourl']
 class Meta:
        verbose_name_plural = "Allenatori"
        unique_together = (("utente", "lega"),)  # c'e' un unico allenatore/squadra per un dato utente/lega
 def resetta(self):
        self.numeroportieri = self.lega.numeroportieri
        self.numerodifensori = self.lega.numerodifensori
        self.numerocentrocampisti = self.lega.numerocentrocampisti
        self.numeroattaccanti = self.lega.numeroattaccanti
        self.budget = self.lega.budgetiniziale
 def save(self, *args, **kwargs):
        if (not(self.nomesquadra) or self.nomesquadra==""): # se la squadra non e' stata impostata le da' un nome di default
          self.nomesquadra="Squadra di " + self.utente.profile.alias
        if (not(self.id)): # sta venendo creato in questo momento
           self.resetta()
        super(Allenatore, self).save(*args, **kwargs)
 def numero_ruolo(self, ruolo):
        """numero calciatori in un dato ruolo ancora da acquistare"""
        return getattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower())
 def decresci_ruolo(self, ruolo):
        currval = getattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower())
        setattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower(), currval - 1)
 def cresci_ruolo(self, ruolo):
        currval = getattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower())
        setattr(self, 'numero'+ ruoli_lunghi_plurali[ruolo].lower(), currval + 1)
 @property
 def nome(self):
    return self.utente.profile.alias
 @property
 def totale_da_tesserare(self):
    tot = 0
    for r in ruoli_lunghi.keys():
            tot = tot + self.numero_ruolo(r)
    return tot
 def ottieni_rosa(self):
    """produce un dizionari dei ruoli contenente le liste di coppie (calciatore, prezzo)"""
    transf = self.trasferimentorosa_set.select_related('calciatore').all()
    rosa_dict = {}
    for r in ruoli_lunghi_plurali.keys():
            rosa_dict[r] = []
    for tr in transf:
        print(tr)
        ru = tr.calciatore.ruolo.get(redazione=self.lega.redazione).nome
        if tr.acquisto:
              print('acquisto')
              rosa_dict[ru].append((tr.calciatore, tr.valore))
        else:
              print('cessione')
              rosa_dict[ru] = [x for x in rosa_dict[ru] if x[0].id != tr.calciatore.id]
              print(rosa_dict[ru])
    return rosa_dict
 def __unicode__(self):
    return self.nomesquadra



class Messaggio(models.Model):
  """Contiene i messaggi su cio' che accade nella lega e ai singoli allenatori"""
  lega = models.ForeignKey(Lega, on_delete = models.CASCADE) # lega del messaggio
  allenatore = models.ForeignKey(Allenatore, blank=True, null=True, on_delete = models.CASCADE) # destinatario del messaggio, se None e' per tutti
  testo = models.CharField(max_length=200) # testo del messaggio
  data = models.DateTimeField(auto_now=True) # data del messaggio
  @property
  def datatesto(self):
        return self.data.strftime("%d-%m-%Y, %H:%M. ") + self.testo
  def __unicode__(self):
    return self.datatesto







class Ruolo(models.Model):
  class Meta:
        verbose_name_plural = "Ruoli"
  calciatore = models.ForeignKey(Calciatore, related_name='ruolo', on_delete = models.CASCADE)
  redazione = models.ForeignKey(Redazione, on_delete = models.CASCADE)
  nome = models.CharField(max_length=5) # stringa indicante il ruolo
  @property
  def nome_lungo(self):
     return ruoli_lunghi[self.nome]
  def __unicode__(self):
     return str(self.calciatore) + " - " + str(self.calciatore.squadra.campionato) + " - " + str(self.nome)


class Formazione(models.Model):
 """contiene la formazione inviata da un allenatore"""
 giocatori = models.ManyToManyField(Calciatore, through='Referto')
 allenatore = models.ForeignKey(Allenatore, on_delete = models.CASCADE)
 data_invio = models.DateTimeField() #data d'invio della formazione
 definitiva = models.BooleanField(default=False) # se la formazione e' definitiva, perche' per esempio riguarda match gia' cominciati
 giornata = models.ForeignKey(Giornata, on_delete = models.CASCADE) # tutte le partite che corrispondono a questa giornata
 modulo = models.CharField(max_length=5, default = '4,4,2', validators=[validate_comma_separated_integer_list]) # modulo tipo '4,4,2'
 #modulo = models.CommaSeparatedIntegerField(max_length=5, default='4,4,2')
 @transaction.atomic
 def riassocia_referti(self):
     """associa i referti della squadra a Voti della giornata corrente"""
     referti = self.referto_set.all()
     votigiornata = self.giornata.voto_set
     for ref in referti:
        try:
          ref.voto = votigiornata.get(calciatore=ref.calciatore)
        except Voto.DoesNotExist:
          ref.voto = None
        ref.da_ricalcolare = True
	ref.save()
 def save(self, *args, **kwargs):
   self.data_invio = datetime.datetime.now(timezone(settings.TIME_ZONE))
   return super(Formazione, self).save(*args, **kwargs)
 def clona(self):
     """restituisce una copia dell'oggetto formazione, copiando anche i referti associati"""
     formazione = self
     referti = list(formazione.referto_set.all())
     formazione.id = None
     formazione.save()
     for ref in referti:
         ref.id = None
         ref.formazione_id = formazione.id
         ref.save()
     return formazione
 def fantavoti(self, referti=None, redazione=None):
   """restituisce (calcolata_adesso, lista_giocatori) ove: calcolata_adesso e' True se l'ha ricalcolata o False se non ha fatto nulla,
   mentre lista_giocatori e' una lista di tuple (referto, ruolo) dei giocatori che sono scesi in campo. Nello stesso tempo
   imposta i referti. Il primo parametro e' False se non sono state effettuate modifiche."""
   if redazione is None:
           redazione = self.allenatore.lega.redazione
   if referti is None:
           referti = self.referto_set.order_by('posizione').select_related('voto').prefetch_related('calciatore__ruolo__redazione').all()
   if not(any([ref.da_ricalcolare for ref in referti])): # la formazione e' vuota o gia' aggiornata
           lista = [ (ref, filter(lambda x: x.redazione==redazione, ref.calciatore.ruolo.all())[0]) for ref in referti if ref.entrato_in_campo ]
           return (False, lista)
   referti.update(entrato_in_campo=False, modificatore=False)
   titolari = referti[0:11]
   riserve = referti[11:]
   riserve = filter(lambda x: x.ha_giocato, riserve) # filtro solo le riserve che hanno giocato
   # prima metto i titolari che hanno giocato
   lista_giocatori_totale = [ (tit, filter(lambda x: x.redazione==redazione,tit.calciatore.ruolo.all())[0]) for tit in titolari] # produco una lista di coppie (referto, ruolo), per i titolari
   lista_giocatori = filter(lambda x: x[0].ha_giocato, lista_giocatori_totale) # filtro quelli che hanno preso un voto
   riserve_ruolo = {}
   schierati_in_ruolo = {}
   giocano_in_ruolo = {}
   for ru in ruoli_lunghi.keys():
     riserve_ruolo[ru] = filter(lambda x: filter(lambda y: y.redazione==redazione, x.calciatore.ruolo.all())[0].nome==ru, riserve)
     schierati_in_ruolo[ru] = len(filter(lambda x: x[1].nome == ru, lista_giocatori_totale)) # conto i difensori schierati in formazione
     giocano_in_ruolo[ru] = len(filter(lambda x: x[1].nome == ru, lista_giocatori)) # conto i giocatori che giocano in ciascun ruolo
   riserve = filter(lambda x: filter(lambda y: y.redazione==redazione, x.calciatore.ruolo.all())[0].nome!='P', riserve)
 # escludo i portieri perche' non possono fare cambi ruolo...
   lista_da_sostituire =  filter(lambda x: x[0].ha_giocato is False, lista_giocatori_totale)   # lista di quelli che non hanno giocato
   for ref, ru in lista_da_sostituire[0:3]: # posso fare al piu' tre cambi
     print("cerco un sostituto per",ref.calciatore.nome)
     if (giocano_in_ruolo['A']>=3): # ci sono gia' 3 attaccanti, non possono piu' entrare, quindi svuoto le liste di attaccanti
           riserve = filter(lambda x: filter(lambda y: y.redazione==redazione, x.calciatore.ruolo.all())[0].nome!='A', riserve)
           riserve_ruolo['A'] = []
     if (riserve_ruolo[ru.nome]): # c'e' almeno una riserva di questo ruolo
        ris = riserve_ruolo[ru.nome].pop(0)
        print("ho trovato", ris.calciatore.nome)
        if (ru.nome!='P'):
            riserve.remove(ris)
        lista_giocatori.append((ris, ru))
        giocano_in_ruolo[ru.nome] += 1 # incremento di 1 quelli che giocano in questo ruolo
        continue
     print("Cerco un cambio ruolo")
     #non sono riuscito a sostituirlo con uno dello stesso ruolo, cerco un cambio ruolo
     if (ru == 'P'): # i portieri non fanno cambi ruolo
             continue
     if (ru == 'D' and giocano_in_ruolo[ru.nome] < 3): # se non ci sono almeno 3 difensori gia' in campo, non posso fare un cambio ruolo di difensori...
             continue
     if (riserve): # c'e' almeno una riserva disponibile, cerco un cambio ruolo
             ris = riserve.pop(0)
             print("Ho trovato", ris.calciatore.nome)
             ru_ris = filter(lambda x: x.redazione==redazione, ris.calciatore.ruolo.all())[0]
             giocano_in_ruolo[ru_ris.nome] += 1 # incremento di 1 quelli che giocano in questo ruolo
             riserve_ruolo[ru_ris.nome].remove(ris)
             lista_giocatori.append((ris, ru_ris))
   ref_entrati = [ref.id for (ref, ru) in lista_giocatori]
   ref_entrati = Referto.objects.filter(pk__in=ref_entrati).update(entrato_in_campo=True)
   port_o_dif_in_campo = [ref.id for (ref, ru) in lista_giocatori if ru.nome=='D' or ru.nome=='P']
   if ( schierati_in_ruolo['D']>3 and len(port_o_dif_in_campo) >= 5): # se ha schierati piu' di 3 difensori ed hanno giocato effettivamente piu' di 3, metto il flag modificatore
       Referto.objects.filter(pk__in=port_o_dif_in_campo).update(modificatore=True)
       for (ref, ru) in lista_giocatori:
               if(ref.id in port_o_dif_in_campo):
                       ref.modificatore = True # aggiorno il modificatore sulla copia locale
   referti.update(da_ricalcolare=False)
   return (True, lista_giocatori)


class GiornataLega(models.Model):
 giornata = models.ForeignKey(Giornata, blank=True, null=True, on_delete = models.CASCADE)
 lega = models.ForeignKey(Lega, on_delete = models.CASCADE)
 numero = models.PositiveSmallIntegerField() # numero della giornata nella lega
 def chiudi_giornata(self):
        incontricoppa = IncontroCoppa.objects.filter(incontro_ritorno__giornatalega=self).select_related('incontro_andata','incontro_ritorno') # seleziono i turni di coppa in cui di cui si e' giocato un ritorno in questa giornata
        if incontricoppa.count() == 0:
                return # non c'e' un ritorno di coppa, esco
        turnoattuale = incontricoppa[0].tipo
        indiceturno = nome_turni_coppa.index(turnoattuale)
        if indiceturno==0: # e' la finale, non ho niente da fare... esco (QUI SI PUO" INSERIRE LA PROCLAMAZIONE DEL VINCITORE DELLA COPPA
            return
        nuovo_turno = self.lega.incontrocoppa_set.filter(tipo=nome_turni_coppa[indiceturno-1])
        #for turno in nome_turni_coppa[::-1][1:]:  # cerco il prossimo turno
        #        nuovo_turno = self.lega.incontrocoppa_set.filter(tipo=turno)
        #        plnum = 2*nuovo_turno.count()
        #        if plnum>0:
        #                break
        if (incontricoppa[0].tipo == nome_turni_coppa[-1]):  # e' il ritorno del turno preliminare
                #allenatori = self.lega.allenatori_set.all()
                scarto_alle = {}
                media_alle = {}
                for inc in incontricoppa:
                        andata = inc.incontro_andata
                        ritorno = inc.incontro_ritorno
                        scarto_alle[andata.allenatorecasa.id] = andata.golcasa - andata.goltrasferta + ritorno.goltrasferta - ritorno.golcasa
                        scarto_alle[andata.allenatoretrasferta.id] = -(andata.golcasa - andata.goltrasferta + ritorno.goltrasferta - ritorno.golcasa)
                        media_alle[andata.allenatorecasa.id] = andata.fmcasa + ritorno.fmtrasferta
                        media_alle[andata.allenatoretrasferta.id] = andata.fmtrasferta + ritorno.fmcasa
                alle_id = sorted(scarto_alle.keys(), key=lambda x: (scarto_alle[x], media_alle[x])) # ordina le teste di serie : 0 il peggiore -1 il migliore
                alle_selected = alle_id[-plnum:] # vengono ripescati solo gli ultimi plnum
                teste_di_serie = alle_selected[-plnum/2:][::-1]
                sfidanti = alle_selected[:plnum/2]
                for (forte,scarso,inccoppa) in zip(teste_di_serie, sfidanti, nuovo_turno.all()):
                        inccoppa.setta_allenatori(scarso,forte)
        else: # non e' un turno preliminare
                for inc in nuovo_turno:
                        inc.setta_allenatori_da_incontri()






class Competizione(models.Model):
 lega = models.ForeignKey(Lega, on_delete = models.CASCADE) # lega a cui la competizione corrisponde
 nome = models.CharField(max_length=50) # nome della competizione
 descrizione = models.TextField(blank=True) # descrizione della competizione
 @property
 def ha_classifica(self):
   fasi = self.fasecompetizione_set
   return fasi.count()==1 and fasi.first().ha_classifica

class FaseCompetizione(models.Model):
  """E' una fase di una competizione, puo' essere a gironi o ad eliminazione diretta"""
  nome = models.CharField(max_length=50) # nome della fase
  tipo = models.CharField(max_length=10) # al momento sono supportati "girone" e "eldir" (eliminazione diretta)
  competizione = models.ForeignKey(Competizione, on_delete = models.CASCADE) # competizione a cui la fase corrisponde
  descrizione = models.TextField(default='{"vincitore_pareggio": "classifica"}') # descrizione della competizione
  @property
  def nomecompleto(self):
     return self.competizione.nome + ": " + self.nome
  @property
  def isgirone(self):
      return self.tipo == "girone"
  @property
  def ha_classifica(self):
      return self.isgirone
  @property
  def descrizione_dict(self):
     return json.loads(self.descrizione)
  @staticmethod
  def classifica_da_incontri(incontri):
           """ restituisce la classifica da un set di incontri, non ha a che vedere con il modello FaseCompetizione ma lo metto qui per ordine logico"""
           dati_allenatori = {}
           class Dati_Allenatore:
	        punti = 0
	        giocate = 0
	        vinte = 0
	        patte = 0
	        sconfitte = 0
	        rf = 0
	        rs = 0
	        fm = 0
           for inc in incontri:
              if inc.allenatorecasa not in dati_allenatori.keys():
	              dati_allenatori[inc.allenatorecasa] = Dati_Allenatore()
              if inc.allenatoretrasferta not in dati_allenatori.keys():
	              dati_allenatori[inc.allenatoretrasferta] = Dati_Allenatore()
              if not inc.disputato:
              	continue
              dati_allenatori[inc.allenatorecasa].giocate +=  1
              dati_allenatori[inc.allenatoretrasferta].giocate +=  1
              dati_allenatori[inc.allenatorecasa].rf +=  inc.golcasa
              dati_allenatori[inc.allenatorecasa].rs +=  inc.goltrasferta
              dati_allenatori[inc.allenatoretrasferta].rf +=  inc.goltrasferta
              dati_allenatori[inc.allenatoretrasferta].rs +=  inc.golcasa
              dati_allenatori[inc.allenatorecasa].fm +=  inc.fmcasa
              dati_allenatori[inc.allenatoretrasferta].fm +=  inc.fmtrasferta
              if (inc.golcasa > inc.goltrasferta):
	              dati_allenatori[inc.allenatorecasa].vinte +=  1
                      dati_allenatori[inc.allenatoretrasferta].sconfitte +=  1
              elif (inc.golcasa == inc.goltrasferta):
	              dati_allenatori[inc.allenatorecasa].patte +=  1
                      dati_allenatori[inc.allenatoretrasferta].patte +=  1
              else:
	              dati_allenatori[inc.allenatorecasa].sconfitte +=  1
                      dati_allenatori[inc.allenatoretrasferta].vinte +=  1
           for alle in dati_allenatori.keys():
	           if dati_allenatori[alle].giocate:
	           	dati_allenatori[alle].fm /= dati_allenatori[alle].giocate
	           dati_allenatori[alle].punti = 3*dati_allenatori[alle].vinte + dati_allenatori[alle].patte
           dati_allenatori = sorted(dati_allenatori.items(), key=lambda x: (-x[1].punti, -x[1].fm))
           return dati_allenatori
  def restituisci_indice(self, indice):
      """restituisce l'allenatore corrispondente all'indice; se e' un girone, indice e' la posizione in classifica (0 per primo), altrimenti e'
      l'indice dell'incontro"""
      if self.isgirone:
        incontri = self.incontrolega_set.all()
        indice = int(indice) # converto l'indice in un intero corrispondente alla posizione in classifica 0(primo)...n-1(ultimo)
        classifica = self.classifica_da_incontri(incontri)
        #print classifica
        #print classifica[indice].key()
        return classifica[indice][0]
      if self.tipo=="elidir": # eliminazione diretta
        indice = str(indice)
        perdente = False
        if indice.endswith("p"):
                indice = indice[0:-1]  # tolgo la p come ultimo carattere che simboleggia il fatto che si debba prendere il perdente
                perdente = True
        incontro = self.incontrocoppa_set.get(pk=indice)
        if perdente:
                return incontro.sconfitto
        return incontro.vincitore


class PremioCompetizione(models.Model):
  """E' un premio per una competizione"""
  nome = models.CharField(max_length=50) # nome della fase
  competizione = models.ForeignKey(Competizione, on_delete = models.CASCADE) # competizione a cui la fase corrisponde
  allenatore = models.ForeignKey(Allenatore, blank=True, null=True) # allenatore vincitore del premio
  faseoriginale = models.ForeignKey(FaseCompetizione, blank=True, null=True, on_delete = models.CASCADE) # fase da cui dipende l'allenatore trasferta
  descrizione = models.CharField(max_length=10) # stringa che determina come ottenere allenatore dalla faseoriginale
  giornata = models.ForeignKey(Giornata, on_delete = models.CASCADE, blank=True, null=True) # giornata del campionato alla cui conclusione viene assegnato il premio
  def assegna_premio(self):
      """imposta l'allenatore che ha vinto il premio"""
      print "Provo ad assegnare un premio per ", self.nome
      if (self.allenatore is None): # se non e' None non c'e' niente da fare
                print "Imposto l'allenatore"
                self.allenatore = self.faseoriginale.restituisci_indice(self.descrizione)
                print "l'allenatore e'", self.allenatore 
                self.save()
                lega = self.faseoriginale.competizione.lega
         	msg = Messaggio(lega=lega, testo=("La squadra di %s e' stata proclamata: %s" % (self.allenatore.nome, self.nome)))
                msg.save()





class IncontroLega(models.Model):
 """ si riferisce ad un incontro disputato tra due fantasquadre all'interno della lega """
 allenatorecasa = models.ForeignKey(Allenatore, blank=True, null=True, related_name="IncontroCasa", on_delete = models.CASCADE) # allenatore della squadra di casa
 allenatoretrasferta = models.ForeignKey(Allenatore,  blank=True, null=True, related_name="IncontroTrasferta", on_delete = models.CASCADE) # allenatore della squadra in trasferta
 formazionecasa = models.OneToOneField(Formazione, blank=True, null=True, related_name="IncontroCasa", on_delete = models.CASCADE) # formazione della squadra in casa
 formazionetrasferta = models.OneToOneField(Formazione, blank=True, null=True, related_name="IncontroTrasferta", on_delete = models.CASCADE) # formazione della squadra in trasferta
 fase =  models.ForeignKey(FaseCompetizione, blank=True, null=True, on_delete = models.CASCADE) # fase della competizione a cui l'incontro corrisponde
 faseoriginalecasa = models.ForeignKey(FaseCompetizione, blank=True, null=True, on_delete = models.CASCADE, related_name="faseoriginalecasa") # fase da cui dipende l'allenatore casa
 faseoriginaletrasferta = models.ForeignKey(FaseCompetizione, blank=True, null=True, on_delete = models.CASCADE, related_name="faseoriginaletrasferta") # fase da cui dipende l'allenatore trasferta
 descrizioneincontri = models.CharField(max_length=10) # stringa che determina come ottenere allenatorecasa e trasferta dalla fase
 giornata = models.ForeignKey(Giornata, on_delete = models.CASCADE) # giornata del campionato
 fmcasa_nomod = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 fmtrasferta_nomod = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 modcasa = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 modtrasferta = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 def setta_allenatori(self):
   """imposta gli allenatori usando la descrizioneincontri"""
   if self.allenatorecasa is None:
        indicecasa = self.descrizioneincontri.split(",")[0]
        self.allenatorecasa = self.faseoriginalecasa.restituisci_indice(indicecasa)
   if self.allenatoretrasferta is None:
        indicetrasferta = self.descrizioneincontri.split(",")[1]
        self.allenatoretrasferta = self.faseoriginaletrasferta.restituisci_indice(indicetrasferta)
   self.save()
 def __unicode__(self):
   if self.allenatorecasa is not None and self.allenatoretrasferta is not None:
     return self.allenatorecasa.__unicode__() + " - " + self.allenatoretrasferta.__unicode__()
   else:
     return "da definire - da definire"
 def short(self):
   return self.allenatorecasa.__unicode__().replace(" ", "").replace(".","")[0:3] + " - " + self.allenatoretrasferta.__unicode__().replace(" ","").replace(".","")[0:3]
 @property
 def lega(self):
    if self.fase is not None:
            return self.fase.competizione.lega
    else:
            return None
 @property
 def disputato(self):
    if self.giornata.disputata:
        return True
    if (self.fmcasa==0.0 or self.fmtrasferta==0.0):
        return False
    return True
 def aggiorna_incontro(self, refertocasa=None, refertotrasferta=None, redazione=None, aggiorna_comunque=False):
    formazioni = [self.formazionecasa, self.formazionetrasferta]
    referti_formazioni = [refertocasa, refertotrasferta]
    redazione = self.lega.redazione if self.lega is not None else ( self.IncontroCoppaAnd.fase.competizione.lega.redazione if hasattr(self, 'IncontroCoppaAnd') else None)
    modificatori = [0.0,0.0]
    fm = [0.0,0.0]
    da_aggiornare = aggiorna_comunque
    calcolata_adesso = [False, False]
    liste_giocatori = [None, None]
    for ind,formazione in enumerate(formazioni):
        if(formazione):
            (calcolata_adesso[ind], liste_giocatori[ind]) = formazione.fantavoti(referti_formazioni[ind], redazione)
            if da_aggiornare or calcolata_adesso[ind]:
                conta_difensori = 0 # indice per contare quanti difensori ho gia' considerato
                lista_difensori = [] # contiene tutti i difensori
                for (ref, ru) in liste_giocatori[ind]:
                    fm[ind] = fm[ind] + ref.fantavoto
                    if(ref.modificatore):
                        modificatori[ind] = modificatori[ind] + ref.votopuro
                        if ru.nome=='D':
                            conta_difensori = conta_difensori+1
                            lista_difensori.append(ref.votopuro)
                lista_difensori.sort()
                lista_difensori.reverse()
                min_difensori = sum(lista_difensori[3:]) # contiene il totale dei difensori oltre il terzo
                conta_difensori = 4 # 3 difensori piu il portiere
                modificatori[ind] = 0 if conta_difensori == 0 else (modificatori[ind]-min_difensori)/conta_difensori # prendo la media togliendo il minimo difensore (include il portiere)
                modificatori[ind] = math.floor((modificatori[ind]-6.0)/0.5)*3
                modificatori[ind] = 1.0 if modificatori[ind]==0 else max(modificatori[ind],0)  # modificatore fa 1 se la media sta tra
                if ind == 0:
                    self.modcasa = modificatori[ind]
                    self.fmcasa_nomod = fm[ind]
                else:
                    self.modtrasferta = modificatori[ind]
                    self.fmtrasferta_nomod = fm[ind]
    if any(calcolata_adesso) or da_aggiornare:
        self.save()
    return (da_aggiornare, liste_giocatori)
 @property
 def fmcasa(self):
    return float(self.fmcasa_nomod) - float(self.modtrasferta) + 1.0
 @property
 def fmtrasferta(self):
    return float(self.fmtrasferta_nomod) - float(self.modcasa)
 @property
 def golcasa(self):
    return int(max(0, math.floor((float(self.fmcasa) - 66.0)/6.0)+1))
 @property
 def goltrasferta(self):
    return int(max(0, math.floor((float(self.fmtrasferta) - 66.0)/6.0)+1))
 @property
 def descrizioneinversa(self):
     """restituisce la descrizione degli incontri (usata per calcolare allenatore_casa e allenatore_trasferta scambiando andata e ritorno"""
     a,r = self.descrizioneincontri.split(",")
     return ",".join((r,a))
 @property
 def allenatorecasanome(self):
     """da' il nome dell'allenatore della squadra di casa se e' definito se no da' qualcos'altro (es. da stabilire)"""
     if self.allenatorecasa is not None:
        return self.allenatorecasa.__unicode__()
     return "da stabilire"
 @property
 def allenatoretrasfertanome(self):
     """da' il nome dell'allenatore della squadra di casa se e' definito se no da' qualcos'altro (es. da stabilire)"""
     if self.allenatoretrasferta is not None:
        return self.allenatoretrasferta.__unicode__()
     return "da stabilire"
 def scambia_andata_ritorno(self):
     """restituisce un nuovo oggetto IncontroLega con """
     nuovoincontro = IncontroLega(allenatorecasa = self.allenatoretrasferta,
                     allenatoretrasferta = self.allenatorecasa, fase=self.fase, faseoriginalecasa = self.faseoriginaletrasferta,
                     faseoriginaletrasferta = self.faseoriginalecasa, giornata=self.giornata, descrizioneincontri = self.descrizioneinversa)
     return nuovoincontro


class IncontroCoppa(models.Model):
  """ si riferisce ad un incontro di coppa con andata e ritorno. Se i due allenatori sono settati, si sa gia' chi la disputera' e si comporta quindi come un incontro di lega
      se invece sono settati gli incontri, vuol dire che a disputarla saranno i vincenti dei due incontri, una volta disputati"""
  incontrocasa = models.ForeignKey("self", related_name="QualificataCasaPer", blank=True, null=True, on_delete = models.CASCADE) # deprecated
  incontrotrasferta = models.ForeignKey("self", related_name="QualificataTrasfertaPer", blank=True, null=True, on_delete = models.CASCADE) # deprecated
  incontro_andata = models.OneToOneField(IncontroLega, blank=True, null=True, related_name="IncontroCoppaAnd", on_delete = models.CASCADE) # incontro per il match d'andata
  incontro_ritorno = models.OneToOneField(IncontroLega, blank=True, null=True, related_name="IncontroCoppaRit", on_delete = models.CASCADE) # incontro per il match d'andata
  fase =  models.ForeignKey(FaseCompetizione, on_delete = models.CASCADE) # fase della competizione a cui l'incontro corrisponde
  andata_ritorno = models.BooleanField(default=True) # specifica se il turno contiene andata e ritorno, se e' false i ritorni saranno nulli
  @property
  def lega(self):
    return self.fase.competizione.lega
  @classmethod
  def create(cls, allenatorecasa, allenatoretrasferta, giornata_andata, giornata_ritorno, **kwargs):
       inclega_andata = IncontroLega(allenatorecasa=allenatorecasa, allenatoretrasferta=allenatoretrasferta, giornata=giornata_andata)
       inclega_andata.save()
       inclega_ritorno = None
       if giornata_ritorno is not None:
         inclega_ritorno = IncontroLega(allenatorecasa=allenatoretrasferta, allenatoretrasferta=allenatorecasa, giornata=giornata_ritorno)
         inclega_ritorno.save()
       inc = cls(incontro_andata = inclega_andata, incontro_ritorno=inclega_ritorno, **kwargs); # preliminare
       return inc
  @property
  def allenatorecasanome(self):
    if (self.incontro_andata is not None):
                    return self.incontro_andata.allenatorecasanome
    return "da stabilire"
  @property
  def allenatoretrasfertanome(self):
    if (self.incontro_andata is not None):
            return self.incontro_andata.allenatoretrasfertanome
    return "da stabilire"
  def setta_allenatori(self): # imposta l'allenatore che gioca in casa/trasferta l'andata DEPRECATED
    self.incontro_andata.setta_allenatori()
    if(self.incontro_ritorno):
            self.incontro_ritorno.setta_allenatori()
  @property
  def vincitore(self):
    scarto = self.incontro_andata.golcasa + self.incontro_ritorno.goltrasferta - self.incontro_andata.goltrasferta - self.incontro_ritorno.golcasa
    if scarto>0:
        return self.incontro_andata.allenatorecasa
    elif scarto<0:
        return self.incontro_andata.allenatoretrasferta
    else: # qui ci andrebbero i RIGORI!!! invece ci metto confronto fantamedie
            scelta = self.fase.descrizione_dict['vincitore_pareggio'] # come gestire il vincitore in caso di parita'
            if scelta=='classifica': # prende il migliore in classifica
                lega = self.fase.competizione.lega
                fase = FaseCompetizione.objects.filter(competizione__lega=lega.id).filter(tipo="girone").order_by('id')[0]  # cerco il girone principale (primo per id) nella stessa lega
                classi = fase.classifica_da_incontri(fase.incontrolega_set.all())
                alle1 = self.incontro_andata.allenatorecasa
                alle2 = self.incontro_andata.allenatoretrasferta
                indice1 = [ind for ind,(x,i) in enumerate(classi) if x==alle1]
                if len(indice1) == 0:
                        return alle2
                indice2 = [ind for ind,(x,i) in enumerate(classi) if x==alle2]
                if len(indice2) == 0:
                        return alle1
                if indice1[0] < indice2[0]:
                        return alle1
                return alle2
            if scelta=='fantamedia': # prende la migliore fantamedia
                    scartofm = self.incontro_andata.fmcasa + self.incontro_ritorno.fmtrasferta - self.incontro_andata.fmtrasferta - self.incontro_ritorno.fmcasa
                    if scartofm>0:
                        return self.incontro_andata.allenatorecasa
                    elif scartofm<0:
                        return self.incontro_andata.allenatoretrasferta
    return None  # qui arriva solo nel caso sfigatissimo che abbiano le stesse fantamedie e gli stessi gol fatti
  @property
  def sconfitto(self):  # restituisce l'allenatore che non e' vincitore
     vinc = self.vincitore
     if self.incontro_andata.allenatorecasa == vinc:
        return self.incontro_andata.allenatoretrasferta
     return self.incontro_andata.allenatorecasa
  def __unicode__(self):
    return self.allenatorecasanome + " - " + self.allenatoretrasfertanome
  @property
  def giornate_coinvolte(self):
     giorns = [self.incontro_andata.giornata.numero]
     if self.andata_ritorno:
             giorns = giorns + [self.incontro_ritorno.giornata.numero]
     return tuple(giorns)


@receiver(post_delete, sender=IncontroCoppa)
def my_handler(sender, instance, **kwargs):
   if instance.incontro_andata is not None:
           instance.incontro_andata.delete()
   if instance.incontro_ritorno is not None:
           instance.incontro_ritorno.delete()

class Voto(models.Model):
  """Voto ricevuto da un calciatore in una certa giornata; contiene le informazioni sul voto puro e gli altri dati; il supporto per differenti redazioni e'
  inserito tramite la variabile redazione """
  redazione = models.ForeignKey(Redazione, on_delete = models.CASCADE)
  giornata = models.ForeignKey(Giornata, on_delete = models.CASCADE)
  calciatore = models.ForeignKey(Calciatore, on_delete = models.CASCADE)
  votopuro = models.DecimalField(default=6.0, max_digits=4, decimal_places = 2)
  assist =  models.PositiveSmallIntegerField(default=0)
  golsuazione = models.PositiveSmallIntegerField(default=0)
  golsurigore =  models.PositiveSmallIntegerField(default=0)
  ammo = models.PositiveSmallIntegerField(default=0)
  espu =  models.PositiveSmallIntegerField(default=0)
  autogol =  models.PositiveSmallIntegerField(default=0)
  golsubiti =  models.PositiveSmallIntegerField(default=0)
  rigorisbagliati =  models.PositiveSmallIntegerField(default=0)
  rigoriparati = models.PositiveSmallIntegerField(default=0)
  goldellavittoria =  models.PositiveSmallIntegerField(default=0)
  goldelpareggio =  models.PositiveSmallIntegerField(default=0)
  ha_giocato = models.BooleanField(default = False)
  def aggiorna_referti(self):
    refs = Referto.objects.filter(calciatore=self.calciatore, formazione__giornata=self.giornata, formazione__allenatore__lega__redazione=self.redazione).update(da_ricalcolare=True)
  def save(self, *args, **kwargs):
          super(Voto, self).save(*args, **kwargs)
          self.aggiorna_referti()




class Referto(models.Model):
  formazione = models.ForeignKey(Formazione, on_delete=models.CASCADE)
  calciatore = models.ForeignKey(Calciatore, on_delete=models.CASCADE)
  posizione = models.PositiveSmallIntegerField() # posizione in campo; i titolari sono da 1 a 11; gli altri sono panchinari. E' usato per ottenere i voti della squadra
  voto = models.ForeignKey(Voto, blank=True, null=True, on_delete = models.CASCADE)
  votopuro_db = models.DecimalField(max_digits=4, decimal_places = 2, blank=True, null=True)
  entrato_in_campo = models.BooleanField(default=False)  # viene settato dalla funzione fantavoti di Formazione e dice se il giocatore schierato e' effettivamente andato a voto
  modificatore = models.BooleanField(default=False) # se e' True il giocatore e' stato coinvolto in un modificatore
  fantavoto_db = models.DecimalField(max_digits=4, decimal_places = 2, blank=True, null=True)
  da_ricalcolare = models.BooleanField(default = True) # quando i voti vengono a giornare, questo flag diventa True, indicando che la formazone associata va ricalcolata
  non_ha_giocato = models.BooleanField(default=False) # se e' true, non ha giocato indipendentemente da voto; se e' false guarda il voto
  class Meta:
     ordering = ['posizione']
  def save(self, *args, **kwargs):
    if self.calciatore.primavera:
      ruolo = self.calciatore.ruolo.all()[0] # prendo un ruolo di una qualunque redazione
      self.votopuro_db = votoprimavera[ruolo.nome]
      self.fantavoto_db = votoprimavera[ruolo.nome]
      self.voto = None
    elif (not(self.id) or (not(self.voto) and not(self.calciatore.primavera)) or  self.voto.calciatore_id != self.calciatore_id): # se il referto non e' associato ad un voto o se il calciatore del voto non coincide con quello del referto, cambio l'associazione
      redazione = self.formazione.allenatore.lega.redazione
      voto, created = Voto.objects.get_or_create(redazione=redazione, calciatore_id=self.calciatore_id, giornata=self.formazione.giornata)
      self.voto = voto
    super(Referto, self).save(*args, **kwargs)
  @property
  def votopuro(self):
    """se il voto e' scritto nel referto, lo uso, altrimenti lo prendo dall'oggetto Voto collegato"""
    if(self.votopuro_db):
            return float(self.votopuro_db)
    return float(self.voto.votopuro)
  @property
  def fantavoto(self):
    if(self.fantavoto_db):
            return float(self.fantavoto_db)
    return getattr(fantafun, self.formazione.allenatore.lega.calcolo_voto)(self.voto)
  @property
  def ha_giocato(self):
    if (self.non_ha_giocato):
            return False
    if (self.fantavoto_db is not None):
            return True
    return self.voto.ha_giocato



