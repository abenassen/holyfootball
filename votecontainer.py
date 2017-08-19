from numpy import *
"""gestisce automaticamente tutti i file di voti"""

from votereader import *
class VContainer:
    def __init__(self):
	self.VOTEDAT = []		#e' una lista di tuple (data, giornata,anno, matchday) con i voti di ogni giornata
	self.listallvotefile()
	self.order()
	self.arrayDAT = array(self.VOTEDAT)
    def listallvotefile(self):
	"""cerca tutti i file contenti voti e li aggiunge alla lista comune VOTEDAT nella forma (data del match, giornata,stagione, oggetto matchday contenente i voti)"""
	def adder(ext, dirname, filenames):
	    def f1(filename,dirname=dirname): return self.checkandadd(os.path.join(dirname,filename))
	    cleanedfilenames = map(f1,filenames)
	    def f2(m): return m!=-1
	    cleanedfilenames = filter(f2, cleanedfilenames)
	    self.VOTEDAT = self.VOTEDAT+cleanedfilenames
	os.path.walk(os.path.abspath("."), adder,"")
    def order(self):
      def cmp(x,y): return (x[0]-y[0]).days
      self.VOTEDAT =  sorted(self.VOTEDAT,cmp)

    def getFileList(self): 
	"""restituisce i dati delle varie giornate"""
	return self.VOTEDAT

    def afterdate(self,date):
	"""restituisce i dati delle varie giornate a partire da date"""
	def gooddata(x): 
	  return (x[0]-date).days>0
	return filter(gooddata, self.VOTEDAT)

    def tilldate(self, date, num = -1):
	"""restituisce i dati delle ultime num giornate fino a date"""
	#def gooddata(x):
	#  return (x[0]-date).days<-1
	#res = filter(gooddata, self.VOTEDAT)
	#if num == -1: num = len(res)
	#return res[len(res)-num:len(res)]
	point = self.findsorted(self.VOTEDAT,date)
	#print "point",point
	return self.VOTEDAT[max(point-num,0):point]
	
    def findsorted(self, lista, date):
      """cerca date presupponendo lista ordinata: lista contiene oggetti tipo VOTEDAT e restituisce il numero di termini precedenti a date"""
      bisection = len(lista)
      #print "bis",bisection
      if bisection == 0:
	 return 0
      if bisection == 1: 
	return int((lista[0][0]-date).days<-2)
      bisection = bisection/2
      if (lista[bisection][0]-date).days<-2:
	return bisection+self.findsorted(lista[bisection::],date)
      else: return self.findsorted(lista[0:bisection],date)
      

    def checkandadd(self,filename):
	"""converte il nome file in un oggetto del tipo (datamatch, giornata, filename, READorNOT=False) da aggiungere a VOTEDAT Se non e' un file corretto restituisce -1"""	
	justname = os.path.basename(filename)
	year = os.path.split(os.path.dirname(filename))[::-1][0]
	if not(os.path.isfile(filename)) or justname.find(".") == -1: return -1
	splitting1 = justname.split(".")
	if len(splitting1) != 3  or not(justname[0].isdigit()) or (splitting1[2]!= "xls" and splitting1[2]!= "xlsx"): return -1
	#print filename, splitting1
	return (getdatetimefromstring(splitting1[1]),int(splitting1[0]),year, Matchday(filename))	#restituisce una tupla (data del match, giornata,stagione, oggetto matchday contenente i voti)

    def seasonmean(self, name, team, role, season):
       """restituisce la fantamedia, la fantamedia quadratica e il numero di giornate disputate stagionali del giocatore"""
       seas = [x[3] for x in self.VOTEDAT if x[2] == str(season)]
       #datedate = [x[1] for x in self.VOTEDAT if x[2] == str(season)]
       #print len(seas)
       total = 0
       sqtotal = 0
       count = 0
       cc = 0
       othdata = 0
       for m in seas:
         #print datedate[cc]
         #cc = cc + 1
         m.getteams()
         pl = m.playerfind(name, team, role)
	 if pl != -1:
	  count = count + 1
	  tmp = pl.fantamedia()
          #print m.filename,tmp
          total = total + tmp
          sqtotal = sqtotal + tmp*tmp
          othdata += pl.datalist
          pl.datalist
       if count != 0:
         #print name, total, count, total/count
         return [total/count, sqrt(sqtotal/count), count]+othdata.tolist()
       return [-1, -1, 0]


