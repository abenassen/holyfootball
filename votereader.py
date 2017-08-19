from htmlparser import *
from numpy import *
from lib import *
import os
import difflib
from openpyxl import load_workbook

#'Cod.', 'Ruolo', 'Nome','VF','Gol Fatto','Gol Subito', 'Rigore Parato', 'Rigore Sbagliato','Rigore Segnato', 'Autorete', 'Ammonizione', 'Espulsione', 'Assist', 'Gdv', 'Gdp'
class Team:
    def __init__(self, n,plist):
        self.name = n
        self.plist = plist
        self.betm = self.evaluatebetmedia()
    def appendplayer(self,pl):
        self.plist.append(pl)
        #print pl.datalist
        self.betm = self.evaluatebetmedia()
    def __repr__(self): return self.name+"\n"
    def evaluatebetmedia(self):
        """restituisce la media voti della squadra calcolati con i pesi appositi per le scommesse"""
        def betm(pl): return pl.betmedia()
        return sum(map(betm,self.plist))/len(self.plist)
    def betmedia(self):
        """restituisce la media voti gia' calcolata"""
        return self.betm

def getnum(cell): 
        if cell=="SV" or cell=="6*" or cell=="-": 
           return None   #giocatori senza voto
        if isinstance(cell, basestring):
           cell = cell.replace(",",".")
           cell = float(cell)
        if isinstance(cell, long):
           cell = int(cell)
        return cell

class Player:
    #def __init__(self,r,n,vf, gf,gs,rp,rsb,rs, au, amm,esp,ass,gdv,gdp):    
    #    self.name = n
    #    self.role = r
    #    self.datalist = array([vf,gf,gs,rp,rsb,rs,au,amm,esp,ass,gdv,gdp])
    def __init__(self, r, n, dl):
        self.name = n
        self.role = r
        if dl[0] > 10: dl[0] = dl[0]/10  # su fantagazzetta a volte dimenticano la virgola, quindi se il voto supera 10 divido per 10
        if len(dl) == 13: 
          dl = dl.tolist()
          dl[9] = dl[9] + dl[10]
          dl[10] = "toremove"
          dl.remove("toremove")
        self.datalist = array(dl)
        self.fantaweights = array([1,3,-1,3,-3,3,-2,-0.5,-1,1,0,0])
	self.betweights = [1,3,-3,1,-1,3,-1,-0.5,-1,1,6,4]
    def media(self):
        """restituisce il voto del giocatore senza malus o bonus"""
        return self.datalist[0]
    def betmedia(self):
	"""restituisce la media voti del giocatore calcolata con i pesi appositi per le scommesse"""
	if (self.datalist[0] is None):
		return -1
        return sum(self.datalist*self.betweights)
    def fantamedia(self):
	"""restituisce la fantamedia voti"""
        voto = -1
        if(self.datalist[0] is not None): 
          voto = sum(self.datalist*self.fantaweights)  
        #if (self.datalist[0] == 5.999) and (abs(voto-self.datalist[0]) <= 0.5 and self.role != 'P'): # e' un senza voto
        #  voto = -1.
	return voto
    def __repr__(self): return self.name+"\n"

class Matchday:
  def __init__(self, filename):
    self.teams = []
    self.text = ""
    self.filename = filename
  def getteams(self):
    if len(self.teams)==0:
      self.readdata()
    return self.teams
  def readxlsx(self):
    print "leggo il file xlsx"
    row = 5
    wb = load_workbook(self.filename)
    try: 
       wbs = wb["Napoli"] # take redazione Napoli 
    except KeyError:
       wbs = wb["Fantagazzetta"]
    while(True):
      if (wbs["A" + str(row)].value==None and wbs["B" + str(row)].value==None): # it is an empty row, it must be the last one
         break 
      elif(wbs["B" + str(row)].value == None): # it should be a team name
         teamname = wbs["A" + str(row)].value
         newteam = Team(teamname, [])
         self.teams.append(newteam)
      elif isinstance(wbs["A" + str(row)].value, long): 
        ruolo = wbs['B' + str(row)].value
        if ruolo != "ALL":  
           nome = wbs['C' + str(row)].value
           dl = [x.value for x in wbs['D' + str(row) + ':P' + str(row)][0]]
           dl = array(map(getnum,dl))
           #print nome, ruolo, dl
           pl = Player(ruolo, nome, dl)
           newteam.appendplayer(pl)
      #print row
      row += 1
  def readdata(self):
    if self.filename.endswith(".xlsx"): # it is an xlsx file
       self.readxlsx()
       return
    self.fileread(self.filename)
    [self.elaboratetab(x) for x in self.tabsofplayer()]
    self.text = ""
  def fileread(self,filename):
    """legge il contenuto del file e lo mette in TEXT"""
    file = open(filename, 'r')
    self.text = file.readline()
    self.text = self.cleantext(self.text)	#fa pulizia
    file.close()
  def cleantext(self,text):
    """ripulisce il testo da alcuni caratteri html"""
    t = text.replace("&nbsp;"," ")
    t = t.replace("\xe0","a'")
    return t
  def getjustteams(self, datateams):
    """restituisce solo i dati delle squadre in datateams"""
    self.getteams()
    return [x for x in self.teams if datateams.count(x.name)>0]
  def tabsofplayer(self):
    """legge la tabella di tutti i giocatori con voti"""
    tabs = getindextabnotag(self.text)   #chiama l'istruzione dalla libreria htmlparser per estrarre le tabelle da un file  html
    return tabs
  def elaboratetab(self,tab):
    """elabora una tabella di dati estraendone i giocatori da mettere nelle squadre"""
    mytab = filter(self.usefulrow, tab)
    newteam = Team("",[])
    for row in mytab:
        if len(row) == 1 : 
            newteam = Team(self.getfirstworld(row[0]).title(), [])
            self.teams.append(newteam)
        else: newteam.appendplayer(self.readplayer(row))
  def readplayer(self,row):
    """restituisce un giocatore dalla riga di dati"""
    ruolo = row[1]
    nome = row[2]
    if ruolo == "ALL" :
        dl = zeros(12)
        dl[0] = getnum(row[3])
        return Player(ruolo,nome,dl)
    all = row[3::]
    dl = array(map(getnum,all))
    return Player(ruolo, nome, dl)
  def getfirstworld(self,txt):
    """restituisce la prima parola da un testo"""
    return txt[0:txt.find(" ")]
  def usefulrow(self,row):
    """restituisce True se la riga contiene dei dati utili"""
    if len(row) == 1 and row[0].isupper(): 
        return False
    if len(row) == 1 and not(self.getfirstworld(row[0]).isupper()): return False
    if len(row)>1 and row[3]=="VF": 
        return False
    return True
  def playerfind(self, name, team, role):  #get a player by name or return -1 if it is not present
    for t in self.teams:
      if team == t.name.upper():
        for pl in t.plist:
          if (difflib.SequenceMatcher(None, pl.name, name).ratio()>0.9 and role == pl.role):
            #print difflib.SequenceMatcher(None, pl.name, name).ratio(), pl.name, team, role, name,self
            return pl
    return -1
  


