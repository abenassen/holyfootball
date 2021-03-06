import os
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'fanta.settings'
application = get_wsgi_application()

from django.contrib.auth.models import User
from fantaapp.models import *  
from django.conf import settings


def setusers():
	if not(User.objects.filter(username="andrea").exists()):
	  user = User.objects.create_user('andrea', 'andrea@thebeatles.com', 'andrea')
	if not(User.objects.filter(username="ciccio").exists()):
	  user = User.objects.create_user('ciccio', 'andrea@thebeatles.com', 'ciccio')
	if not(User.objects.filter(username="gian").exists()):
	  user = User.objects.create_user('giancarlo', 'andrea@thebeatles.com', 'giancarlo')
	if not(User.objects.filter(username="marco").exists()):
	  user = User.objects.create_user('marco', 'andrea@thebeatles.com', 'marco')
	if not(User.objects.filter(username="scialpi").exists()):
	  user = User.objects.create_user('franco', 'andrea@thebeatles.com', 'franco')
	if not(User.objects.filter(username="enrico").exists()):
	  user = User.objects.create_user('enrico', 'andrea@thebeatles.com', 'enrico')
	if not(User.objects.filter(username="rocco").exists()):
	  user = User.objects.create_user('rocco', 'andrea@thebeatles.com', 'rocco')
	if not(User.objects.filter(username="vince").exists()):
	  user = User.objects.create_user('vincenzo', 'andrea@thebeatles.com', 'vincenzo')
	if not(User.objects.filter(username="francesco").exists()):
	  user = User.objects.create_user('francesco', 'andrea@thebeatles.com', 'francesco')
	if not(User.objects.filter(username="almi").exists()):
	  user = User.objects.create_user('almi', 'andrea@thebeatles.com', 'almi')

def setredazione():
	if not(Redazione.objects.filter(nome="Napoli").exists()):
	  user = Redazione.objects.create(nome = 'Napoli',descrizione = 'La redazione di fantagazzetta')

def setlega():
    user = User.objects.get(username='andrea')
    allen = user.allenatore_set.all()[0]
    lega = allen.lega
    for u in User.objects.all():
      if not(u.allenatore_set.filter(lega_id=lega.id).exists()):
	      allnew = lega.nuovo_allenatore(u)
	      allnew.save()





def main():
  setusers()
  setredazione()
  setlega()

if __name__ == "__main__":
  main()
