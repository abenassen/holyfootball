#!/home/abenassen/.virtualenvs/django18/bin/python

import os
import django
import sys
sys.path.append('fanta/')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fanta.settings")
django.setup()

import completa_quotazioni
completa_quotazioni.inserisci_calendario(2018)

