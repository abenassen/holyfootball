from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseForbidden,HttpResponseRedirect
from django.shortcuts import get_object_or_404
from fantaapp.models import *
from django.urls import reverse
from django.shortcuts import get_object_or_404
from asta.models import Asta
from django.db import transaction
import sys, datetime, pytz
from django import db
from django.template import Template, RequestContext
from django.forms import ModelChoiceField,IntegerField, Form
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
import simplejson as json
from django.core import serializers
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags


from django.core.exceptions import PermissionDenied


### decorators
def logger(func):
  def inner(*args, **kwargs):
    print "Arguments were: %s, %s" % (args, kwargs)
    return HttpResponse("Arguments were: %s, %s" % (args, kwargs))
    return func(*args, **kwargs)
  return inner



def allenatore_required(func): #la pagina e' visibile solo agli allenatori della lega
   def inner(*args, **kwargs):
     legahash = kwargs.get('legahash') if 'legahash' in kwargs.keys() else args[1]
     request = args[0]
     lega = get_object_or_404(Lega, codice=legahash)
     if(not(lega.allenatore_set.filter(utente_id=request.user.id).exists())):
        return HttpResponseRedirect(reverse('home_utente'))
     return func(*args, **kwargs)
   return inner

def amministratore_required(func): #la pagina e' visibile solo agli amministratori della lega
   def inner(*args, **kwargs):
     legahash = kwargs.get('legahash') if 'legahash' in kwargs.keys() else args[1]
     request = args[0]
     lega = get_object_or_404(Lega, codice=legahash)
     if(not(lega.allenatore_set.filter(utente_id=request.user.id, amministratore=True).exists())):
        return HttpResponseRedirect(reverse('home_utente'))
     return func(*args, **kwargs)
   return inner



def populateContext(request):
    context = {'utente': request.user.profile.alias}
    return context

# Create your views here.

@csrf_exempt
@transaction.atomic
def uploadvoti(request):
        redazione, created = Redazione.objects.get_or_create(nome = 'Napoli')
	data = json.loads(request.body)
	anno = 2017
        campionato = Campionato.objects.get(nome=('Serie A %d-%d' % (anno-1, anno)))
        lista_all = []
        giornata_obj = trova_ultima_lega(campionato)
	for dizio in data:
		print >>sys.stderr, dizio['nome']
		dizio['ha_giocato'] = True
		try:
		  calc_obj = Calciatore.objects.get(nome=dizio['nome'].rstrip(), squadra__campionato=campionato)
        	except Calciatore.DoesNotExist:
        	  print >>sys.stderr, "Non l'ho trovato"
		  if(dizio['nome'] in lista_all):
		    raise Calciatore.DoesNotExist
		  else:
           	    print >>sys.stderr, "e' forse un allenatore?"
		    lista_all.append(dizio['nome'])
		    continue
		try:
		   dizio['votopuro'] = round(float(dizio['votopuro']),1)
		except ValueError:
        	     dizio['votopuro'] = 6.0
       		     dizio['ha_giocato'] = False
       		dizio.pop("nome", None)  # Rimuovo il nome perche' non sta nel database in questa forma, ma entra come oggetto calciatore
   		dizio.pop("ruolo", None)  # Rimuovo il ruolo perche' non sta nel database del voto
  	        voto,created = Voto.objects.update_or_create(redazione=redazione, giornata=giornata_obj,calciatore=calc_obj, defaults=dizio)
       		print >>sys.stderr, "Inserito con successo"
	return HttpResponse("Voti inseriti")


@allenatore_required
def test(request, legahash):
   return HttpResponse(lega.nome)


def viewtemplate(request):
   pagename = request.GET.get('page', False)
   context = {}
   context = dict(request.GET.items() + context.items())
   context['data'] = IncontroCampionato.objects.all()[0].data
   if pagename:
     return render(request, 'fantaapp/'+pagename, context)
   else:
     return HttpResponse("No page requested.")

def messaggio(request, msg, context = {}):
   context['msg'] = msg
   return render(request, 'fantaapp/messaggio.html', context)

def maglia_colore(request, legahash):
   lega = get_object_or_404(Lega, codice=legahash)
   try:
	allenatore = lega.allenatore_set.get(utente_id=request.user.id)
	intero = hash(allenatore.nomesquadra)
        import struct
        r = intero % 256
        g = (intero/256) % 256
        b = (intero/256/256) % 256
        stringa_colore = "".join(map(chr, (r,g,b))).encode('hex')
   except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        stringa_colore = "ffffff"
   context = {}
   context['stringa_colore'] = stringa_colore
   return render(request, 'fantaapp/shirt_colora.svg', context, content_type = 'image/svg+xml')

def login_view(request):
    username = request.POST.get('username', False)
    if username:
      password = request.POST['password']
      print >>sys.stderr, password
      user = authenticate(username=username, password=password)
      print >>sys.stderr, user
      if user is not None:
        if user.is_active:
          login(request, user)
          newpath = request.GET.get('next', '/fantaapp/')
          return redirect(newpath)
        else:
          context = {'titolo': 'Errore', 'messaggio_errore': "L'utente risulta disattivato. Contatta l'amministratore."}
          return render(request, 'fantaapp/errore.html', context)
    else:
      context = {'titolo': 'Login', 'data': ""}
      return render(request, 'fantaapp/login.html', context)

@login_required
def home_user(request):
    context = populateContext(request)
    context['titolo'] = 'HomePage ' + request.user.get_username()
    context['listaallenatori'] = request.user.allenatore_set.all()
    return render(request, 'fantaapp/hp_utente.html', context)

@login_required
def home_lega(request, legahash, entra=False):
    """pagina di visualizzazione della home della tua lega data dal codice legahash"""
    context = populateContext(request)
    lega = get_object_or_404(Lega, codice=legahash)
    allenatori = lega.allenatore_set
    context['lega'] = lega
    try:
       ultima_giornata = trova_ultima_lega(lega.campionato)
       incontri_cartello = IncontroLega.objects.filter(giornata=ultima_giornata, fase__competizione__lega=lega)
    except Giornata.DoesNotExist: #il campionato e' terminato
       incontri_cartello = []
    lista_incontri = {}
    for inc in incontri_cartello:
	nomecomp = inc.fase.nomecompleto
    	print >>sys.stderr, inc, nomecomp
	key = nomecomp + " - Giornata " + str(ultima_giornata.numero)
	if key not in lista_incontri.keys():
		lista_incontri[key]=[]
	lista_incontri[key].append(inc)
    context['incontri_cartello'] = lista_incontri
    try:
        asta = lega.asta_set.latest('id')
        context['astaid'] = asta.id
        context['tipoasta'] = asta.tipo
        adesso = datetime.datetime.now(pytz.utc)
        print >>sys.stderr, 'orari: ', adesso, asta.apertura, asta.chiusura
        context['astaattiva'] = (asta.apertura < adesso) and (asta.chiusura > adesso)
    except Asta.DoesNotExist:
        pass
    try:
	allenatore = allenatori.get(utente_id=request.user.id)
    except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        if(lega.allenatore_set.count() < lega.numeropartecipanti): #c'e' ancora posto nella lega, propongo l'iscrizione
          if(entra): # ho gia' avuto la conferma dall'utente, lo aggiungo
		nuovoallenatore = lega.nuovo_allenatore(utente=request.user, is_amministratore=False)
                nuovoallenatore.save()
	  else:
	    context['link'] = request.build_absolute_uri(reverse('entralega', kwargs={'legahash': lega.codice}))
	    return render(request, 'fantaapp/accetta_lega.html', context)
            #return HttpResponse(context['link'])
        else: #la lega e' completa, lo rimando alla sua home -> METTERE UN MESSAGGIO D'ERRORE?
          return HttpResponseRedirect(reverse('home_utente'))
    allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
    context['messaggi'] = lega.messaggio_set.all().order_by('-id')[:5]
    context['allenatore'] = allen
    if allen.amministratore:
	    context['allenatori'] = allenatori
    return render(request, 'fantaapp/hp_lega.html', context)


@amministratore_required
def amministrazione(request, legahash):
    """pagina di gestione dell'amministrazione della lega data dal codice legahash"""
    context = populateContext(request)
    lega = get_object_or_404(Lega, codice=legahash)
    allenatori = lega.allenatore_set
    context['lega'] = lega
    context['giornfin'] = lega.campionato.totale_giornate
    context['giornini'] = lega.campionato.giornate_disputate() + 1
    allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
    context['allenatore'] = allen
    context['allenatori'] = allenatori
    return render(request, 'fantaapp/amministrazione.html', context)



def aggiusta_faseindice(nomefase, indice, dizionariofasi):
          """associa un id e un indice dell'incontro a nomefase e indice usando dizionariofasi. Se il nomefase non e' tra le keys
          di dizionariofasi, vuol dire che si tratta di un'altra fase distinta e che quindi e' semplicemente un id. Inoltre indice puo' essere
          o la posiione in classifica (ed in tal caso non viene modificato) o l'indice dell'incontro e allora viene sostituito dall'id dell'incontrocoppa corrispondente"""
          if isinstance(indice, basestring):
             indice = int(indice)
          if nomefase in dizionariofasi.keys():
        	      faseid = dizionariofasi[nomefase]['id']
        	      tipo = dizionariofasi[nomefase]['tipo']
        	      id_incontri = dizionariofasi[nomefase]['incontri']
        	      print nomefase, faseid, tipo, id_incontri, indice
          else:
		      faseid = int(nomefase)
		      faseobj = FaseCompetizione.objects.get(pk=faseid)
		      tipo = faseobj.tipo
		      id_incontri = faseobj.incontrocoppa_set.values_list('id', flat=True)
	  if tipo=='elidir':                  # se e' un girone, indice e' semplicemente la posizione in classifica e resta tale
	              if indice < len(id_incontri): # da 0...len(id_incontri) corrisponde alla squadra vincente di quell'incontro; se no e' la perdente
	                indice = id_incontri[indice]   # rimpiazzo l'indice con il vero id dell'incontro
	              else:
	                indice = str(id_incontri[indice - len(id_incontri)]) + "p"    # aggiungo una p a simboleggiare che e' la perdente
	  print "Indice finale: ", str(indice)
          return faseid, str(indice)

def settasquadraincontro(nuovoincontro, inc, dizionariofasi, casatrasferta = 'casa'):
                """restituisce una coppia nuovoincontro, indice, ove nuovoincontro ha impostata l'allenatore o la fase e la descrizione del modo
                per ottenere l'allenatore; indice contiene il riferimento all'incontro
                """
		stringa = inc['squadra' + casatrasferta]
        	if stringa.isdigit(): # la squadra casa e' un numero, quindi e' l'indice di un'allenatore
        		setattr(nuovoincontro,'allenatore' + casatrasferta + '_id', int(stringa))
        		return (nuovoincontro, '')
        	else:
        	   compid, nomefase, indice = stringa.split("__")
                   faseid, indice = aggiusta_faseindice(nomefase, indice, dizionariofasi)
        	   setattr(nuovoincontro, 'faseoriginale' + casatrasferta + '_id',faseid)
        	return (nuovoincontro, indice)


@amministratore_required
@transaction.atomic
def edita_competizione(request, legahash):
    """pagina per la creazione e la modifica delle competizioni della lega, viene chiamata dalla pagina amministrazione"""
    #sid = transaction.savepoint()
    if request.method == 'POST':
    	salvataggio = json.loads(request.POST['salvataggio'])
        lega = get_object_or_404(Lega, codice=legahash)
       	idcomp = salvataggio['id']
	if (idcomp != "nuovacomp"):
	      return messaggio(request, "Spiacente, la modifica di una competizione non e' supportata al momento.", context)
        print >>sys.stderr, salvataggio
        print >>sys.stderr, "Nuova competizione chiamata", salvataggio['nome']
        #return HttpResponse("{}", content_type='application/json')
	competizione = Competizione(lega=lega, nome=salvataggio['nome'], descrizione = '')   # creo la nuova competizione
	competizione.save()
	dizionariofasi = {}
        for fase in salvataggio['fasi']:
            print >>sys.stderr, "Nuova fase chiamata", fase['titolo']
	    nuovafase = FaseCompetizione(nome=strip_tags(fase['titolo']), tipo=fase['tipo'], competizione=competizione)
	    nuovafase.save()
   	    dizfase = {} # dizionario relativo alla nuova fase creata
	    dizfase['id'] = nuovafase.id # associo il nome schematico della fase all'id nel database
	    dizfase['incontri'] = []     # id degli incontricoppa corrispondenti alla fase, e' utile per fare riferimento all'indice dello scontro diretto
	    dizfase['tipo'] = fase['tipo']
   	    dizionariofasi[fase['nome']] = dizfase
	    if fase['tipo'] == 'girone':
	        for inc in fase['incontri']:
	        	giornata = Giornata.objects.get(numero=inc['giornatacampionato'], campionato=lega.campionato)
	        	nuovoincontro = IncontroLega(giornata=giornata, fase=nuovafase)
			nuovoincontro, indicecasa = settasquadraincontro(nuovoincontro, inc, dizionariofasi, casatrasferta = 'casa')
			nuovoincontro, indicetrasferta = settasquadraincontro(nuovoincontro, inc, dizionariofasi, casatrasferta = 'trasferta')
			nuovoincontro.descrizioneincontri = indicecasa + "," + indicetrasferta
	        	nuovoincontro.save()
	        	print >>sys.stderr, inc
	    elif fase['tipo'] == 'elidir':
	        for inc in fase['incontri']:
                        numero_giornate = inc['giornatacampionato'].split(",") # giornate degli incontri, se sono due vuol dire andata e ritorno
                        giornata = Giornata.objects.get(numero=numero_giornate[0], campionato=lega.campionato)
	        	nuovoincontro = IncontroLega(giornata=giornata, fase=nuovafase)
			nuovoincontro, indicecasa = settasquadraincontro(nuovoincontro, inc, dizionariofasi, casatrasferta = 'casa')
			nuovoincontro, indicetrasferta = settasquadraincontro(nuovoincontro, inc, dizionariofasi, casatrasferta = 'trasferta')
			nuovoincontro.descrizioneincontri = indicecasa + "," + indicetrasferta
	        	nuovoincontro.save()
	        	nuovoincontro_ritorno = None
	        	if len(numero_giornate) == 2: # c'e' il ritorno
	        	   nuovoincontro_ritorno = nuovoincontro.scambia_andata_ritorno()
                           giornata_ritorno = Giornata.objects.get(numero=numero_giornate[1], campionato=lega.campionato)
	        	   nuovoincontro_ritorno.giornata = giornata_ritorno
	        	   nuovoincontro_ritorno.save()
	        	nuovoincontro_coppa = IncontroCoppa(incontro_andata=nuovoincontro, incontro_ritorno=nuovoincontro_ritorno,
	        	                      fase=nuovafase, andata_ritorno=(len(numero_giornate)==2))
	        	nuovoincontro_coppa.save()
	        	dizionariofasi[fase['nome']]['incontri'].append(nuovoincontro_coppa.id)
	    elif fase['tipo'] == 'premio':
	    	premio = PremioCompetizione(nome=fase['titolo'], competizione = competizione)
	    	stringa = fase['datipremio']
	    	if stringa.isdigit(): # e' un po' strano: sarebbe un premio dato direttamente ad un allenatore...
        		premio.allenatore_id = int(stringa)
        	else:    # e' un premio che dipende dal risultato di una fase
        	   compid, nomefase, indice = stringa.split("__")
        	   print >>sys.stderr, dizionariofasi
                   faseid, indice = aggiusta_faseindice(nomefase, indice, dizionariofasi)
        	   premio.faseoriginale_id = faseid
        	   premio.descrizione = indice
        	   #imposto la giornata di assegnazione del premio come quella in cui si conclude la fase
                   numero_giornata_premio = max(IncontroLega.objects.filter(fase_id=1).values_list('giornata__numero', flat=True)) # massima giornata degli incontri della competizione
                   premio.giornata = Giornata.objects.get(numero=numero_giornata_premio, campionato=lega.campionato)
        	premio.save()
        #raise PermissionDenied("Errore generico")
	return HttpResponse("{}", content_type='application/json')
    return render(request, 'fantaapp/amministrazione.html', context)



@login_required
def entra_lega(request, legahash):
    """l'utente viene inserito nella lega"""
    return home_lega(request, legahash, True)

@login_required
def crea_lega(request, legahash=None):
     """pagina di creazione di una nuova lega; se legahash e' None assume che si stia creando una nuova lega altrimenti immagina sia un editing"""
     creazione = True
     context = {'submit_title':'Crea', 'action':reverse('crealega')} # l'utente sta creando una nuova lega
     if(legahash is not None):
        creazione = False
        lega = get_object_or_404(Lega, codice=legahash)
	allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
        if(not(allen.amministratore)): #controllo che l'allenatore loggato sia amministratore della lega e possa quindi editarla
          return HttpResponseRedirect(reverse('home_utente'))
	context = {'submit_title':'Modifica',
	           'action': reverse('editalega', kwargs={'legahash':legahash}),
		   'link': request.build_absolute_uri(reverse('aprilega', kwargs={'legahash': lega.codice}))}
     if request.method == 'POST':
	    if(not(creazione)):
               form = LegaForm(request.POST, instance=lega)
            else:
               form = LegaForm(request.POST)
            if form.is_valid(): #salvo se il form e' corretto
               nuovalega = form.save()
               if(creazione): # se e' una creazione aggiungo un nuovo allenatore associato all'utente loggato e lo rendo amministratore della nuova lega
                 nuovoallenatore = nuovalega.nuovo_allenatore(utente=request.user, is_amministratore=True)
                 nuovoallenatore.save()
               return HttpResponseRedirect(reverse('editalega', kwargs={'legahash':nuovalega.codice}))
     else:
    	    if(not(creazione)):
               form = LegaForm(instance=lega)
            else:
               form = LegaForm()
     context.update({'form': form, 'metodo':'post', 'nome_form': '', 'action': reverse('crealega')})
     return render(request, 'fantaapp/formlega.html', context)

@allenatore_required
@login_required
def rose(request, legahash):
    """associato alla lista delle rose della lega"""
    context = populateContext(request)
    lega = get_object_or_404(Lega, codice=legahash)
    context['lega'] = lega
    allenatori = lega.allenatore_set.all()
    context['rose'] = [ (x, x.ottieni_rosa()) for x in allenatori]
    return render(request, 'fantaapp/rose.html', context)


def ottieni_allenatore_rosa(request, legahash):
    """restituisce la coppia (lega, allenatore loggato)"""
    lega = get_object_or_404(Lega, codice=legahash)
    allenatore = lega.allenatore_set.get(utente_id=request.user.id)
    return (lega, allenatore)


def trova_ultima_lega(campionato):
    """restituisce la prima giornata del campionato associato alla lega non conclusa; se non esiste
    lancia un'eccezione"""
    giornate = campionato.giornata_set
    try:
      numero_max = giornate.filter(disputata=True).latest('numero').numero # insieme di giornate che sono gia' associate ad una di campionato
    except Giornata.DoesNotExist: # non esistono giornate disputate... magari e' la prima!
      numero_max = 0
    giorn = giornate.get(numero=(numero_max+1))
    return giorn


def gestione_formazione(request, creata, formazione, giornata, rosa, context = {}):
    """creata indica se la formazione e' stata appena creata; giornata e' la giornata di campionato corrispondente, rosa contiene la rosa dell'allenatore """
    data_ora = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    squadre_disponibili = [x.squadre for x in giornata.incontrocampionato_set.filter(data__gt=data_ora)]
    squadre_disponibili = [element for tupl in squadre_disponibili for element in tupl]
    print >>sys.stderr, squadre_disponibili
    calc_primavera = Calciatore.objects.filter(primavera=True).all()
    for ru in rosa.keys():
	    rosa[ru] = filter(lambda x: x[0].squadra in squadre_disponibili, rosa[ru]) # TOGLIERE PER RENDERE FORMAZIONE EDITABILE
	    primavera = filter(lambda x: x.ruolo.all()[0].nome == ru, calc_primavera)[0]
	    rosa[ru].append((primavera,0))
    context['rosa'] = rosa
    context['D'] = 4
    context['C'] = 4
    context['A'] = 2
    print >>sys.stderr, "La formazione risulta creata"
    if (creata):
      return render(request, 'fantaapp/formazione.html', context)
    # la formazione esiste gia'... controllo che sia ancora editabile, cioe' che gli schierati non abbiano gia' giocato
    print >>sys.stderr, "formazione gia' esistente"
    (context['D'],context['C'],context['A']) = map(int, formazione.modulo.split(","))
    referti = formazione.referto_set.order_by('posizione').select_related('calciatore__squadra')
    schierati_che_giocano = referti.exclude(calciatore__squadra__in=squadre_disponibili).exclude(calciatore__primavera=True)
    if(schierati_che_giocano.exists()):
       context['msg']="Non puoi piu' editare la formazione: le partite sono gia' iniziate."
       return render(request, 'fantaapp/messaggio.html', context)   # TOGLIERE PER RENDERE FORMAZIONE EDITABILE
    if(not(request.POST)):
	    id_schierati = referti.values_list('posizione', 'calciatore__id')
	    context['formaz_list'] = ','.join(map(lambda x: str(list(x)), id_schierati))
    else:
	    rosadic = {}
	    for ru in rosa.keys():
	      for (gioc,val) in rosa[ru]:
                rosadic[gioc.id] = ru  # dizionari contenente rosadic[id del giocatore] = ruolo del giocatore, per tutti i giocatori in rosa
	    for ru in rosa.keys():
	    	context[ru] = 0 # azzero i contatori del modulo
	    print >>sys.stderr, rosadic
	    print >>sys.stderr, request.POST
	    modulo = request.POST.get('modulo', '4-4-2')
	    modulo_data = {}
	    (modulo_data['D'], modulo_data['C'], modulo_data['A']) = map(int,modulo.split('-'))
	    if ( sum(modulo_data.values()) != 10 or modulo_data['D']<3 or modulo_data['A']>3):
	       context['msg']="Modulo inaccettabile."
	       return render(request, 'fantaapp/messaggio.html', context)
	    for i in range(18):
		print >>sys.stderr, i
		elem = int(request.POST.get('formaz[%d]' %(i+1), 0))
		print >>sys.stderr, "qui ci sono-1"
		if (elem in rosadic.keys()): #l'elemento c'e' ed e' nella rosa, aggiorno la formazione
		     print >>sys.stderr, "qui ci sono-2"
                     try:
		       print >>sys.stderr, "qui ci sono0"
		       ref = referti.get(posizione=i+1, formazione=formazione)
		     except Referto.DoesNotExist:
		       print >>sys.stderr, "qui ci sono"
		       ref = Referto(posizione=i+1, formazione=formazione)
		     ref.calciatore_id = elem
		     print >>sys.stderr, "qui ci sono3"
		     try:
		       ref.save()
		     except Exception as e:
		       print >>sys.stderr, e
		     print >>sys.stderr, "qui ci sono4"
		     if(i+1 <= 11):
			     context[rosadic[elem]] = context[rosadic[elem]] + 1
		else:
		     referti.filter(posizione=i+1).delete()
		print >>sys.stderr, elem
	    if (context['D'] <= modulo_data['D'] and context['C'] <= modulo_data['C'] and context['A'] <= modulo_data['A']):
   	       formazione.modulo = '%d,%d,%d' % (modulo_data['D'], modulo_data['C'], modulo_data['A'])
	    else: # ci sono delle incongruenze tra schierati e modulo... annullo tutto
               formazione.referto_set.delete()
	       context['msg']="Modulo inaccettabile."
	       return render(request, 'fantaapp/messaggio.html', context, status=304)
	    print >>sys.stderr, formazione.modulo
	    formazione.save()
	    msg = Messaggio(lega=context['lega'], testo=("La formazione di %s e' stata aggiornata." % (context['utente'])))
	    msg.save()
    return render(request, 'fantaapp/formazione.html', context)

@login_required
def formazione(request, legahash, id_comp, all_id=None):
    """associato alla creazione della prossima formazione"""
    context = populateContext(request)
    try:
	(lega, allenatore) = ottieni_allenatore_rosa(request, legahash)
    except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
    context['lega'] = lega
    if (allenatore.amministratore):
	    #all_id = request.POST.get('allenatore_id', allenatore.id)
	    if (all_id is not None and all_id != allenatore.id):
		    allenatore = lega.allenatore_set.get(id=all_id)
    try:
      giornata = trova_ultima_lega(lega.campionato)
    except ValueError as e:
      context['msg']= str(e)
      return render(request, 'fantaapp/messaggio.html', context)
    rosa = allenatore.ottieni_rosa()
    gioca_in = 'casa'
    incontrolega = IncontroLega.objects.filter(fase__competizione_id = id_comp, giornata=giornata, allenatorecasa=allenatore)
    if not(incontrolega.exists()): #controllo se gioca in trasferta
        incontrolega = IncontroLega.objects.filter(fase__competizione_id = id_comp, giornata=giornata, allenatoretrasferta=allenatore)
   	gioca_in = 'trasferta'
    if (not(incontrolega.exists())):
        context['msg']= "La tua squadra non gioca questa giornata, goditi le partite degli altri!"
        return render(request, 'fantaapp/messaggio.html', context)
    incontrolega = incontrolega[0]
    formazione = getattr(incontrolega, 'formazione'+ gioca_in)
    creata = False
    if (formazione is None): # la formazione non esisteva prima
	    creata = True
            formazione = Formazione(allenatore=allenatore, giornata=giornata)
	    formazione.save()
            setattr(incontrolega, 'formazione' + gioca_in, formazione)
	    incontrolega.save()
    return gestione_formazione(request, creata, formazione, giornata, rosa, context)


@login_required
def formazionecoppa(request, legahash, all_id=None):
    """associato alla creazione della prossima formazione di coppa"""
    context = populateContext(request)
    try:
	(lega, allenatore) = ottieni_allenatore_rosa(request, legahash)
    except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
    context['lega'] = lega
    if (allenatore.amministratore):
	    #all_id = request.POST.get('allenatore_id', allenatore.id)
	    if (all_id is not None and all_id != allenatore.id):
		    allenatore = lega.allenatore_set.get(id=all_id)
    try:
      (ultima_giornata_lega, giornata) = trova_ultima_lega(lega.campionato)
    except ValueError as e:
      context['msg']= str(e)
      return render(request, 'fantaapp/messaggio.html', context)
    tipo_turno = 'andata'
    incontricoppa = IncontroCoppa.objects.filter(incontro_andata__giornatalega=ultima_giornata_lega).select_related('incontro_andata')
    if not(incontricoppa.exists()):
       tipo_turno = 'ritorno'
       incontricoppa = IncontroCoppa.objects.filter(incontro_ritorno__giornatalega=ultima_giornata_lega).select_related('incontro_ritorno')
    if not(incontricoppa.exists()):
        context['msg']= "Non ci sono turni di coppa in questa giornata."
        return render(request, 'fantaapp/messaggio.html', context)
    rosa = allenatore.ottieni_rosa()
    gioca_in = 'casa'
    incontrocoppa = incontricoppa.filter(**{("incontro_%s__allenatorecasa" % tipo_turno): allenatore})
    if not(incontrocoppa.exists()): #controllo se gioca in trasferta
        incontrocoppa = incontricoppa.filter(**{("incontro_%s__allenatoretrasferta" % tipo_turno): allenatore})
    	gioca_in = 'trasferta'
    if (not(incontrocoppa.exists())):
        context['msg']= "Non sei qualificato per questo turno!"
        return render(request, 'fantaapp/messaggio.html', context)
    incontrocoppa = incontrocoppa[0]
    incontro = getattr(incontrocoppa, 'incontro_%s' % (tipo_turno))
    formazione = getattr(incontro, "formazione%s" % (gioca_in))
    creata = False
    if (formazione is None): # la formazione non esisteva prima
	    print >>sys.stderr, "formazione nulla"
	    creata = True
            formazione = Formazione(allenatore=allenatore, giornata=giornata) # se eventualmente esiste gia' una formazione la prendo (e' la formazione del campionato)
	    formazione.save()
	    setattr(incontro, 'formazione%s' % (gioca_in), formazione)
	    incontro.save()
    return gestione_formazione(request, creata, formazione, giornata, rosa, context)



def leggi_incontri(incontri, redazione):
    for inc in incontri:
        refcasa = None if inc.formazionecasa is None else inc.formazionecasa.referto_set.all()
        reftrasferta = None if inc.formazionetrasferta is None else inc.formazionetrasferta.referto_set.all()
        da_aggiornare, liste_giocatori = inc.aggiorna_incontro(refcasa, reftrasferta, redazione)
    return incontri

@login_required
def tabellino_singolo(request, legahash, incontro_id):
   """restituisce la pagina del tabellino dell'incontro richiesto"""
   context = populateContext(request)
   lega = get_object_or_404(Lega.objects.select_related('redazione'), codice=legahash)
   context['lega'] = lega
   try:
	allenatore = lega.allenatore_set.get(utente_id=request.user.id)
   except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
   context['allenatore'] = allenatore
   incontri = IncontroLega.objects.prefetch_related('formazionecasa__referto_set__voto__calciatore__ruolo__redazione',
                                                              'formazionetrasferta__referto_set__voto__calciatore__ruolo__redazione',
							      'formazionecasa__allenatore__lega',
							      'formazionetrasferta__allenatore__lega',).select_related('allenatorecasa__lega__redazione', 'allenatoretrasferta__lega__redazione').filter(pk=incontro_id)
   print >>sys.stderr, len(db.connection.queries)
   redazione = lega.redazione
   context['inc']    = leggi_incontri(incontri, redazione)[0]
   print >>sys.stderr, len(db.connection.queries)
   if (request.is_ajax()):
     return render(request, 'fantaapp/tabellino_singolo.html', context) # e' stato chiamato in seguito all'inserimento di un voto e serve solo ad aggiornare, quindi non serve l'involucro html
   else:
     return render(request, 'fantaapp/tabellino_singolo_mostra.html', context) # e' una chiamata alla pagina quindi carico una pagina html completa


def mostra_tabellino(request, incontri, lega, context):
   """mostra il tabellino di un set d'incontri IncontroLega"""
   redazione = lega.redazione
   context['incontri'] = leggi_incontri(incontri, redazione)
   return render(request, 'fantaapp/tabellino.html', context)


@login_required
def tabellino(request, legahash, faseid, numero_giornata='0'):
   """restituisce la pagina dei tabellini della giornata richiesta"""
   context = populateContext(request)
   lega = get_object_or_404(Lega.objects.select_related('redazione'), codice=legahash)
   context['lega'] = lega
   try:
	allenatore = lega.allenatore_set.get(utente_id=request.user.id)
   except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
   context['allenatore'] = allenatore
   try:
     if (numero_giornata == '0'):
	     numero_giornata = lega.campionato.giornata_set.filter(disputata=True).latest('numero').numero
   except GiornataLega.DoesNotExist:
	       context['msg']="Giornata non ancora disputata"
	       return render(request, 'fantaapp/messaggio.html', context, status=404)
   incontri = IncontroLega.objects.filter(fase__id=faseid).filter(giornata__numero=numero_giornata).prefetch_related('formazionecasa__referto_set__voto__calciatore__ruolo__redazione',
                                                              'formazionetrasferta__referto_set__voto__calciatore__ruolo__redazione',
							      'formazionecasa__allenatore__lega',
							      'formazionetrasferta__allenatore__lega',).select_related('allenatorecasa__lega__redazione', 'allenatoretrasferta__lega__redazione').all()
   mostra_tabellino(request, incontri, lega, context)
   context['numerogiornata'] = numero_giornata
   return render(request, 'fantaapp/tabellino.html', context)


@login_required
def tabellino_coppa(request, legahash, incontro_id):
   """restituisce la pagina del tabellino dell'incontro richiesto"""
   context = populateContext(request)
   lega = get_object_or_404(Lega.objects.select_related('redazione'), codice=legahash)
   context['lega'] = lega
   try:
	allenatore = lega.allenatore_set.get(utente_id=request.user.id)
   except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
   context['allenatore'] = allenatore
   incontri = IncontroCoppa.objects.prefetch_related('incontro_andata__formazionecasa__referto_set__voto__calciatore__ruolo__redazione',
                                                              'incontro_andata__formazionetrasferta__referto_set__voto__calciatore__ruolo__redazione',
							      'incontro_andata__formazionecasa__allenatore__lega',
							      'incontro_andata__formazionetrasferta__allenatore__lega',
							      'incontro_ritorno__formazionecasa__referto_set__voto__calciatore__ruolo__redazione',
                                                              'incontro_ritorno__formazionetrasferta__referto_set__voto__calciatore__ruolo__redazione',
							      'incontro_ritorno__formazionecasa__allenatore__lega',
							      'incontro_ritorno__formazionetrasferta__allenatore__lega',).select_related('incontro_andata__allenatorecasa__lega__redazione', 'incontro_ritorno__allenatorecasa__lega__redazione','incontro_andata__allenatoretrasferta__lega__redazione','incontro_ritorno__allenatoretrasferta__lega__redazione').filter(pk=incontro_id)
   print >>sys.stderr, "Stampo gli incontri di coppa", incontri, incontri[0].fase
   if incontri[0].fase.competizione.lega!=lega:
      return messaggio(request, "Non hai accesso a questo incontro!", context)
   redazione = lega.redazione
   for inc in incontri:
	   if(inc.incontro_andata is not None):
		   leggi_incontri([inc.incontro_andata],redazione)
	   if(inc.incontro_ritorno is not None):
		   leggi_incontri([inc.incontro_ritorno],redazione)
   context['incontri'] = incontri
   print >>sys.stderr, len(db.connection.queries)
   return render(request, 'fantaapp/tabellino_coppa.html', context)





@allenatore_required
@login_required
def classifica(request, legahash, faseid):
   context = populateContext(request)
   lega = get_object_or_404(Lega, codice=legahash)
   incontri = IncontroLega.objects.filter(fase_id=faseid).select_related('allenatorecasa','allenatoretrasferta') # incontri associati ad una giornata di campionato
   context['dati_allenatori'] = FaseCompetizione.classifica_da_incontri(incontri)
   context['lega'] = lega
   return render(request, 'fantaapp/classifica.html', context)


@login_required
def editavoto(request, legahash, referto_id):
    context = populateContext(request)
    lega = get_object_or_404(Lega, codice=legahash)
    allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
    if(not(allen.amministratore)): #controllo che l'allenatore loggato sia amministratore della lega e possa quindi editarla
          return HttpResponse('Non sei amministratore del sito. Richiedi di diventarlo per poter editare i voti.')
    referto = Referto.objects.select_related('voto').get(pk = referto_id)
    formvoto = None
    if request.method == 'POST':
	  formreferto = RefertoForm(request.POST, instance=referto)
	  if(referto.voto is not None):
		  formvoto = VotoForm(request.POST, instance=referto.voto)
	  if formreferto.is_valid() and formvoto.is_valid(): #salvo se il form e' corretto
               referto = formreferto.save()
               if(referto.voto is not None):
		       voto = formvoto.save()
    else:
	  formreferto = RefertoForm(instance=referto)
	  if(referto.voto is not None):
		  formvoto = VotoForm(instance=referto.voto)
    context['form_referto'] = formreferto
    context['submit_title'] = 'Salva'
    context['form_voto'] = formvoto
    context['referto_id'] = referto_id
    context['lega'] = lega
    context['metodo'] = 'POST'
    return render(request, 'fantaapp/editavoto.html', context)

@login_required
def editarose(request, legahash):
        context = populateContext(request)
        lega = get_object_or_404(Lega, codice=legahash)
	allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
        if(not(allen.amministratore)): #controllo che l'allenatore loggato sia amministratore della lega e possa quindi editarla
          return HttpResponse('Non sei amministratore del sito.')
	if request.method == 'POST':
	  form = TrasferimentoRosaForm(request.POST, lega=lega)
          trasferimento = form.save()
	  return HttpResponse('ok')
	else:
	  form = TrasferimentoRosaForm(lega=lega)
	context['titolo_form'] = 'Trasferimento nelle rose'
	context['form'] = form
	context['nomeform'] = 'form_editarose'
	#{% url 'editarose' legahash=lega.codice %}
        context['actionurl'] = reverse('editarose', kwargs={'legahash':legahash})
	context['submit_title'] = 'Salva'
	context['lega'] = lega
	context['metodo'] = 'POST'
	return render(request, 'fantaapp/formpopup.html', context)

@login_required
def scambiorose(request, legahash):
        context = populateContext(request)
        lega = get_object_or_404(Lega, codice=legahash)
	allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
        if(not(allen.amministratore)): #controllo che l'allenatore loggato sia amministratore della lega e possa quindi editarla
          return HttpResponse('Non sei amministratore del sito.')
	if request.method == 'POST':
	  form = ScambioForm(request.POST, lega=lega)
	  if form.is_valid():
	  	with transaction.atomic():
			trasf1 = TrasferimentoRosa(	calciatore=form.cleaned_data['calciatore1'],
						valore = form.cleaned_data['costo2'] - form.cleaned_data['contropartita'],
						acquisto = False,
						allenatore = form.cleaned_data['allenatore1']) # l'allenatore1 lascia il calciatore1 al costo di calciatore2 - contropartita
			trasf2 = TrasferimentoRosa(	calciatore=form.cleaned_data['calciatore2'],
						valore = form.cleaned_data['costo1'] + form.cleaned_data['contropartita'],
						acquisto = False,
						allenatore = form.cleaned_data['allenatore2']) # l'allenatore2 lascia il calciatore2 al costo di calciatore1 + contropartita
			trasf3 = TrasferimentoRosa(	calciatore=form.cleaned_data['calciatore2'],
						valore = form.cleaned_data['costo2'],
						acquisto = True,
						allenatore = form.cleaned_data['allenatore1']) # l'allenatore1 acquista il calciatore2 al costo di calciatore2
			trasf4 = TrasferimentoRosa(	calciatore=form.cleaned_data['calciatore1'],
						valore = form.cleaned_data['costo1'],
						acquisto = True,
						allenatore = form.cleaned_data['allenatore2']) # l'allenatore2 acquista il calciatore1 al costo di calciatore1
			trasf1.save()
			trasf2.save()
			trasf3.save()
			trasf4.save()
			if form.cleaned_data['contropartita']>0:
	        		testomsg = "%s e' stato ceduto da %s a %s in cambio di %s e %d crediti." % (form.cleaned_data['calciatore2'], form.cleaned_data['allenatore2'], form.cleaned_data['allenatore1'], form.cleaned_data['calciatore1'], form.cleaned_data['contropartita'])
			if form.cleaned_data['contropartita']<0:
	        		testomsg = "%s e' stato ceduto da %s a %s in cambio di %s e %d crediti." % (form.cleaned_data['calciatore1'], form.cleaned_data['allenatore1'], form.cleaned_data['allenatore2'], form.cleaned_data['calciatore2'], -form.cleaned_data['contropartita'])
			else:
	        		testomsg = "%s e' stato ceduto da %s a %s in cambio di %s." % (form.cleaned_data['calciatore1'], form.cleaned_data['allenatore1'], form.cleaned_data['allenatore2'], form.cleaned_data['calciatore2'])
			msg = Messaggio(lega=lega, testo=testomsg)
			msg.save()
			return HttpResponse('ok')
	else:
	  form = ScambioForm(lega=lega)
	context['titolo_form'] = 'Scambio nelle rose'
	context['form'] = form
	context['nomeform'] = 'form_editarose'
	#{% url 'editarose' legahash=lega.codice %}
        context['actionurl'] = reverse('scambiorose', kwargs={'legahash':legahash})
	context['submit_title'] = 'Salva'
	context['lega'] = lega
	context['metodo'] = 'POST'
	return render(request, 'fantaapp/formpopup.html', context)


@login_required
def aggiungicrediti(request, legahash):
        context = populateContext(request)
        lega = get_object_or_404(Lega, codice=legahash)
	allen = get_object_or_404(lega.allenatore_set, utente_id=request.user.id)
        if(not(allen.amministratore)): #controllo che l'allenatore loggato sia amministratore della lega e possa quindi editarla
          return HttpResponse('Non sei amministratore del sito.')
        class CreditiForm(Form):
          crediti = IntegerField(label = "Crediti:", min_value=-1000, max_value=1000)
	if request.method == 'POST':
	    form = CreditiForm(request.POST)
	    if form.is_valid():
		valore_crediti = form.cleaned_data['crediti']
		print >>sys.stderr, valore_crediti
		lega.allenatore_set.update(budget=F('budget') + valore_crediti)
		testomsg = "Budget di %d crediti aggiunto a tutti gli allenatori" % (abs(valore_crediti))
		if (valore_crediti < 0):
			testomsg.replace('aggiunto', 'rimosso')
		if (valore_crediti == 1):
			testomsg.replace('crediti', 'credito')
		msg = Messaggio(lega=lega, testo=testomsg)
		msg.save()
		return HttpResponseRedirect(reverse('home_utente'))
	else:
	  form = CreditiForm()
	context['titolo_form'] = 'Aggiunta di crediti'
	context['form'] = form
	context['nomeform'] = 'form_aggiungicrediti'
        context['actionurl'] = reverse('aggiungicrediti', kwargs={'legahash':legahash})
	context['submit_title'] = 'Salva'
	context['lega'] = lega
	context['metodo'] = 'POST'
	return render(request, 'fantaapp/formpopup.html', context)



@amministratore_required
@login_required
def nuova_giornata(request, legahash, conferma=False):
    """permette all'amministratore di associare la prossima giornata della lega alla prossima giornata del campionato"""
    context = populateContext(request)
    lega = get_object_or_404(Lega, codice=legahash)
    context['lega'] = lega
    giornate = lega.giornatalega_set
    if (giornate.count() == 0):
         #bisogna creare il calendario prima
	 return HttpResponse("Bisogna creare il calendario prima")
    giornate_associate = giornate.exclude(giornata__isnull=True) # insieme di giornate che sono gia' associate ad una di campionato
    if (giornate_associate.count() == giornate.count()): # tutte le giornate sono associate
         #campionato completo
	 return HttpResponse("Il campionato e' completo!")
    if (not(giornate_associate.count()==0) and not(giornate_associate.latest('numero').giornata.disputata)):  # se l'ultima associata non e' disputata, e' una giornata in corso...
	print >>sys.stderr, "e quindi?"
	return messaggio(request, "La giornata e' in corso!", context)
    giornate_campionato = lega.campionato.giornata_set.filter(disputata=False).order_by('numero')
    if (giornate_campionato.count() == 0): # tutte le giornate sono gia' associate
	    return HttpResponse("Spiacente, ma il campionato e' esaurito")
    prossima_giornata = giornate_campionato[0] # prendo la prima disponibile
    if (conferma):
      prossima_giornata_lega = giornate.filter(giornata__isnull=True).order_by('numero')[0]
      prossima_giornata_lega.giornata = prossima_giornata
      prossima_giornata_lega.save()
      prec = giornate.get(numero=prossima_giornata.numero-1)
      prec.chiudi_giornata() # chiude la giornata precedente: segna i passaggi del turno in coppa
      context['msg']='Giornata %d della lega associata correttamente alla giornata %d del campionato' % (prossima_giornata_lega.numero, prossima_giornata.numero)
      return render(request, 'fantaapp/messaggio.html', context)
    else: #mostro la pagina della conferma
      context['giornata'] = prossima_giornata
      context['incontri'] = prossima_giornata.incontrocampionato_set.all()
      return render(request, 'fantaapp/nuova_giornata.html', context)

def nuova_giornata_conferma(request, legahash):
   """chiamo la pagina di associazione della giornata con conferma"""
   return nuova_giornata(request, legahash, True)

@allenatore_required
@login_required
def calendario_competizione(request, legahash, id_comp):
     """associato al calendario della lega"""
     context = populateContext(request)
     competizione = get_object_or_404(Competizione.objects, id=id_comp)
     lega = competizione.lega
     fasi = competizione.fasecompetizione_set.exclude(tipo="premio").all()
     context['lega'] = lega
     listafasi = []
     for fase in fasi:
       print >>sys.stderr, "stampo la fase", fase.tipo
       dictfase = {'tipo': fase.tipo, 'nome': fase.nome}
       if fase.tipo=='girone':
          incontriquery = fase.incontrolega_set.all()
          valori_giornate = sorted(list(set(incontriquery.values_list('giornata__numero', flat=True))))
	  incontriid = {}
          incontri_giornate = [[y for y in incontriquery if y.giornata.numero==x] for x in valori_giornate]
          dictfase['incontrigiornate'] = incontri_giornate
          print >> sys.stderr, dictfase
          dictfase['id'] = fase.id
       elif fase.tipo=='elidir':
          #dictfase['incontricoppa'] = fase.incontrocoppa_set.all()
          dictfase['incontricoppa'] = {}
          incs = fase.incontrocoppa_set.all()
          for inc in incs:
               gg = inc.giornate_coinvolte
               if gg not in dictfase['incontricoppa'].keys():
                 dictfase['incontricoppa'][gg] = []
               dictfase['incontricoppa'][gg].append(inc)
       listafasi.append(dictfase)
     context['fasi'] = listafasi
     context['compid'] = competizione.id
     return render(request, 'fantaapp/calendario.html', context)


@allenatore_required
@login_required
def calendario_lega(request, legahash):
     """associato al calendario della lega"""
     print >>sys.stderr, len(db.connection.queries)
     context = populateContext(request)
     lega = get_object_or_404(Lega.objects.prefetch_related('incontrolega_set__giornatalega','incontrolega_set__allenatorecasa','incontrolega_set__allenatoretrasferta'), codice=legahash)
     incontrilega = lega.incontrolega_set.all()
     context['lega'] = lega
     gironi = []
     totale_giornate = lega.totale_giornate()
     g=1
     for girone in range(lega.numero_gironi):
	gir = []
	for gg in range(lega.numeropartecipanti-1):
	  gir.append(filter(lambda x: x.giornatalega.numero==g, incontrilega))
	  g = g+1
	  print g
        gironi.append(gir)
     context['gironi'] = gironi
     print >>sys.stderr, len(db.connection.queries)
     return render(request, 'fantaapp/calendario.html', context)

@login_required
def calendario_coppa(request, legahash):
     context = populateContext(request)
     lega = get_object_or_404(Lega, codice=legahash)
     context['lega'] = lega
     nomi_turni = list(lega.incontrocoppa_set.values_list('tipo', flat=True).distinct())
     nomi_turni.sort(key = lambda x: nome_turni_coppa.index(x))
     nomi_turni.reverse()
     turni = []
     for turno in nomi_turni:
	turni.append(lega.incontrocoppa_set.filter(tipo=turno))
     context['turni'] = turni
     return render(request, 'fantaapp/calendario_coppa.html', context)



@allenatore_required
@login_required
def edita_squadra(request, legahash):
  if request.method == 'POST':
    lega = get_object_or_404(Lega, codice=legahash)
    allenatore = lega.allenatore_set.get(utente_id=request.user.id)
    fields_name = allenatore.editabili
    for f in fields_name:
      nuovo_valore = request.POST.get(f, False)
      print >>sys.stderr, f + " " + str(nuovo_valore)
      if nuovo_valore:
		 setattr(allenatore, f, nuovo_valore)
    allenatore.logourl = request.build_absolute_uri(allenatore.logourl)
    allenatore.full_clean()
    allenatore.save()
    return HttpResponse("Squadra aggiornata.")
  else:
    return HttpResponse(status=405) # return a wrong method error


# funzione usata per i test
@transaction.atomic
def genera_rose(request, legahash):
  """ riempio le rose con giocatori a caso"""
  #context = populateContext(request)
  context = {}
  lega = get_object_or_404(Lega, codice=legahash)
  context['lega'] = lega
  redazione = lega.redazione
  rulist = redazione.ruolo_set.filter(calciatore__squadra__campionato=lega.campionato) # lista di oggetti ruolo della redazione della lega e di questo campionato
  allenatori = lega.allenatore_set.all()
  transf = TrasferimentoRosa.objects.filter(allenatore__lega=lega).all() # ottengo tutti i trasferimenti gia' presenti
  for t in transf:
          print >>sys.stderr, "rimuovo: %s" %t
	  t.delete() # gli elimino singolarmente per aggiornare anche i dati di ciascun allenatore
          pass
  for alle in allenatori:
	  print >>sys.stderr, 'resetto %s' %alle
	  alle.resetta() # resetto i numeri a quelli della lega
	  alle.save()
  for ru in ruoli_lunghi.keys():
      print >>sys.stderr, 'considero come ruolo: %s' % ru
      rulist_ruolo = list(rulist.filter(nome=ru))
      for alle in allenatori:
	  print >>sys.stderr, 'considero %s' %alle
          while(alle.numero_ruolo(ru) > 0):
	    print >>sys.stderr, 'da comprare %d' % alle.numero_ruolo(ru)
	    idindex = random.randint(0,len(rulist_ruolo)-1)
            cal = rulist_ruolo.pop(idindex).calciatore
	    print >>sys.stderr, 'scelgo %s' % cal
            valore = random.randint(1, alle.budget - alle.totale_da_tesserare + 1)
	    trasf = TrasferimentoRosa(calciatore=cal, valore=valore, allenatore=alle)
	    trasf.save()
  return HttpResponse("Generazione delle rose fatta")

