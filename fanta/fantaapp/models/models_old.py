
nome_turni_coppa = [u'Finale', u'Semifinale', u'Quarti', u'Ottavi', u'Sedicesimi', u'Trentaduesimi', u'Sessantaquattresimi', u'Turno Preliminare']
votoprimavera = {'P': 3.5, 'D':4.5, 'C':4.5, 'A':4.5}
ruoli_lunghi = {'P': "Portiere", 'D':"Difensore", 'C':"Centrocampista", 'A':"Attaccante"}
ruoli_lunghi_plurali = {'P': "Portieri", 'D':"Difensori", 'C':"Centrocampisti", 'A':"Attaccanti"}

def randomHash():
   N = 12
   return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(N))

def lastCampionato():
   return Campionato.objects.latest('id').id

class Redazione(models.Model):
 nome = models.CharField(max_length=50) # nome della redazione
 descrizione = models.TextField() # descrizione del funzionamento della redazione
 def __unicode__(self):
    return self.nome

class Campionato(models.Model):
  """Si riferisce ad un campionato nazionale, e.g. Serie A, Liga..."""
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
 con_coppa = models.BooleanField(default=True)
 redazione = models.ForeignKey(Redazione)
 campionato = models.ForeignKey(Campionato, default=lastCampionato)
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
 def genera_calendario(self):
   """genera tutti gli accoppiamenti del torneo"""
   if (self.giornatalega_set.count()>0):
	  raise ValueError("Il set delle giornate non e' vuoto! " + str(self.giornatalega_set.count()) + " incontri gia' presenti")
   if ((self.numeropartecipanti - 1)*self.numero_gironi > self.campionato.giornate_da_disputare):
      self.numero_gironi = math.floor(self.campionato.giornate_da_disputare/(self.numeropartecipanti - 1))
      if (self.numero_gironi==0):
	      raise ValueError('Non ci sono sufficienti giornate nel campionato per generare almeno un girone.')
   allenatori = list(self.allenatore_set.all()) #ottengo la lista di allenatori della lega
   if len(allenatori)<self.numeropartecipanti: # se gli allenatori iscritti alla lega sono meno del numero di partecipanti fissato per la lega, la lega e' incompleta
     raise ValueError("Numero di allenatori non sufficiente a riempire la lega: %d." % (len(allenatori)))
   random.shuffle(allenatori) # mischio gli allenatori
   rr = roundRobin(allenatori) # genero gli accoppiamenti di tutte le giornate
   if (self.numero_gironi%2 == 0): # se il numero di gironi e' pari tengo conto di casa e fuori casa
	   rr1 = [[ (x[1], x[0]) for x in giornata] for giornata in rr]
	   accoppiamenti = (rr+rr1)*(self.numero_gironi/2)
   else:
	   accoppiamenti = rr*self.numero_gironi
   for g, giornata in enumerate(accoppiamenti):
     giornata_new = GiornataLega(lega=self,numero=(g+1))
     giornata_new.save()
     for acc in giornata:
	  if(acc[0] is None or acc[1] is None): # e' un incontro fittizio in cui una squadra riposa
		  continue
	  inc = IncontroLega(allenatorecasa=acc[0], allenatoretrasferta=acc[1], lega=self, giornatalega=giornata_new)
          inc.save()
 def genera_coppa(self):
   if (self.giornatalega_set.count() < self.totale_giornate()):
	   raise ValueError("Un numero insufficiente di giornate e' presente. Avvia la generazione del calendario prima.")
   if (self.incontrocoppa_set.count()>0):
	  raise ValueError("Il set delle giornate non e' vuoto! " + str(self.incontrocoppa_set.count()) + " incontri gia' presenti")
   allenatori = list(self.allenatore_set.all()) #ottengo la lista di allenatori della lega
   if len(allenatori)<self.numeropartecipanti: # se gli allenatori iscritti alla lega sono meno del numero di partecipanti fissato per la lega, la lega e' incompleta
     raise ValueError("Numero di allenatori non sufficiente a riempire la lega: %d." % (len(allenatori)))
   random.shuffle(allenatori) # mischio gli allenatori
   numero_turni = int(math.log(self.numeropartecipanti,2)) # numero turni da disputare, piu' eventualmente il preliminare
   turni_da_disputare = numero_turni
   numero_partite = 2*(numero_turni - 1) + 1 # i turni sono andata e ritorno tranne la finale
   turno_prec = []
   turno_curr = []
   if (2**numero_turni<self.numeropartecipanti): # il turno preliminare e' necessario
     numero_partite = numero_partite + 2 # si aggiungono i due turni preliminari
     gap_giornate = self.totale_giornate()/numero_partite # ogni quante giornate di campionato se ne disputa una di coppa
     numero_giornata_corrente = gap_giornate - 1 + (self.totale_giornate()% numero_partite) # voglio che la finale si disputi alla penultima giornata
     giornata_coppa_1 = self.giornatalega_set.get(numero=numero_giornata_corrente)                # giornata dell'andata
     giornata_coppa_2 = self.giornatalega_set.get(numero=(numero_giornata_corrente+gap_giornate)) # giornata del ritorno
     for m,(x,y) in enumerate(izip(allenatori, allenatori[(len(allenatori)+1)/2:])): #creo il turno preliminare sorteggiando a caso delle coppie
       inc = IncontroCoppa.create(x,y, giornata_coppa_1, giornata_coppa_2, lega=self, tipo=nome_turni_coppa[-1], indice=(m+1)); # preliminare
       inc.save()
     numero_giornata_corrente = numero_giornata_corrente + 2*gap_giornate # incremento di due giornate, i turni preliminari gia' considerati
     giornata_coppa_1 = self.giornatalega_set.get(numero=numero_giornata_corrente)                # giornata dell'andata
     giornata_coppa_2 = self.giornatalega_set.get(numero=(numero_giornata_corrente+gap_giornate)) # giornata del ritorno
     for m in range(2**(turni_da_disputare-1)): #creo il primo turno eliminatorio
       inc = IncontroCoppa.create(None,None, giornata_coppa_1, giornata_coppa_2, lega=self, tipo=nome_turni_coppa[turni_da_disputare-1], indice=(m+1)); # preliminare
       turno_curr.append(inc)
       inc.save()
   else:
     gap_giornate = self.totale_giornate()/numero_partite # ogni quante giornate di campionato se ne disputa una di coppa
     numero_giornata_corrente = gap_giornate - 1 + (self.totale_giornate()% numero_partite) # voglio che la finale si disputi alla penultima giornata
     giornata_coppa_1 = self.giornatalega_set.get(numero=numero_giornata_corrente)                # giornata dell'andata
     giornata_coppa_2 = self.giornatalega_set.get(numero=(numero_giornata_corrente+gap_giornate)) # giornata del ritorno
     for m,(x,y) in izip(allenatori, allenatori[len(allenatori)/2+1:]): #creo il primo turno eliminatorio sorteggiando a caso delle coppie
       inc = IncontroCoppa.create(x,y, giornata_coppa_1, giornata_coppa_2, lega=self, tipo=nome_turni_coppa[turni_da_disputare-1], indice=(m+1)); # preliminare
       inc.save()
       turno_curr.append(inc)
   turni_da_disputare = turni_da_disputare - 1
   print "turni da disp", turni_da_disputare
   for turno in range(turni_da_disputare):
     numero_giornata_corrente = numero_giornata_corrente + 2*gap_giornate # incremento di due giornate, che riguardano il turno precedente
     print numero_giornata_corrente
     giornata_coppa_1 = self.giornatalega_set.get(numero=numero_giornata_corrente)                # giornata dell'andata
     if(turno!=turni_da_disputare-1): # se non sono alla finale...
	     giornata_coppa_2 = self.giornatalega_set.get(numero=(numero_giornata_corrente+gap_giornate)) # giornata del ritorno
     else:
	     giornata_coppa_2 = None
     turno_prec = turno_curr
     turno_curr = []
     for m,(inc1,inc2) in enumerate(izip(turno_prec, turno_prec[(len(turno_prec)+1)/2:])): #creo il turno preliminare sorteggiando a caso delle coppie
       inc = IncontroCoppa.create(None,None,giornata_coppa_1, giornata_coppa_2, incontrocasa=inc1, incontrotrasferta=inc2, lega=self,
       tipo=nome_turni_coppa[turni_da_disputare-1-turno], indice=(m+1)); # turno eliminatorio
       turno_curr.append(inc)
       inc.save()
   [incontro_finale] = turno_curr
   incontro_finale.andata_e_ritorno = False
   incontro_finale.save()

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
 utente = models.ForeignKey(settings.AUTH_USER_MODEL) #utente corrispondente a quest'allenatore/squadra
 lega = models.ForeignKey(Lega)
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
        print tr
        ru = tr.calciatore.ruolo.get(redazione=self.lega.redazione).nome
        if tr.acquisto:
	      print 'acquisto'
	      rosa_dict[ru].append((tr.calciatore, tr.valore))
        else:
	      print 'cessione'
	      rosa_dict[ru] = [x for x in rosa_dict[ru] if x[0].id != tr.calciatore.id]
	      print rosa_dict[ru]
    return rosa_dict
 def __unicode__(self):
    return self.nomesquadra



class Messaggio(models.Model):
  """Contiene i messaggi su cio' che accade nella lega e ai singoli allenatori"""
  lega = models.ForeignKey(Lega) # lega del messaggio
  allenatore = models.ForeignKey(Allenatore, blank=True, null=True) # destinatario del messaggio, se None e' per tutti
  testo = models.CharField(max_length=200) # testo del messaggio
  data = models.DateTimeField(auto_now=True) # data del messaggio
  @property
  def datatesto(self):
        return self.data.strftime("%d-%m-%Y, %H:%M. ") + self.testo
  def __unicode__(self):
 	return self.datatesto

class SquadraCampionato(models.Model):
  """Si riferisce ad una vera squadra nel campionato"""
  nome = models.CharField(max_length=50) # nome della squadra
  campionato = models.ForeignKey(Campionato) # campionato di appartenenza
  def __unicode__(self):
    return self.nome.title()




class Giornata(models.Model):
  """Si riferisce ad una giornata di un campionato reale"""
  campionato = models.ForeignKey(Campionato)
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
      self.data = data
      self.save()
  def __unicode__(self):
    return "Giornata %d" % self.numero


class IncontroCampionato(models.Model):
  """Si riferisce ad un vero incontro disputato tra due squadre del campionato"""
  data = models.DateTimeField(auto_now_add=True) #data d'inizio dell'incontro
  giornata = models.ForeignKey(Giornata) # giornata a cui l'incontro appartiene
  squadracasa = models.ForeignKey(SquadraCampionato, related_name="IncontroCasa") #squadra che gioca in casa
  squadratrasferta = models.ForeignKey(SquadraCampionato, related_name="IncontroTransferta") #squadra che gioca in trasferta
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
 nome = models.CharField(max_length=40)
 primavera = models.BooleanField(default=False)
 squadra = models.ForeignKey(SquadraCampionato, blank=True, null=True)
 scorsoanno = models.ForeignKey('self',  blank=True, null=True) # altro oggetto calciatore corrispondente a se stesso l'anno prima
 #i seguenti sono dati statistici relativi all'anno precedente, usati nella visualizzazione in fase d'asta
 exsquadra = models.CharField(max_length=40)
 quotazione = models.PositiveSmallIntegerField(blank=True, null=True)
 fantamedia = models.FloatField(blank=True, null=True)
 fantamediasq = models.FloatField(blank=True, null=True)
 mediavoto = models.FloatField(blank=True, null=True)
 presenze = models.PositiveSmallIntegerField(blank=True, null=True)
 golfatti = models.PositiveSmallIntegerField(blank=True, null=True)
 golsubiti = models.PositiveSmallIntegerField(blank=True, null=True)
 rigoriparati = models.PositiveSmallIntegerField(blank=True, null=True)
 ammonizioni = models.PositiveSmallIntegerField(blank=True, null=True)
 espulsioni = models.PositiveSmallIntegerField(blank=True, null=True)
 assist = models.PositiveSmallIntegerField(blank=True, null=True)
 imageurl = models.URLField(blank=True, null=True) # url con un'immagine del giocatore
 def save(self, *args, **kwargs):
   if self.primavera:
       ru = self.ruolo.first().nome
       self.nome = 'Primavera '  + ru
       self.exsquadra = ''
       self.squadra = None
   return super(Calciatore, self).save(*args, **kwargs)
 def __unicode__(self):
    return self.nome.title()


class Ruolo(models.Model):
  calciatore = models.ForeignKey(Calciatore, related_name='ruolo')
  redazione = models.ForeignKey(Redazione)
  nome = models.CharField(max_length=5) # stringa indicante il ruolo
  @property
  def nome_lungo(self):
     return ruoli_lunghi[self.nome]

class Formazione(models.Model):
 """contiene la formazione inviata da un allenatore"""
 giocatori = models.ManyToManyField(Calciatore, through='Referto')
 allenatore = models.ForeignKey(Allenatore)
 data_invio = models.DateTimeField() #data d'invio della formazione
 definitiva = models.BooleanField(default=False) # se la formazione e' definitiva, perche' per esempio riguarda match gia' cominciati
 giornata = models.ForeignKey(Giornata) # tutte le partite che corrispondono a questa giornata
 modulo = models.CharField(max_length=5, default = '4,4,2', validators=[validate_comma_separated_integer_list]) # modulo tipo '4,4,2'
 #modulo = models.CommaSeparatedIntegerField(max_length=5, default='4,4,2')
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
   print >>sys.stderr, "lista giocatori totale"
   print >>sys.stderr, lista_giocatori_totale
   lista_giocatori = filter(lambda x: x[0].ha_giocato, lista_giocatori_totale) # filtro quelli che hanno preso un voto
   print >>sys.stderr, "lista giocatori in campo"
   print >>sys.stderr, lista_giocatori
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
     print "cerco un sostituto per",ref.calciatore.nome
     if (giocano_in_ruolo['A']>=3): # ci sono gia' 3 attaccanti, non possono piu' entrare, quindi svuoto le liste di attaccanti
	   riserve = filter(lambda x: filter(lambda y: y.redazione==redazione, x.calciatore.ruolo.all())[0].nome!='A', riserve)
	   riserve_ruolo['A'] = []
     if (riserve_ruolo[ru.nome]): # c'e' almeno una riserva di questo ruolo
        ris = riserve_ruolo[ru.nome].pop(0)
        print "ho trovato", ris.calciatore.nome
        if (ru.nome!='P'):
            riserve.remove(ris)
        lista_giocatori.append((ris, ru))
        giocano_in_ruolo[ru.nome] += 1 # incremento di 1 quelli che giocano in questo ruolo
        continue
     print "Cerco un cambio ruolo"
     #non sono riuscito a sostituirlo con uno dello stesso ruolo, cerco un cambio ruolo
     if (ru == 'P'): # i portieri non fanno cambi ruolo
	     continue
     if (ru == 'D' and giocano_in_ruolo[ru.nome] < 3): # se non ci sono almeno 3 difensori gia' in campo, non posso fare un cambio ruolo di difensori...
	     continue
     if (riserve): # c'e' almeno una riserva disponibile, cerco un cambio ruolo
             ris = riserve.pop(0)
             print "Ho trovato", ris.calciatore.nome
             ru_ris = filter(lambda x: x.redazione==redazione, ris.calciatore.ruolo.all())[0]
	     giocano_in_ruolo[ru_ris.nome] += 1 # incremento di 1 quelli che giocano in questo ruolo
	     riserve_ruolo[ru_ris.nome].remove(ris)
	     lista_giocatori.append((ris, ru_ris))
   ref_entrati = [ref.id for (ref, ru) in lista_giocatori]
   print >>sys.stderr, "ref entrati"
   print >>sys.stderr, ref_entrati
   ref_entrati = Referto.objects.filter(pk__in=ref_entrati).update(entrato_in_campo=True)
   port_o_dif_in_campo = [ref.id for (ref, ru) in lista_giocatori if ru.nome=='D' or ru.nome=='P']
   print >>sys.stderr, 'schierati in difesa'
   print >>sys.stderr, schierati_in_ruolo['D']
   print >>sys.stderr, 'port o dif'
   print >>sys.stderr, port_o_dif_in_campo
   if ( schierati_in_ruolo['D']>3 and len(port_o_dif_in_campo) >= 5): # se ha schierati piu' di 3 difensori ed hanno giocato effettivamente piu' di 3, metto il flag modificatore
       Referto.objects.filter(pk__in=port_o_dif_in_campo).update(modificatore=True)
       for (ref, ru) in lista_giocatori:
	       if(ref.id in port_o_dif_in_campo):
		       ref.modificatore = True # aggiorno il modificatore sulla copia locale
   referti.update(da_ricalcolare=False)
   return (True, lista_giocatori)


class GiornataLega(models.Model):
 giornata = models.ForeignKey(Giornata, blank=True, null=True)
 lega = models.ForeignKey(Lega)
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
	#	nuovo_turno = self.lega.incontrocoppa_set.filter(tipo=turno)
	#	plnum = 2*nuovo_turno.count()
	#	if plnum>0:
	#		break
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


class IncontroLega(models.Model):
 """ si riferisce ad un incontro disputato tra due fantasquadre all'interno della lega """
 allenatorecasa = models.ForeignKey(Allenatore, blank=True, null=True, related_name="IncontroCasa") # allenatore della squadra di casa
 allenatoretrasferta = models.ForeignKey(Allenatore,  blank=True, null=True, related_name="IncontroTrasferta") # allenatore della squadra in trasferta
 formazionecasa = models.OneToOneField(Formazione, blank=True, null=True, related_name="IncontroCasa") # formazione della squadra in casa
 formazionetrasferta = models.OneToOneField(Formazione, blank=True, null=True, related_name="IncontroTrasferta") # formazione della squadra in trasferta
 lega = models.ForeignKey(Lega, blank=True, null=True) # lega a cui la giornata corrisponde
 giornatalega = models.ForeignKey(GiornataLega) # giornata nella lega
 fmcasa_nomod = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 fmtrasferta_nomod = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 modcasa = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 modtrasferta = models.DecimalField(default=0.0, max_digits=5, decimal_places = 2)
 #disputato = models.BooleanField(default=False) # se l'incontro e' gia' stato disputato o meno
 def __unicode__(self):
   if self.allenatorecasa is not None and self.allenatoretrasferta is not None:
     return self.allenatorecasa.__unicode__() + " - " + self.allenatoretrasferta.__unicode__()
   else:
     return "da definire - da definire"
 def short(self):
   return self.allenatorecasa.__unicode__().replace(" ", "").replace(".","")[0:3] + " - " + self.allenatoretrasferta.__unicode__().replace(" ","").replace(".","")[0:3]
 @property
 def disputato(self):
    if (self.fmcasa==0.0 or self.fmtrasferta==0.0):
	    return False
    return True
 def aggiorna_incontro(self, refertocasa=None, refertotrasferta=None, redazione=None, aggiorna_comunque=False):
    formazioni = [self.formazionecasa, self.formazionetrasferta]
    referti_formazioni = [refertocasa, refertotrasferta]
    redazione = self.lega.redazione if self.lega is not None else ( self.IncontroCoppaAnd.lega.redazione if hasattr(self, 'IncontroCoppaAnd') else self.IncontroCoppaRit.lega.redazione)
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



class IncontroCoppa(models.Model):
  """ si riferisce ad un incontro di coppa con andata e ritorno. Se i due allenatori sono settati, si sa gia' chi la disputera' e si comporta quindi come un incontro di lega
      se invece sono settati gli incontri, vuol dire che a disputarla saranno i vincenti dei due incontri, una volta disputati"""
  incontrocasa = models.ForeignKey("self", related_name="QualificataCasaPer", blank=True, null=True) # incontro da cui proviene la squadra di casa
  incontrotrasferta = models.ForeignKey("self", related_name="QualificataTrasfertaPer", blank=True, null=True) # allenatore della squadra in trasferta
  incontro_andata = models.OneToOneField(IncontroLega, blank=True, null=True, related_name="IncontroCoppaAnd") # incontro per il match d'andata
  incontro_ritorno = models.OneToOneField(IncontroLega, blank=True, null=True, related_name="IncontroCoppaRit") # incontro per il match d'andata
  lega = models.ForeignKey(Lega) # lega a cui la giornata corrisponde
  tipo = models.CharField(max_length=20, default="Turno Preliminare") # specifica se si tratta di turno preliminare, quarti...
  andata_ritorno = models.BooleanField(default=True) # specifica se il turno contiene andata e ritorno, se e' false i ritorni saranno nulli
  indice = models.PositiveSmallIntegerField(default=0) # indice del turno e.g. 1o quarto, 2o quarto
  @classmethod
  def create(cls, allenatorecasa, allenatoretrasferta, giornata_andata, giornata_ritorno, **kwargs):
       inclega_andata = IncontroLega(allenatorecasa=allenatorecasa, allenatoretrasferta=allenatoretrasferta, giornatalega=giornata_andata)
       inclega_andata.save()
       inclega_ritorno = None
       if giornata_ritorno is not None:
         inclega_ritorno = IncontroLega(allenatorecasa=allenatoretrasferta, allenatoretrasferta=allenatorecasa, giornatalega=giornata_ritorno)
         inclega_ritorno.save()
       inc = cls(incontro_andata = inclega_andata, incontro_ritorno=inclega_ritorno, **kwargs); # preliminare
       return inc
  class Meta:
        unique_together = (("lega", "indice", "tipo"),)  # per ogni lega e tipo c'e' un unico incontro
  @property
  def allenatorecasanome(self):
    if (self.incontro_andata is not None and self.incontro_andata.allenatorecasa is not None):
		    return self.incontro_andata.allenatorecasa.__unicode__()
    elif (self.incontrocasa is not None):
            return ("Vincitore %s %d" % (self.incontrocasa.tipo, self.incontrocasa.indice))
    return "da stabilire"
  @property
  def allenatoretrasfertanome(self):
    if (self.incontro_andata is not None and self.incontro_andata.allenatoretrasferta is not None):
	    return self.incontro_andata.allenatoretrasferta.__unicode__()
    elif (self.incontrotrasferta is not None):
            return ("Vincitore %s %d" % (self.incontrotrasferta.tipo, self.incontrotrasferta.indice))
    return "da stabilire"
  def setta_allenatori(self, allcasa_id, alltrasferta_id): # imposta l'allenatore che gioca in casa/trasferta l'andata
    self.incontro_andata.allenatorecasa_id = allcasa_id
    self.incontro_andata.allenatoretrasferta_id = alltrasferta_id
    self.incontro_andata.save()
    if(self.incontro_ritorno):
	    self.incontro_ritorno.allenatorecasa_id = alltrasferta_id
	    self.incontro_ritorno.allenatoretrasferta_id = allcasa_id
	    self.incontro_ritorno.save()
  def setta_allenatori_da_incontri(self):
    vincitore_casa = self.incontrocasa.vincitore.id
    vincitore_trasferta = self.incontrotrasferta.vincitore.id
    self.setta_allenatori(vincitore_casa, vincitore_trasferta)
  @property
  def vincitore(self):
    scarto = self.incontro_andata.golcasa + self.incontro_ritorno.goltrasferta - self.incontro_andata.goltrasferta - self.incontro_ritorno.golcasa
    if scarto>0:
	return self.incontro_andata.allenatorecasa
    elif scarto<0:
	return self.incontro_andata.allenatoretrasferta
    else: # qui ci andrebbero i RIGORI!!!
	return None
  def __unicode__(self):
    return self.allenatorecasanome + " - " + self.allenatoretrasfertanome


@receiver(post_delete, sender=IncontroCoppa)
def my_handler(sender, instance, **kwargs):
   if instance.incontro_andata is not None:
	   instance.incontro_andata.delete()
   if instance.incontro_ritorno is not None:
	   instance.incontro_ritorno.delete()




class Voto(models.Model):
  """Voto ricevuto da un calciatore in una certa giornata; contiene le informazioni sul voto puro e gli altri dati; il supporto per differenti redazioni e'
  inserito tramite la variabile redazione """
  redazione = models.ForeignKey(Redazione)
  giornata = models.ForeignKey(Giornata)
  calciatore = models.ForeignKey(Calciatore)
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
  voto = models.ForeignKey(Voto, blank=True, null=True)
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
        labels = {'non_ha_giocato': _('Imponi SV'),
		  'fantavoto_db': _('Fantavoto'),
	          'votopuro_db': _('Voto Puro')}
	widgets = {'fantavoto_db': NumberInput(attrs={'step': 0.5}), 'votopuro_db': NumberInput(attrs={'step': 0.5})}



class TrasferimentoRosa(models.Model):
  """acquisto/cessione di un calciatore da parte di un allenatore"""
  from asta.models import Asta
  calciatore = models.ForeignKey(Calciatore) # il calciatore acquistato
  valore = models.PositiveSmallIntegerField() # importo dell'acquisto/cessione (nel secondo caso sono i soldi recuperati
  acquisto = models.BooleanField(default=True) # se e' un acquisto o una cessione
  allenatore = models.ForeignKey(Allenatore) # l'allenatore che ha fatto il trasferimento
  asta = models.ForeignKey(Asta, blank=True, null=True) # asta da cui proviene l'acquisto
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
