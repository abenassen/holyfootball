from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from fantaapp import views


urlpatterns = [
    url(r'^test/(?P<legahash>[a-zA-Z\d]+)/$', views.test, name='test'),
    url(r'^uploadvoti/$', views.uploadvoti),
    url(r'^viewtemplate/$', views.viewtemplate, name='view_template'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^login/$', auth_views.login, {'template_name': 'fantaapp/login.html'}, name='login'),

    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/$', views.home_lega, name='aprilega'),

    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/calendario/(?P<id_comp>\d+)$', views.calendario_competizione, name='calendariocompetizione'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/amministrazione$', views.amministrazione, name='amministrazione'),

    url(r'^lega/edita_competizione/(?P<legahash>[a-zA-Z\d]+)/$', views.edita_competizione, name='editacompetizione'),



    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/calendariocoppa$', views.calendario_coppa, name='calendariocoppa'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/calendario$', views.calendario_lega, name='calendariolega'),


    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/rose$', views.rose, name='rose'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/formazionecoppa$', views.formazionecoppa, name='formazionecoppa'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/formazione/(?P<id_comp>[\d]+)/(?P<all_id>[\d]+)/$', views.formazione, name='formazione'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/formazione/(?P<id_comp>[\d]+)/$', views.formazione, name='formazione'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/nuovagiornata/conferma$', views.nuova_giornata_conferma, name='nuovagiornata_conferma'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/nuovagiornata$', views.nuova_giornata, name='nuovagiornata'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/classifica/(?P<faseid>[\d]+)/$', views.classifica, name='classifica'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/entra/$', views.entra_lega, name='entralega'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/tabellino/(?P<faseid>[\d]+)/(?P<numero_giornata>[\d]+)/$', views.tabellino, name='tabellino'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/tabellino_singolo/$', views.tabellino_singolo, name='tabellinosingolo'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/tabellino_singolo/(?P<incontro_id>[\d]+)/$', views.tabellino_singolo, name='tabellinosingolo'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/tabellino_coppa/(?P<incontro_id>[\d]+)/$', views.tabellino_coppa, name='tabellinocoppa'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/editavoto/(?P<referto_id>[\d]+)/$', views.editavoto, name='editavoto'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/editavoto/$', views.editavoto, name='editavoto'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/editarose/$', views.editarose, name='editarose'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/scambiorose/$', views.scambiorose, name='scambiorose'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/aggiungicrediti/$', views.aggiungicrediti, name='aggiungicrediti'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/generarose/$', views.genera_rose, name='generarose'),
    url(r'^lega/$', views.home_lega, name='aprilega'),
    url(r'^lega/crea$', views.crea_lega, name='crealega'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/asta/', include('asta.urls')),
    url(r'^lega/edita_squadra/(?P<legahash>[a-zA-Z\d]+)/$', views.edita_squadra, name='editasquadra'),
    url(r'^lega/(?P<legahash>[a-zA-Z\d]+)/maglia.svg$', views.maglia_colore, name='magliacolorata'),
    url(r'^lega/edita/(?P<legahash>[a-zA-Z\d]+)/$', views.crea_lega, name='editalega'),
    url(r'^homeuser/$', views.home_user),
    url(r'^$', views.home_user, name='home_utente'),
]
