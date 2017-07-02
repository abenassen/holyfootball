from django.conf.urls import url

from asta import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    #url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    url(r'^(?P<astaid>[\d]+)/script$', views.asta_script, name='asta_script'),
    url(r'^(?P<astaid>[\d]+)/$', views.gestione_asta, name='gestione_asta'),
    url(r'^crea/conferma/$', views.crea_asta_conferma, name='crea_asta_conferma'),
    url(r'^crea/$', views.crea_asta, name='crea_asta'),
    url(r'^(?P<astaid>[\d]+)/offerte/(?P<numero>\d+)/$', views.lista_offerte),
    url(r'^(?P<astaid>[\d]+)/acquistati/(?P<numero>\d+)/$', views.lista_acquistati),
    url(r'^(?P<astaid>[\d]+)/chiamati/(?P<numero>\d+)/$', views.lista_chiamati),
    url(r'^scheda/(?P<id_calciatore>\d+)/$', views.html_calciatore),
    url(r'^scheda/$', views.html_calciatore),
    url(r'^(?P<astaid>[\d]+)/resettaasta/$', views.resetta_asta),
    #url(r'^banditore/$', views.banditore_asta),
    #url(r'^banditore/login/$', views.banditore_login),
    url(r'^(?P<astaid>[\d]+)/faiofferta/$', views.faiofferta),
    url(r'^(?P<astaid>[\d]+)/inserisciofferta/(?P<numero>\d+)/$', views.faiacquisto),
    url(r'^(?P<astaid>[\d]+)/chiamagiocatore/$', views.chiama_giocatore, name='chiama_giocatore'),
    url(r'^(?P<astaid>[\d]+)/resoconto/$', views.resoconto),
    url(r'^(?P<astaid>[\d]+)/cancellaofferte/(?P<numero>\d+)/$', views.cancella_offerte),
    url(r'^(?P<astaid>[\d]+)/cancellaacquistati/(?P<numero>\d+)/$', views.cancella_acquistati),
    url(r'^(?P<astaid>[\d]+)/cancellachiamati/(?P<numero>\d+)/$', views.cancella_chiamati),
    url(r'^(?P<astaid>[\d]+)/aggiornamento/$', views.aggiornamento_periodico, name='aggiornamento'),
    url(r'^(?P<astaid>[\d]+)/rimuoviripetizioni/$', views.rimuoviripetizioni),
    #url(r'^prova/$', views.prova),
    #url(r'^confronta/$', views.confronta),
    #url(r'^salvaconfronto/$', views.salvaconfronto, name = "salvaconfronto"),
    ### parte dedicata al mercato
    url(r'^(?P<astaid>[\d]+)/nuovaofferta/$', views.nuovaofferta, name='nuovaofferta'),
    url(r'^(?P<astaid>[\d]+)/resocontomercato/$', views.resoconto_mercato, name='resocontomercato'),
    url(r'^(?P<astaid>[\d]+)/rilanciaofferta/(?P<offid>[\d]+)/$', views.nuovaofferta, name='rilanciaofferta'),
    url(r'^(?P<astaid>[\d]+)/eliminaofferta/(?P<offid>[\d]+)/$', views.elimina_offerta, name='eliminaofferta'),
    url(r'^(?P<astaid>[\d]+)/approvaofferta/(?P<offid>[\d]+)/$', views.approva_offerta, name='approvaofferta'),
]
