# coding=utf-8

import urllib2
import simplejson
import os
import subprocess
import random
import select
import sys
import time
import datetime
from bs4 import BeautifulSoup
import requests
import datetime
import locale
from pytz import timezone
from numpy import *
from decimal import *
import os
sys.path.append(os.path.abspath("./FantaWebsite/fanta/"))

import votecontainer
VDAT = votecontainer.VContainer().VOTEDAT

notalwaysfield = ['fantamedia', 'fantamediasq', 'pres', 'mediavoto', 'gf', 'gs', 'rp', 'ammo', 'espu', 'assist']

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'fanta.settings'
application = get_wsgi_application()

from django.contrib.auth.models import User
from fantaapp.models import *
from django.db import transaction
from django.conf import settings




roles = {'P': "Portiere", 'D':"Difensore", 'C':"Centrocampista", 'A':"Attaccante"}
cambioruoli = {'P': (), 'D': ('C'), 'C': ('D','A'), 'A':('C')}


def aggiusta_nomi_file_voti(anno, path):
    campionato = Campionato.objects.get(nome=('Serie A %d-%d' % (anno-1, anno)))
    giornate = campionato.giornata_set.all()
    for g in giornate:
      filename = "Voti_Fantacalcio_Stagione_%d-%d_Giornata_%d.xlsx" % (anno-1, anno-2000, g.numero)
      fullpath = os.path.join(path, filename)
      print "looking for file", fullpath
      if os.path.exists(fullpath):
        print "File found!"
        dataf = datetime.date.strftime(g.data, "%d-%m-%y")
        newname = os.path.join(path, str(g.numero) + "." + dataf + ".xls")
        os.rename(fullpath, newname)
        
       
        
@transaction.atomic
def inseriscivoti(giornata, anno, nomeredazione):
    matchday = [x[3] for x in VDAT if (x[1] == giornata)&(x[2]==str(anno))][0]
    calcs = [x for team in matchday.getteams() for x in team.plist]
    redazione, created = Redazione.objects.get_or_create(nome = nomeredazione)
    campionato = Campionato.objects.get(nome=('Serie A %d-%d' % (anno-1, anno)))
    giornata_obj = campionato.giornata_set.get(numero=giornata)
    lista_all = []
    for calc in calcs:
	  print calc.name
	  try:
	    calc_obj = Calciatore.objects.get(nome=calc.name, squadra__campionato=campionato)
          except Calciatore.DoesNotExist:
	    if(calc.name in lista_all):
		    raise Calciatore.DoesNotExist
	    else:
	       lista_all.append(calc.name)
	       continue
          #    self.datalist = array([vf,gf,gs,rp,rsb,rs,au,amm,esp,ass,gdv,gdp])
	  print calc.datalist
	  dizio = 	{'votopuro': calc.datalist[0], 'assist': calc.datalist[9],
			 'golsuazione': calc.datalist[1], 'golsurigore': calc.datalist[5],
			 'ammo': calc.datalist[7], 'espu':calc.datalist[8], 'autogol':calc.datalist[6],
			 'golsubiti': calc.datalist[2], 'rigorisbagliati':calc.datalist[4],
			 'rigoriparati': calc.datalist[3], 'goldellavittoria':calc.datalist[10],
			 'goldelpareggio': calc.datalist[11],
			 'ha_giocato': True}
          if (dizio['votopuro'] is None):
             dizio['votopuro'] = 6.0
             dizio['ha_giocato'] = False
          else:
             dizio['votopuro'] = round(dizio['votopuro'],1)
          voto,created = Voto.objects.update_or_create(redazione=redazione, giornata=giornata_obj,calciatore=calc_obj, defaults=dizio)
          """voto.votopuro =
	  voto.assist=calc.datalist[9]
	  voto.golsuazione=calc.datalist[1]
	  voto.golsurigore=calc.datalist[5]
	  voto.ammo=calc.datalist[7]
	  voto.espu=calc.datalist[8]
	  voto.autogol=calc.datalist[6]
	  voto.golsubiti=calc.datalist[2]
	  voto.rigorisbagliati=calc.datalist[4]
	  voto.rigoriparati=calc.datalist[3]
	  voto.goldellavittoria=calc.datalist[10]
	  voto.goldelpareggio=calc.datalist[11]
	  voto.save()"""
	  print voto
    return 1


@transaction.atomic
def inseriscivoticampionato(anno, nomeredazione):
    """inserisce i voti dell'intero campionato"""
    campionato = Campionato.objects.get(nome=('Serie A %d-%d' % (anno-1, anno)))
    giornate = campionato.giornata_set.all()
    for g in giornate:
       print "Inserisco voti per la giornata", g.numero
       inseriscivoti(g.numero, anno, nomeredazione)



@transaction.atomic
def inserisci_calendario(startyear=2015, totale_giornate = 38):
	locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")
	today = datetime.date.today()
        tz = timezone('Europe/Rome')
	source_code = requests.get('https://it.wikipedia.org/wiki/Serie_A_%d-%d' % (startyear-1, startyear))
	soup = BeautifulSoup(source_code.content, 'lxml')
	table = soup.find('span', id='Calendario').parent.find_next_sibling('table')
	print "Cerca il calendario ", 	"Serie A %d-%d" % (startyear-1, startyear)
	campionato = Campionato.objects.get(nome="Serie A %d-%d" % (startyear-1, startyear))
	squadre = campionato.squadracampionato_set
	dataandata = datetime.datetime.now()
	dataritorno = datetime.datetime.now()
	h_andata = 15 # ora andata
	m_andata = 0 # minuto andata
	h_ritorno = 15 # ora ritorno
	m_ritorno = 0 # minuto ritorno
	for g,giornata in enumerate(table.find_all('table', style="font-size: 85%; text-align: center;")):
	    giornata_obj, created = campionato.giornata_set.get_or_create(numero=(g+1))
	    giornata_rit_obj, created = campionato.giornata_set.get_or_create(numero=(g+1+totale_giornate/2))
            print "Giornata", (g+1)
	    for i,riga in enumerate(giornata.find_all('tr')):
               time_andata_is_set = False
	       time_ritorno_is_set = False
	       giocato_andata = False
	       giocato_ritorno = False
	       gc_andata, gf_andata, gc_ritorno, gf_ritorno = (0,0,0,0)
	       print i, riga
	       if (i==0):
		       continue # la prima riga e' l'indice della giornata che non m'interessa
	       cols = riga.find_all('td')
	       cols = [x.text.replace(u'\xb0','').replace(u'\xba','') for x in filter(lambda x: x.text != '', cols)] # prendo giusto il testo dentro gli elementi di cols, e.g. cols[0].text ed elimino il carattere \xba corrispondente all'unicode di 1o nel primo del mese
	       print "Colonne", cols
	       if len(cols)==0:
		       continue
	       try:
		 if cols[0]=='29 feb.':
			 dataandata = datetime.datetime(year = startyear, day=29, month=2)
		 else:
		 	 dataandata = datetime.datetime.strptime(cols[0], '%d %b.')
		 indice_ris = 1 # avanzo di uno per cercare il risultato
		 if dataandata.month > 7:
			 dataandata = dataandata.replace(year=startyear-1)
		 else:
			 dataandata = dataandata.replace(year=startyear)
	       except ValueError: # se non e' una data, o e' un orario o un risultato
		 indice_ris = 0
	       print 'indice_ris:',indice_ris
	       #if (cols[0] != u'-' and len(cols)==2):
	       #   cols = [u'-'] + cols
	       if(cols[indice_ris].find(':') != -1): # e' un orario
			 h_andata,m_andata = map(int,cols[indice_ris].split(':'))
			 time_andata_is_set = True
	       elif(cols[indice_ris].find('-') != -1): # e' un risultato
			 gc_andata, gf_andata = cols[indice_ris].split('-')
			 if(gc_andata != '' and gf_andata != ''):
			   if(gc_andata.isdigit() and gf_andata.isdigit()):
				   gc_andata = int(gc_andata)
				   gf_andata = int(gf_andata)
				   giocato_andata = True
			   else:
			     cols = [u'-'] + cols
	       try:
		 if cols[-1]=='29 feb.':
			 dataritorno = datetime.datetime(year = startyear, day=29, month=2)
		 else:
		 	 dataritorno = datetime.datetime.strptime(cols[-1], '%d %b.')
		 indice_ris = 1 # avanzo di uno per cercare il risultato
		 if dataritorno.month > 7:
			 dataritorno = dataritorno.replace(year=startyear-1)
		 else:
			 dataritorno = dataritorno.replace(year=startyear)
	       except ValueError: # se non e' una data, o e' un orario o un risultato
		 indice_ris = 0
	       if(cols[-1-indice_ris].find(':') != -1):
			 h_ritorno,m_ritorno = map(int,cols[-1-indice_ris].split(':'))
			 time_ritorno_is_set = True
	       elif(cols[-1-indice_ris].find('-') != -1): # e' un risultato
			 gf_ritorno, gc_ritorno = cols[-1-indice_ris].split('-')
			 if(gc_ritorno != '' and gf_ritorno != ''):
			   if(gc_ritorno.isdigit() and gf_ritorno.isdigit()):
                             gc_ritorno = int(gc_ritorno)
                             gf_ritorno = int(gf_ritorno)
                             giocato_ritorno = True
                           else:
			     cols =  cols + [u'-']
	       if(not(time_andata_is_set)):
		 if(dataandata.weekday() == 5): # e' un sabato
			 h_andata=18
			 m_andata=0
		 if(dataandata.weekday() == 6): # e' una domenica
			 if(dataandata.month <= 8 and dataandata.month >= 7): # se e' estate giocheranno di sera
			     h_andata = 20
			     m_andata = 45
			 else:
			     h_andata = 15
			     m_andata = 0
		 elif(dataandata.weekday() == 2): # mercoledi' sara' un match serale
			     h_andata = 20
			     m_andata = 45
	       dataandata = dataandata.replace(hour=h_andata, minute=m_andata)
	       if(not(time_ritorno_is_set)):
		 if(dataritorno.weekday() == 5): # e' un sabato
			 h_ritorno=18
			 m_ritorno=0
		 if(dataritorno.weekday() == 6): # e' una domenica
			 if(dataritorno.month <= 8 and dataritorno.month >= 7): # se e' estate giocheranno di sera
			     h_ritorno = 20
			     m_ritorno = 45
			 else:
			     h_ritorno = 15
			     m_ritorno = 0
		 elif(dataritorno.weekday() == 2): # mercoledi' sara' un match serale
			     h_ritorno = 20
			     m_ritorno = 45
	       dataritorno = dataritorno.replace(hour=h_ritorno, minute=m_ritorno)
		       #print [x.text for x in cols]
	       squadra_casa, squadra_trasferta =  cols[-indice_ris-2].split('-')
	       if squadra_casa=="" or squadra_trasferta=="":
			print "Incontro non valido... Salto"
			continue
	       #print "Lista squadre", squadra_casa, squadra_trasferta, dataandata, dataritorno
	       #continue
               squadra_casa_obj, created = squadre.get_or_create(nome=squadra_casa)
	       squadra_trasferta_obj, created = squadre.get_or_create(nome=squadra_trasferta)
	       #print gc_andata, gf_andata, giocato_andata, giocato_ritorno
	       #print gc_ritorno, gf_ritorno, giocato_andata, giocato_ritorno
               defaults = {'data': tz.localize(dataandata)}
	       inc_andata, created = giornata_obj.incontrocampionato_set.get_or_create(squadracasa=squadra_casa_obj, squadratrasferta=squadra_trasferta_obj, defaults=defaults)
	       if (created or not(giocato_andata)):
		       inc_andata.data = tz.localize(dataandata)
	       inc_andata.disputato = giocato_andata
	       if (giocato_andata):
		       inc_andata.golcasa = gc_andata
		       inc_andata.goltrasferta = gf_andata
	       inc_andata.save()
	       print inc_andata
	       defaults = {'data': tz.localize(dataritorno)}
	       inc_ritorno, created = giornata_rit_obj.incontrocampionato_set.get_or_create(squadracasa=squadra_trasferta_obj, squadratrasferta=squadra_casa_obj, defaults=defaults)
	       if (created or not(giocato_ritorno)):
		       inc_ritorno.data = tz.localize(dataritorno)
	       inc_ritorno.disputato = giocato_ritorno
	       if (giocato_ritorno):
		       inc_ritorno.golcasa = gc_ritorno
		       inc_ritorno.goltrasferta = gf_ritorno
	       inc_ritorno.save()
	       print inc_ritorno
            giornata_obj.aggiorna()
            giornata_rit_obj.aggiorna()


def getImage(nomegioc, team):
  url = ('https://ajax.googleapis.com/ajax/services/search/images?'+'v=1.0&q='+urllib2.quote(nomegioc)+'%20'+urllib2.quote(team)+'%20calcio&userip=INSERT-USER-IP')
  #url = ('https://ajax.googleapis.com/ajax/services/search/images?'+'v=1.0&q='+urllib2.quote(nomegioc)+'%20'+urllib2.quote(team)+'&userip=INSERT-USER-IP')
  request = urllib2.Request(url, None, {'Referer': 'www.gazzetta.it'})
  response = urllib2.urlopen(request)
  # Process the JSON string.
  results = simplejson.load(response)
  # now have some fun with the results...
  print results.items()
  if(results['responseStatus']!=200):
    print "Maximum amount of google request reached... Waiting for next request."
    time.sleep(60)
    return getImage(nomegioc, team)
  imgurl = results.items()[0][1]['results'][0]['url']
  return imgurl
  #print ("wget -O image.jpg" + imgurl)
  #os.popen("wget -O image.jpg " + imgurl)


def getImageResult(nomegioc, team):
  url = ('https://ajax.googleapis.com/ajax/services/search/images?'+'v=1.0&q='+urllib2.quote(nomegioc)+'%20'+urllib2.quote(team)+'%20calcio&userip=INSERT-USER-IP')
  #url = ('https://ajax.googleapis.com/ajax/services/search/images?'+'v=1.0&q='+urllib2.quote(nomegioc)+'%20'+urllib2.quote(team)+'&userip=INSERT-USER-IP')
  request = urllib2.Request(url, None, {'Referer': 'www.gazzetta.it'})
  response = urllib2.urlopen(request)
  # Process the JSON string.
  results = simplejson.load(response)
  # now have some fun with the results...
  return results
  #print ("wget -O image.jpg" + imgurl)
  #os.popen("wget -O image.jpg " + imgurl)


def waitforinput(time):
  counter = time
  while True:
    i, o, e = select.select([sys.stdin], [], [], 1)
    if i:
        inp = sys.stdin.readline()
        #shortwait
        return inp
    counter -= 1
    if counter == 0:
      #long wait
      return -1

def stampaquotazioni(anno=2015):
  calciatori = Calciatore.objects.filter(squadra__campionato__nome=("Serie A %d-%d" % (anno-1, anno)))
  squadrebuone = ['JUVENTUS','ROMA', 'FIORENTINA', 'INTER','NAPOLI','MILAN', 'LAZIO', 'ATALANTA']
  squadrecoppe = ['JUVENTUS','ROMA', 'LAZIO', 'MILAN','NAPOLI', 'ATALANTA']
  for ru in roles.keys():
    idruolo = Ruolo.objects.filter(redazione__nome="Napoli", nome=ru).values_list('calciatore')
    calciatori_ruolo = calciatori.filter(id__in=idruolo)
    filedata = open('quot%d%s.txt' % (anno, ru), 'w')
    for calc in calciatori_ruolo:
	nomesquadra = calc.squadra.nome.upper()
	bonussquadra = 1 + (0.2 if nomesquadra in squadrebuone else 0.0) -  (0.08 if nomesquadra in squadrecoppe else 0.0)
	exsquadra = " " if calc.scorsoanno is None else calc.scorsoanno.squadra.nome
	if (calc.presenze is None):
		filedata.write("%s\t%s\t%s\t%d\t \t \t \t \t%.3f\n" % (calc.nome, calc.squadra.nome, exsquadra, calc.quotazione, bonussquadra))
	else:
		filedata.write("%s\t%s\t%s\t%d\t%d\t%.3f\t%.3f\t%.3f\t%.3f\n" % (calc.nome, calc.squadra.nome, exsquadra, calc.quotazione, calc.presenze, calc.fantamedia, sqrt(calc.fantamediasq**2 - calc.fantamedia**2), calc.mediavoto, bonussquadra))
    filedata.close()



def aggiorna_immagini(nomecampionato):
  """scarica da google il link delle immagini per un dato campionato"""
  campionato = Campionato.objects.get(nome=nomecampionato)
  cal_list = Calciatore.objects.filter(squadra__campionato=campionato)
  for cal in cal_list:
	  print "Considero", cal.nome, ', ', cal.squadra.nome
	  if (cal.imageurl is None):
	    if (cal.scorsoanno is not None and cal.scorsoanno.imageurl is not None) : # se c'e' quella dell'anno prima la uso
		    print "Uso l'immagine dello scorso anno"
		    cal.imageurl = cal.scorsoanno.imageurl
            else:
		    #print "Prendo un'immagine da google"
                    #cal.imageurl = getImage(cal.nome, cal.squadra.nome)
                    print "le immagini da google non sono piu' disponibili... trova un altro sistema"
            cal.save()
	  else:
		  print "Immagine gia' presente"



@transaction.atomic
def calcola_fantamedia(anno=2015):
  """calcola la fantamedia dell'anno precedente usando lo scorsoanno, se presente"""
  calciatori = Calciatore.objects.filter(squadra__campionato__nome=("Serie A %d-%d" % (anno-1, anno)), scorsoanno__isnull=False)
  somma = array([1,-1,-Decimal(0.5),3,3,-2,-1,-3,3, 1])
  for calc in calciatori:
	  print "Calcolo dati per", calc.nome
          datalist = calc.scorsoanno.voto_set.values_list('votopuro','espu', 'ammo', 'golsuazione', 'golsurigore', 'autogol', 'golsubiti', 'rigorisbagliati', 'rigoriparati', 'assist')
	  if len(datalist)==0:
		  datalist = [10*[0]]
	  fm = sum(array(datalist)*somma, axis=1)
	  calc.presenze = len(datalist)
	  sommadata = sum(datalist, axis=0)
	  calc.mediavoto = float(sommadata[0]/calc.presenze)
	  calc.golfatti = sommadata[3] + sommadata[4]
	  calc.golsubiti = sommadata[6]
	  calc.rigoriparati = sommadata[8]
	  calc.ammonizioni = sommadata[2]
	  calc.espulsioni = sommadata[1]
	  calc.assist = sommadata[-1]
	  calc.fantamedia = float(sum(fm)/calc.presenze)
	  calc.fantamediasq = float(sqrt(sum(fm*fm)/calc.presenze))
	  calc.save()

def aggiungi_quotazioni_link_annoprec(filequot, nomecampionato, nomecampionatoprec, nomeredazione, onlynew=False, datainizio=None, datafine=None):
  """aggiunge un file di quotazioni rozze al database sotto il nomecampionato, linkando ciascun calciatore ad un calciatore (se esiste) nel nomecampionatoprec
  Il file deve essere della forma id, ruolo, nome, squadra, quot, quotold, diff. Se onlynew, aggiunge solo quelli che non ci sono"""
  filedatanew = open(filequot, 'r')
  #line = filedatanew.readline()
  playersnew = []
  for line in filedatanew: #while(line != ""):
    print line
    split = line.strip().split("\t")
    playersnew.append(split)
    #line = filedatanew.readline()
  filedatanew.close()
  defaults = {}
  if (datainizio is not None and datafine is not None):
     defaults = {'datainizio': datainizio, 'datafine': datafine}
  campionato, created = Campionato.objects.update_or_create(nome=nomecampionato, defaults = defaults)
  campionato_prec = Campionato.objects.get(nome=nomecampionatoprec)
  print campionato_prec
  redazione, created = Redazione.objects.get_or_create(nome = nomeredazione,descrizione = '')
  calciatori_attuali = Calciatore.objects.filter(squadra__campionato=campionato)
  for count, split in enumerate(playersnew):
    sq, created = SquadraCampionato.objects.get_or_create(nome=split[3], campionato=campionato)
    pl = {'code': int(split[0]), 'ruolo': split[1], 'nome': split[2],
          'squadra': split[3], 'quot':float(split[4].replace(",","."))}
    cal_list = calciatori_attuali.filter(nome=pl['nome'])
    print (count+1), 'di', len(playersnew)
    print "Considero: ", pl['ruolo'], pl['nome'], pl['squadra']
    if (cal_list.count()>0 and onlynew):
	    print "Gia' presente"
	    continue
    old_cals = Calciatore.objects.filter(nome=pl['nome'], squadra__nome=pl['squadra'], squadra__campionato=campionato_prec)    # calciatori del campionato precedente che hanno stesso nome, stesso, ruolo e stessa squadra
    if (old_cals.count() == 1): # c'e' solo un match, mi fido che sia lui...
	    vecchiocal = old_cals.last()
	    print "Match con ", vecchiocal, ', ', vecchiocal.squadra.nome
    else:
       print pl['nome']
       print campionato_prec
       old_cals = Calciatore.objects.filter(nome__contains=pl['nome'], squadra__campionato=campionato_prec)    # calciatori del campionato precedente che hanno stesso nome
       if (old_cals.count() == 0):
	       vecchiocal = None
       else:
	 for i,x in enumerate(old_cals):
           print i+1, x.nome, x.squadra.nome
         var = raw_input("Inserisci l'indice della tua scelta (0 per None):")
         var = int(var) if var != "" else 1
         if(var == 0):
	   vecchiocal = None
         else:
	   vecchiocal = old_cals[var-1]
	   print 'Scelta per', old_cals[var-1].nome, 'del', old_cals[var-1].squadra.nome, 'registrata'
    if (cal_list.count() == 1):
	    print "Il giocatore esiste gia' nel database... lo aggiorno"
	    cal = cal_list.last()
	    cal.scorsoanno = vecchiocal
	    cal.squadra = sq
            cal.save()
	    ruolo_list = cal.ruolo.filter(redazione=redazione)
	    if (ruolo_list.exists()):
		    ru = ruolo_list.last()
		    ru.nome = pl['ruolo']
	    else:
                    ru = Ruolo(calciatore=cal, redazione=redazione, nome=pl['ruolo'])
    else:
	    cal = Calciatore(nome=pl['nome'], squadra=sq, quotazione=pl['quot'], scorsoanno=vecchiocal)
            cal.save()
            ru = Ruolo(calciatore=cal, redazione=redazione, nome=pl['ruolo'])
    ru.save()
    print cal, 'salvato con successo'

def aggiungi_quotazioni_complete(filequot, nomecampionato, datainizio, datafine, nomeredazione):
  """aggiunge un file di quotazioni al database, sotto il nomecampionato"""
  filedatanew = open(filequot, 'r')
  line = filedatanew.readline()
  playersnew = []
  while(line != ""):
    split = line.strip().split("\t")
    playersnew.append(split)
    line = filedatanew.readline()
  filedatanew.close()
  #teams = list(set([x[3].title() for x in playersnew]))
  campionato, created = Campionato.objects.get_or_create(nome=nomecampionato, datainizio=datainizio, datafine=datafine)
  print Calciatore.objects.filter(squadra__campionato__nome=nomecampionato)
  print campionato, "creato"
  Calciatore.objects.filter(squadra__campionato__nome=nomecampionato).delete()
  SquadraCampionato.objects.filter(campionato__nome=nomecampionato).delete()
  redazione, created = Redazione.objects.get_or_create(nome = nomeredazione,descrizione = '')
  #for sq in teams:
  #  sqobj = SquadraCampionato.objects.create(nome=sq, campionato=campionato)
  #  print sqobj, "creata"
  for split in playersnew:
    sq, created = SquadraCampionato.objects.get_or_create(nome=split[3], campionato=campionato)
    pl = {'code': int(split[0]), 'ruolo': split[1], 'nome': split[2],
          'squadra': split[3], 'exsquadra': split[7], 'quot':float(split[4].replace(",","."))}
    pl['imgurl'] = getImage(pl['nome'],pl['squadra'])
    if(split[8] != "-1"):
      pl['fantamedia'] = float(split[8])
      pl['fantamediasq'] = float(split[9])
      pl['pres'] = int(split[10])
      pl['mediavoto'] = float(split[11])/int(split[10])
      pl['gf'] = int(float(split[12])+float(split[16]))
      pl['gs'] = int(float(split[13]))
      pl['rp'] = int(float(split[14]))
      pl['ammo'] = int(float(split[18]))
      pl['espu'] = int(float(split[19]))
      pl['assist'] = int(float(split[20]))
    else:
      for f in notalwaysfield:
        pl[f] = -1
    print pl
    cal = Calciatore(nome=pl['nome'], squadra=sq, exsquadra=pl['exsquadra'], quotazione=pl['quot'], fantamedia=pl['fantamedia'], fantamediasq=pl['fantamediasq'],
mediavoto=pl['mediavoto'], presenze=pl['pres'], golfatti=pl['gf'], golsubiti=pl['gs'], rigoriparati=pl['rp'], ammonizioni=pl['ammo'], espulsioni=pl['espu'], assist=pl['assist'], imageurl=pl['imgurl'])
    cal.save()
    ru = Ruolo(calciatore=cal, redazione=redazione, nome=pl['ruolo'])
    ru.save()
    print cal




