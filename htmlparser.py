
import urllib

def readpage(link):
    """restituisce il contenuto della pagina web al link"""
    f = urllib.urlopen(adjustlink(link))
    s = f.read()
    f.close()
    return s 



def adjustlink(link):
    """controlla che il link sia nella forma corretta, altrimenti lo ripara"""
    link = link.lower()
    if link.startswith("www"): link = "http://"+link
    return link


def gettagdivs(buffer, tag):
    """restituisce le stringe contenute tra i tag nel buffer html"""
    res = []
    return isolatetag(buffer, res, tag)

    
    
def isolatetag(buf, r, tag):
    """si autoitera aggiungendo in r tutte le parti contenute all'interno di ciascun tag"""
    i = buf.find("<"+tag)
    #print "i",i
    i_f = buf.find(">",i)+1
    #print "if",i_f
    f = buf.find("</"+tag,i+1)
    n = buf.find("<"+tag,i+1)
    #print "n",n
    if n!=-1 and (n<f or f==-1): 
      f=n
    if f==-1: f = len(buf)
    #print "f",f
    if i != -1 and f > i: r.append(buf[i_f:f])
    else: return r
    newbuf = buf[f::]
    return isolatetag(newbuf, r, tag)


def cleanfield(text):
  toberemoved = ("\t","\xa0","\n","\r")
  for char in toberemoved:
    text = text.replace(char,"")
  text = text.replace(",",".")
  return text

def getindextabnotag(buffer):
    """restituisce una lista di matrici per ogni tabella nel buffer html"""
    tables = gettagdivs(buffer, "table")
    def ftr(tab):
        return gettagdivs(tab, "tr")
    def ftd(row):
        return map(removealltag,gettagdivs(row, "td"))
    def ftab(tab):
        rows = ftr(tab)
        return map(ftd, rows)
    return  map(ftab,tables)
    

def removetagleftright(string):
    """rimuove tutti i tag a sinistra e a destra da una stringa"""
    return removerighttag(removelefttag(string))


def removelefttagchar(string, leftchar, rightchar):
    """rimuove i tag, segnalati dai char, a sinistra da una stringa"""
    if not(string.startswith(leftchar)): return string
    return removelefttagchar(string[string.find(rightchar)+1::], leftchar,right)

def removelefttag(string):
    return removelefttagchar(string, "<",">")

def removerighttag(string):
    reversedstring = string[::-1]
    reversedstring = removelefttagchar(reversedstring, ">", "<")
    return reversedstring[::-1]


def removealltag(string):
    """rimuove tutti i tag da una stringa"""
    i = string.find("<")
    f = string.find(">")                         
    if i==-1 or f<i: return string
    newstring = string[0:i]+string[f+1::]                        
    return removealltag(newstring)
