#!/usr/bin/python3

from splinter import Browser
from selenium.common.exceptions import StaleElementReferenceException
from splinter.exceptions import ElementDoesNotExist	
import requests
import json      

def leggivotilive(browser, url):
	    # Visit URL
	    browser.visit(url)
	    elems = browser.find_by_css(".btn.fab.btn-default.btn-raised.whitebtn2")
	    links = [x._element.get_attribute('href') for x in elems]
	    links = list(filter(lambda x: x.find("voti") != -1, links))
	    return links
	    
	    
	    
def leggimatch(browser, url = "http://www.fantagazzetta.com/live-serie-a/Napoli#voti"):
	browser.visit(url)
	while(True):
		try:
			elems = browser.find_by_css(".lteam.pname") + browser.find_by_css(".rteam.pname")
			listagiocatori = []
			for gioc in elems:
				giocatore = {
				 'assist': 0, 'golsuazione': 0, 'golsurigore': 0, 'ammo': 0, 'espu' :0,
				 'autogol': 0, 'golsubiti': 0, 'rigorisbagliati' :0, 'rigoriparati': 0,
				 'goldellavittoria' : 0, 'goldelpareggio': 0 
				 }
				print("Inizio analisi nuovo giocatore...")	
				if len(gioc.find_by_css(".nlvoti")) == 0:
				   print("Impossibile leggere il nome del giocatore... Salto")
				   continue
				giocatore['nome'] = gioc.find_by_css(".nlvoti").html
				print("Leggo i dati di ", giocatore['nome'])
				giocatore['ruolo'] = gioc.find_by_css(".role").html
				giocatore['votopuro'] = gioc.find_by_css(".sqnum").html
				rsp = gioc.find_by_css(".rsp")
				linka = rsp.find_by_css("a")
				for link in linka:
					txt = link.html
					print(txt)
					if txt.find("golsubito") != -1:
						giocatore['golsubiti'] += 1
					elif txt.find("golfatto") != -1:
						giocatore['golsuazione'] += 1
					elif txt.find("rigoresegnato") != -1:
						giocatore['golsurigore'] += 1 
					elif txt.find("assist") != -1:
						giocatore['assist'] += 1 
					elif txt.find("amm") != -1:
						giocatore['ammo'] += 1 
					elif txt.find("esp") != -1:
						giocatore['espu'] += 1 
					elif txt.find("golvittoria") != -1:
						giocatore['goldellavittoria'] += 1 
					elif txt.find("golpareggio") != -1:
						giocatore['goldelpareggio'] += 1 
					elif txt.find("autogol") != -1:
						giocatore['autogol'] += 1 
					elif txt.find("rigoresbagliato") != -1:
						giocatore['rigorisbagliati'] += 1 
					elif txt.find("rigoreparato") != -1:
						giocatore['rigoriparati'] += 1
				listagiocatori.append(giocatore)
		except StaleElementReferenceException:
			pass
		else:
			break
	return listagiocatori	
			
		



def leggitutto(browser, url = "http://www.fantagazzetta.com/live-serie-a"):
      links = leggivotilive(browser, url)
      listagiocatori = []
      for l in links:
        print("Analizzo il link" , l)
        listagiocatori = listagiocatori + leggimatch(browser, l)
      url = 'http://abenassen.pythonanywhere.com/fanta/uploadvoti/'
      headers = {'content-type': 'application/json'}
      response = requests.post(url, data=json.dumps(listagiocatori), headers=headers)
      print("Status ",response.status_code)
      print("Text ", response.text)
      return listagiocatori
      
      
def main():
   with Browser() as browser:
   	return leggitutto(browser)
      
if __name__ == "__main__":
	main()   

