from datetime import *

DATETIME = datetime.today()

def getdatetimefromstring(str):
    """converte la stringa in una data. se manca l'ora imposta predefinito le 15. Se la stringa e' vuota restituisce l'ultimo valore prodotto, o l'ora attuale se e' la prima esecuzione."""
    global DATETIME
    if str == "": return DATETIME
    dateandtime = str.split(" ")
    #print dateandtime
    if len(dateandtime) == 1: dateandtime.append("15:00")
    dateandtime[0] = dateandtime[0].replace("/","-")
    date = map(int,dateandtime[0].split("-"))
    if date[2]<1000: date[2] = date[2]+2000
    if date[2]>2050:date[2] = date[2]-100
    time = map(int,dateandtime[1].split(":"))
    DATETIME = datetime(date[2],date[1],date[0],time[0],time[1])
    return DATETIME