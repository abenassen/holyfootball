from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from asta.models import *
#from asta import googleinteraction
from datetime import *
import random
import json
#from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from fantaapp.views import *
from django.utils.translation import ugettext_lazy as _
from django.forms import Form, IntegerField, ModelChoiceField, CharField, TextInput, Select
from math import ceil
from pytz import timezone,utc
from django.core.validators import MinValueValidator


def prova(request):
  return HttpResponse("ciao")

def ottieni_ultimi(astaid, Oggetto, numero=0):
  """ fa una query per ottenere gli ultimi numero Oggetti inseriti nell'asta"""
  queryS = Oggetto.objects.filter(asta__id=astaid).order_by('-id')
  if(int(numero)==0):
    ultimi = queryS.all()
  else:
    ultimi = queryS[:numero]
  return ultimi


@allenatore_required
@login_required
def lista_ultimi(request, legahash, astaid, Oggetto, numero=0):
  """restituisce un codice html per un select list con gli ultimi numero Oggetti"""
  ultimi = ottieni_ultimi(astaid, Oggetto, numero)
  context = {'lista': ultimi}
  return render(request, 'fanta/select_da_lista.html', context)

def lista_ultimi_acquisti(legahash, numero=0):
  queryS = TrasferimentoRosa.objects.filter(allenatore__lega__codice=legahash).order_by('-id')
  if(int(numero)==0):
    ultimi = queryS.all()
  else:
    ultimi = queryS[:numero]
  return ultimi


def funzione_aggiornamento(legahash, astaid, numero=5):
  def convertioggetto(oggetto):
      off = {}
      off['id'] = oggetto.id
      off['stringa'] = str(oggetto)
      return off
  #data = serializers.serialize("json", ultime_offerte)
  ultime_offerte = ottieni_ultimi(astaid, Offerta, numero)
  ultimi_acquistati = lista_ultimi_acquisti(legahash, numero)
  ultimi_chiamati= ottieni_ultimi(astaid, CalciatoreChiamato, numero)
  offerte_convertite = map(convertioggetto, ultime_offerte)
  acquistati_convertiti = map(convertioggetto, reversed(ultimi_acquistati))
  chiamati_convertiti = map(convertioggetto, ultimi_chiamati)
  response_data = {}
  response_data['offerte'] = offerte_convertite
  response_data['acquistati'] = acquistati_convertiti
  response_data['chiamati'] = chiamati_convertiti
  if(CalciatoreChiamato.objects.count()==0):
    response_data['calciatore'] = "null"
  else:
    calciatore = CalciatoreChiamato.objects.latest('id').calciatore
    response_data['calciatore'] = model_to_dict(calciatore)
    response_data['calciatore']['squadra'] = calciatore.squadra.nome
    response_data['calciatore']['ruolo'] = calciatore.ruolo.get(redazione=Lega.objects.get(codice=legahash).redazione).nome
  response_data['allenatori'] = lista_allenatori(legahash)
  return response_data

def aggiornamento_periodico(request, legahash, astaid, numero=5):
  response_data = funzione_aggiornamento(legahash, astaid, numero)
  return HttpResponse(json.dumps(response_data), content_type="application/json")
  #return HttpResponse(serializers.serialize("json",response_data), mimetype="application/json")

@allenatore_required
@login_required
def asta_script(request, legahash, astaid, numero=0):
  """return the js script compiled with the proper link"""
  context = { 'legahash': legahash, 'astaid':astaid}
  return render(request, 'fanta/asta_template_backup.js', context)



def lista_offerte(request, legahash, astaid, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  return lista_ultimi(request, legahash, astaid, Offerta, numero)


def lista_acquistati(request, legahash, astaid, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  return lista_ultimi(request, legahash, astaid, Acquisto, numero)

def lista_chiamati(request, legahash, astaid, numero):
  """return an html code for the select list of the last 'howmany' offers"""
  return lista_ultimi(request, legahash, astaid, CalciatoreChiamato, numero)

@amministratore_required
@login_required
def cancella_ultimi(request, legahash, astaid, Oggetto, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  ultimi = ottieni_ultimi(astaid, Oggetto, numero)
  context = {'lista': ultimi}
  #ultimi.delete()
  for x in ultimi:
	  x.delete()
  return HttpResponse("Cancellato/i!")

def cancella_offerte(request, legahash, astaid, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  return cancella_ultimi(request, legahash, astaid, Offerta, numero)

def cancella_chiamati(request, legahash, astaid, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  return cancella_ultimi(request, legahash, astaid, CalciatoreChiamato, numero)


def cancella_acquistati(request, legahash, astaid, numero=0):
  """return an html code for the select list of the last 'howmany' offers"""
  TrasferimentoRosa.objects.filter(asta_id=astaid).latest('id').delete()
  return HttpResponse("Cancellato/i!")

def resetta_allenatori(request, legahash, astaid):
  [ x.resetta() for x in lista_allenatori() ]
  return HttpResponse("Allenatori azzerati")

def resetta_asta(request):
  if((not('password' in request.POST) or request.POST['password']!="fantafanta") and request.session.get('banditore_id',"") != "301988435"):
      return banditore_login(request, True)
  resetta_allenatori(request)
  cancella_offerte(request)
  cancella_chiamati(request)
  return HttpResponse("Asta azzerata")

def inserisci_offerta(off):
  """verifico che l'allenatore abbia i crediti sufficienti e gli slot per fare l'offerta"""
  allenatore = off.allenatore
  lega = allenatore.lega
  redazione = lega.redazione
  ru = off.calciatore.ruolo.get(redazione=redazione).nome
  dacomprare = allenatore.totale_da_tesserare
  dacomprare_ruolo = allenatore.numero_ruolo(ru)
  #return (dacomprare, dacomprare_ruolo, allenatore.budget, off.soldi)
  if(dacomprare_ruolo>0 and (allenatore.budget - off.soldi - dacomprare +1 )>=0):
    off.save()
    return 1
  return 0


def inserisci_acquisto(off):
  allenatore = off.allenatore
  lega = allenatore.lega
  redazione = lega.redazione
  ru = off.calciatore.ruolo.get(redazione=redazione).nome
  dacomprare = allenatore.totale_da_tesserare
  dacomprare_ruolo = allenatore.numero_ruolo(ru)
  if(dacomprare_ruolo>0 and (allenatore.budget - off.soldi - dacomprare +1 )>=0):
    nuovo_acquisto = TrasferimentoRosa(calciatore=off.calciatore, valore=off.soldi, asta=off.asta, allenatore=off.allenatore)
    nuovo_acquisto.save()
    return 1
  else:
    return 0


@amministratore_required
#@logger
@login_required
def faiacquisto(request, legahash, astaid, numero):
  if(numero == '0'):
    offerta = Offerta.objects.latest('id')
  else:
    offerta = get_object_or_404(Offerta, pk=numero)
  if(inserisci_acquisto(offerta)):
    return HttpResponse("Acquisto inserito con successo\n")
  else:
    return HttpResponse("Richiesta non valida\n" + str(request.POST))

@login_required
def faiofferta(request, legahash, astaid):
  lega = get_object_or_404(Lega, codice=legahash)
  req = request.POST
  try:
	allenatore_loggato = lega.allenatore_set.get(utente_id=request.user.id)
  except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
  if ("calciatore" in req and "soldi" in req):
    if(allenatore_loggato.amministratore and "allenatore" in req):
	    allenatore = lega.allenatore_set.get(pk=req['allenatore'])
    else:
	    allenatore = allenatore_loggato
    calciatore = get_object_or_404(Calciatore, pk=req.get('calciatore', False))
    off = Offerta(allenatore=allenatore, calciatore=calciatore, soldi=int(req['soldi']), asta_id=astaid)
    if(inserisci_offerta(off)==1): return HttpResponse("Offerta inserita!")
  return HttpResponse("Richiesta non valida\n" + str(request.POST))




def html_calciatore(request, id_calciatore=-1):
  if(id_calciatore==-1):
    if(CalciatoreChiamato.objects.count()==0):
      return HttpResponse("Asta non iniziata")
    calciatore = CalciatoreChiamato.objects.latest('id').calciatore
  else:
    calciatore = get_object_or_404(Calciatore, pk=id_calciatore)
  context = {'calciatore': calciatore, 'ruolo': calciatore.RUOLI_NOME[calciatore.ruolo]}
  return render(request, 'fanta/scheda_calciatore.html', context)


def confronta(request):
   ruolo = random.randint(0,3)
   da_chiamare = Calciatore.objects.filter(ruolo=ruolo)
   while(True):
     setlen = []
     l = len(da_chiamare)
     for s in range(len(da_chiamare)):
       setlen = setlen + [s]*l
       l -= 1
     idindex1 = random.choice(setlen)
     setlen = [x for x in setlen if x != idindex1]
     idindex2 = random.choice(setlen)
     calc1 = da_chiamare[idindex1]
     calc2 = da_chiamare[idindex2]
     confrs = ConfrontoCalciatori.objects.filter(calciatore1__pk=calc1.id, calciatore2__pk=calc2.id)
     confrs2 = ConfrontoCalciatori.objects.filter(calciatore1__pk=calc2.id, calciatore2__pk=calc1.id)
     if (len(confrs)+len(confrs2)) == 0:
       break
   context = {'calc1': calc1,'calc2': calc2, 'ruolo1': calc1.RUOLI_NOME[calc1.ruolo], 'ruolo2': calc2.RUOLI_NOME[calc2.ruolo]}
   return render(request, 'fanta/confronta.html', context)

def salvaconfronto(request):
   if request.method == "GET":
     calcid1 = request.GET.get('calc1', False)
     calcid2 = request.GET.get('calc2', False)
     if calcid1 and calcid2:
       calc1 = get_object_or_404(Calciatore, pk=calcid1)
       calc2 = get_object_or_404(Calciatore, pk=calcid2)
       confr = ConfrontoCalciatori(calciatore1 = calc1, calciatore2 = calc2)
       confr.save()
   return confronta(request)

@login_required
def gestione_asta(request, legahash, astaid):
    asta = Asta.objects.get(pk=astaid)
    if (asta.tipo=="mercato" or asta.tipo=='mercatorip'):
        return mercato(request, legahash, asta)
    lega = get_object_or_404(Lega, codice=legahash)
    try:
	  allenatore = lega.allenatore_set.get(utente_id=request.user.id)
    except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
        return HttpResponseRedirect(reverse('home_utente'))
    if (allenatore.amministratore):
	    return banditore_asta(request, legahash, asta)
    context = {"allenatore" : allenatore, "lega": lega, 'asta': asta}
    return render(request, 'fanta/asta.html', context)

@login_required
def banditore_asta(request, legahash, asta):
    lega = get_object_or_404(Lega, codice=legahash)
    context = {'lega': lega, 'asta': asta, 'lista': lega.allenatore_set.all()}
    return render(request, 'fanta/banditore.html', context)


@login_required
def mercato(request, legahash, asta):
   altroieri = datetime.datetime.now() - datetime.timedelta(days=2)
   offerte = Offerta.objects.filter(asta=asta, status='attiva', orario__gt=altroieri).order_by('calciatore__nome', '-orario').select_related('calciatore', 'allenatore')
   approvate = Offerta.objects.filter(asta=asta, status='accettata').order_by('calciatore__nome', '-orario').select_related('calciatore', 'allenatore')
   lega = get_object_or_404(Lega, codice=legahash)
   try:
	  allenatore = lega.allenatore_set.get(utente_id=request.user.id)
   except Allenatore.DoesNotExist: #l'utente non e' iscritto alla lega
      return HttpResponseRedirect(reverse('home_utente'))
   context = {'offerte':offerte, 'approvate': approvate, 'lega': lega, 'astaid': asta.id, 'allenatore':allenatore}
   return render(request, 'fanta/mercato.html',context)

@login_required
def resoconto_mercato(request, legahash, astaid):
   altroieri = datetime.datetime.now() - datetime.timedelta(days=2)
   offerte = Offerta.objects.filter(asta__id=astaid, status='attiva', orario__gt=altroieri).order_by('calciatore__nome', '-orario').select_related('calciatore', 'allenatore')
   approvate = Offerta.objects.filter(asta__id=astaid, status='accettata').order_by('calciatore__nome', '-orario').select_related('calciatore', 'allenatore')
   context= {'offerte':offerte, 'approvate': approvate}
   return render(request, 'fanta/resoconto_mercato.html',context)

@amministratore_required
def elimina_offerta(request, legahash, astaid, offid):
    offerta = get_object_or_404(Offerta, id=offid)
    asta = Asta.objects.get(pk=astaid)
    lega = {'codice': legahash}
    context = {'lega': lega}
    if (offerta.asta.id != int(astaid) or asta.lega.codice != legahash):
        return messaggio(request, "Offerta non valida.", context)
    offerta.delete()
    return messaggio(request, "Offerta cancellata correttamente!", context)

@amministratore_required
def approva_offerta(request, legahash, astaid, offid):
    offerta = get_object_or_404(Offerta, id=offid)
    asta = Asta.objects.get(pk=astaid)
    lega = {'codice': legahash}
    context = {'lega': lega}
    budget = offerta.allenatore.budget
    if (offerta.asta.id != int(astaid) or asta.lega.codice != legahash or offerta.status != "attiva"):
        return messaggio(request, "Offerta non valida.", context)
    try:
      trasf = TrasferimentoRosa.objects.filter(calciatore=offerta.calciatore_da_lasciare, allenatore__lega=offerta.allenatore.lega).latest('id') # ultimo trasferimento del giocatore lasciato in questa lega.
    except TrasferimentoRosa.DoesNotExist:
        return messaggio(request, "Errore nell'offerta: il giocatore da lasciare non e' in possesso di alcun allenatore!", context)
    if (not(trasf.acquisto) or trasf.allenatore != offerta.allenatore):
        return messaggio(request, "Errore nell'offerta: il giocatore da lasciare non e' in possesso di questo allenatore!", context)
    offerte_prec = Offerta.objects.filter(asta=offerta.asta,calciatore=offerta.calciatore,status='attiva', orario__lt=offerta.orario)
    offerte_prec.update(status='superata')
    cred = 1 # crediti recuperati nella cessione
    if (asta.tipo == 'mercatorip'): # se e' un mercato di riparazione recupero meta' dei crediti
	    cred = ceil(float(trasf.valore)/2) # recupero meta' dei crediti approssimati per eccesso
    if budget + cred < offerta.soldi:
        return messaggio(request, "Errore nell'offerta: l'allenatore non ha crediti sufficienti per effettuarla!", context)
    trasf_cessione = TrasferimentoRosa(calciatore=offerta.calciatore_da_lasciare, valore=cred, acquisto=False, allenatore=offerta.allenatore, asta=offerta.asta)
    trasf_cessione.save() # inserisco la cessione del giocatore
    trasf_acquisto = TrasferimentoRosa(calciatore=offerta.calciatore, valore=offerta.soldi, acquisto=True, allenatore=offerta.allenatore, asta=offerta.asta)
    trasf_acquisto.save() # inseriscto l'acquisto del giocatore
    offerta.status='accettata'
    offerta.save() # aggiorno l'offerta
    return messaggio(request, "Acquisto inserito correttamente!", context)



@login_required
def nuovaofferta(request, legahash, astaid, offid=None):
	if offid:
	    offerta = get_object_or_404(Offerta, id=offid)
        context = populateContext(request)
        lega = get_object_or_404(Lega, codice=legahash)
	try:
          allen = lega.allenatore_set.get(utente_id=request.user.id)
        except Allenatore.DoesNotExist:
          return HttpResponse('Non sei un utente della lega.')
        allenatori = lega.allenatore_set.all()
        #rose = [ (x, x.ottieni_rosa()) for x in allenatori]
        id_in_rosa = []
	rose_allenatori = {}
        for alle in allenatori:
		rose_allenatori[alle] = alle.ottieni_rosa()
		id_suoi = [k.id for x in rose_allenatori[alle].keys() for k,val in rose_allenatori[alle][x]]
		id_in_rosa = id_in_rosa + id_suoi
		if alle.id == allen.id:
			id_di_alle = id_suoi
        #print >>sys.stderr, rose
	adesso = datetime.datetime.now(utc)
        asta = get_object_or_404(Asta, id=astaid)
	if (adesso > asta.chiusura):
	       context['msg']="L'asta e' gia' terminata!"
	       return HttpResponse(context['msg'])
	if (adesso < asta.apertura):
	       context['msg']="L'asta non e' ancora aperta!"
	       return HttpResponse(context['msg'])
	my_default_errors = {
	   'required': "Questo campo e' necessario",
	   'invalid': 'Metti un valore valido!'
	}
        class OffertaMercatoForm(Form):
	  if (offid): # deve essere un rilancio
		  #calciatore = CharField(initial=offerta.calciatore, widget=TextInput(attrs={'readonly':'readonly'}))
		  calciatore = ModelChoiceField(required=True, error_messages=my_default_errors, queryset=Calciatore.objects.filter(id=offerta.calciatore.id), label = "Calciatore coinvolto nell'acquisto", initial = 1,widget=Select(attrs={'readonly':'readonly'}))
		  valore = IntegerField(initial = offerta.soldi+1, error_messages=my_default_errors, validators=[MinValueValidator(offerta.soldi+1)])
	  else:
		  calciatore = ModelChoiceField(required=True, error_messages=my_default_errors, queryset=Calciatore.objects.filter(squadra__campionato=lega.campionato).exclude(id__in=id_in_rosa).order_by('nome'), label = "Calciatore coinvolto nell'acquisto")
		  valore = IntegerField(error_messages=my_default_errors, validators=[MinValueValidator(1)])
          calciatore_da_lasciare = ModelChoiceField(required=True, error_messages=my_default_errors, queryset=Calciatore.objects.filter(id__in=id_di_alle).order_by('nome'), label = "Calciatore della tua rosa da lasciare")
          #valore = IntegerField(error_messages=my_default_errors, validators=[MinValueValidator(1), MaxValueValidator(allen.budget)])
	if request.method == 'POST':
	  form = OffertaMercatoForm(request.POST)
	  if form.is_valid():
	    off = Offerta(allenatore=allen, soldi = form.cleaned_data['valore'], calciatore=form.cleaned_data['calciatore'], calciatore_da_lasciare= form.cleaned_data['calciatore_da_lasciare'])
	    off.asta_id = astaid
	    off.save()
	    return HttpResponse(content="Offerta effettuata", status=303)
	else:
	  form = OffertaMercatoForm()
	context['titolo_form'] = 'Offerta sul mercato'
	context['form'] = form
	context['nomeform'] = 'form_nuovaofferta'
        context['actionurl'] = reverse('rilanciaofferta', kwargs={'legahash':legahash, 'astaid':astaid, 'offid':offid}) if offid else reverse('nuovaofferta', kwargs={'legahash':legahash, 'astaid':astaid})
	context['submit_title'] = 'Salva'
	context['lega'] = lega
	context['metodo'] = 'POST'
	return render(request, 'fantaapp/formpopup.html', context)





@amministratore_required
@login_required
def crea_asta(request, legahash):
	context = {}
        context['link'] = request.build_absolute_uri(reverse('crea_asta_conferma', kwargs={'legahash': legahash}))
	return render(request, 'fanta/crea_asta.html', context)


@amministratore_required
@login_required
def crea_asta_conferma(request, legahash):
    lega = get_object_or_404(Lega, codice=legahash)
    asta = Asta(lega=lega)
    asta.save()
    return HttpResponseRedirect(reverse('gestione_asta', kwargs={'legahash': legahash, 'astaid':asta.id}))

@amministratore_required
@login_required
def chiama_giocatore(request, legahash, astaid):
    calcChiamati = CalciatoreChiamato.objects.filter(asta_id=astaid)
    lega = get_object_or_404(Lega, codice=legahash)
    redazione = lega.redazione
    rulist = redazione.ruolo_set.filter(calciatore__squadra__campionato=lega.campionato, calciatore__primavera=False) # lista di oggetti ruolo della redazione della lega e di questo campionato
    #calcs = Calciatore.objects.filter(squadra__campionato=lega.campionato)
    id_chiamati = map(lambda x: x.calciatore.id, calcChiamati.all())
    ru_da_chiamare = rulist.prefetch_related('calciatore__squadra__campionato').exclude(calciatore__id__in=id_chiamati) # escludo quelli gia' chiamati
    if(('ruolo' in request.GET)  and (request.GET['ruolo']!="-")):
      ru_da_chiamare = [ru for ru in ru_da_chiamare if ru.nome==request.GET['ruolo']]
    if(len(ru_da_chiamare) == 0):
      return HttpResponse("Tutti i giocatori sono stati chiamati!", status = 402)
    idindex = random.randint(0,len(ru_da_chiamare)-1)
    chiamato = CalciatoreChiamato(calciatore=ru_da_chiamare[idindex].calciatore, asta_id=astaid)
    chiamato.save()
    return HttpResponse("chiamato " + chiamato.calciatore.nome + " - " + str(len(id_chiamati) + 1) + " su " + str(len(id_chiamati)+len(ru_da_chiamare)))

def lista_allenatori(legahash):
    alls = Allenatore.objects.filter(lega__codice=legahash)
    lis = []
    for all in alls:
        all_dic = {'nome': all.utente.profile.alias, 'budget': all.budget, 'por': all.numeroportieri, 'dif': all.numerodifensori, 'centr': all.numerocentrocampisti, 'att': all.numeroattaccanti}
        lis.append(all_dic)
    return lis

@allenatore_required
@login_required
def resoconto(request):
    lis = lista_allenatori()
    context = {'lista': lis}
    return render(request, 'fanta/resoconto.html', context)



def rimuoviripetizioni(request):
  for row in CalciatoreChiamato.objects.all():
    if CalciatoreChiamato.objects.filter(id=row.id).count() > 1:
        row.delete()
  return HttpResponse("Rimozioni ripetizioni completata")

