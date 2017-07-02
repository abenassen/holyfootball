
$(function() {
 var schedaclonata = $("#schedacorrente").clone();
 var chiama = function(event) {    event.preventDefault();
                                   $('#statusbar').html("chiamata in corso...");
                                   $('#statusbar').load("{% url 'chiama_giocatore' legahash=legahash astaid=astaid %}?" + $.param({ruolo: $("#ruolosel").val()}),function(response, status, xhr) {
										console.log(xhr.responseText)	
										if(xhr.status === 200 && $("#schedacorrente").html()==="<h1>Asta completata!</h1>") $("#schedacorrente").replaceWith(schedaclonata);
										if (xhr.status === 402) {
                                                                                  $("#statusbar").html("Asta completata");
                                                                                  $("#schedacorrente").html("<h1>Asta completata!</h1>");
                                                                                }
                                                                                });};
 var annullachiama = function(event) {  event.preventDefault();
                                   $('#statusbar').html("Annullamento in corso..."); 
                                   $('#statusbar').load("cancellachiamati/1/");
                                   if($("#schedacorrente").html()==="<h1>Asta completata!</h1>") $("#schedacorrente").replaceWith(schedaclonata);
				   //aggiornachiamati(); 
				   };
 var offricorrente = function(event, successfun) {
  successfun = typeof successfun !== 'undefined' ? successfun : function(txt) {
                                                                    $('#statusbar').html(txt);
                                                                    console.log(txt);
                                                                    //aggiornaofferte();
                                                                };
    event.preventDefault();
    $('#statusbar').html("Inserimento in corso...");
    $.ajax({
    // the URL for the request
    url: "faiofferta/",
    data: {
    csrfmiddlewaretoken: "{{ csrf_token }}",
    soldi: $('input[name=soldi]').val(),
    calciatore: $('#scheda_id').html(),
    allenatore: $('#allenatore').val(),
    },
    // whether this is a POST or GET request
    type: "POST",
    // the type of data we expect back
    dataType : "html",
    // code to run if the request succeeds;
    // the response is passed to the function
    success: successfun,
    // code to run if the request fails; the raw request and
    // status codes are passed to the function
    error: function( xhr, status,error ) {
    $('#statusbar').html("L'offerta non è adata a buon fine, controlla che fosse ammessa!");
    console.log(xhr.statusText);
    console.log(status);
    console.log(error);
    },
    // code to run regardless of success or failure
    complete: function( xhr, status ) {	    
      console.log(xhr.responseText);	
    }
  });
 };
  var acquistodiretto = function(event) { offricorrente(event, function(txt) { $('#statusbar').load("inserisciofferta/0"); });
                        };
/* var aggiornascheda = function() {
  $("#schedacorrente").load("/fanta/scheda/");
  };
 var aggiornaofferte = function() {
  $("#ultimeofferte").load("/fanta/offerte/5/");
  };
 var aggiornacquisti = function() {
  $("#ultimiacquistati").load("/fanta/acquistati/5/");
  };
 var aggiornachiamati = function() {
  $("#ultimichiamati").load("/fanta/chiamati/5/");
  };
 var resocontoallenatori = function() {
  $("#resocontoallenatori").load("/fanta/resoconto/");
  }; */
 var ruoli = new Array("P","D","C","A");
 var aggiornamento_periodico = function() {
  console.log("eseguo!");
  $.getJSON( "{% url 'aggiornamento' legahash=legahash astaid=astaid %}", function(data) {
                        //console.log( "success" );
                        string = '';
                        for (var i = 0; i < data.offerte.length; i++) {
                          //alert(data.offerte[i].stringa);
                          string = string + '<option value="' + data.offerte[i].id + '">' + data.offerte[i].stringa + "</option>\n";
                        }
                        $('#ultimeofferte').html(string);
                        string = '';
                        for (var i = 0; i < data.acquistati.length; i++) {
                          string = string + '<option value="' + data.acquistati[i].id + '">' + data.acquistati[i].stringa + "</option>\n";
                        }
                        $('#ultimiacquistati').html(string);
                        string = '';
                        for (var i = 0; i < data.chiamati.length; i++) {
                          string = string + '<option value="' + data.chiamati[i].id + '">' + data.chiamati[i].stringa + "</option>\n";
                        }
                        $('#ultimichiamati').html(string);
                        string = '';
                        for (var i = 0; i < data.allenatori.length; i++) {
                          //string = string + '<option value="' + data.chiamati[i].id + '">' + data.chiamati[i].stringa + "</option>\n";
                          string = string + "<tr><td>"+data.allenatori[i].nome+"</td>"+
                                            "<td>" + data.allenatori[i].por+"</td>" +
                                            "<td>" + data.allenatori[i].dif+"</td>" +
                                            "<td>" + data.allenatori[i].centr+"</td>" +
                                            "<td>" + data.allenatori[i].att+"</td>" +
                                            "<td>" + data.allenatori[i].budget+"</td></tr>";
                        }
                        $('#tabella_allenatori').html(string);
			//console.log(data.calciatore);
                        for (var i in data.calciatore) {
                          if (data.calciatore.hasOwnProperty(i)) {
                            var value = data.calciatore[i];
                            if(Math.floor(data.calciatore[i]) != data.calciatore[i] && $.isNumeric(data.calciatore[i])) {
                                value = data.calciatore[i].toFixed(2);
                            }
                            if(value == -1) value = "-";
                            else if (i == "ruolo") {
                                if(value == 'P') {
                                  $('#scheda_portiere').show();
                                  $('#scheda_attaccante').hide();
                                }
                                else {
                                  $('#scheda_portiere').hide();
                                  $('#scheda_attaccante').show();
                                }
                                //value = ruoli[value];
                            }
                            $('#scheda_' + i).html(value);
                        }}
                        $('#foto').attr('src', data.calciatore.imageurl);
            })
                    .always(function() {setTimeout(aggiornamento_periodico,2000)});
 };
 $('#mostrarose').click(function(event) { event.preventDefault();
                                          $('#roseframe').toggle();
                        });
 $('#acquistodiretto').button().click(acquistodiretto);
 $('#rilancia').button().click(offricorrente);
 $('#chiamagiocatore').click(chiama);
 $('#prossimo').button().click(chiama);
 $('#inserisciofferta').click(function(event) { event.preventDefault();
                                                $('#statusbar').load("inserisciofferta/"+ $('select[name=ultimeofferte] option:first-child').val());
                        //aggiornacquisti();
 						});
 $('#cancellaultimaofferta').click(function(event) { event.preventDefault();
                                                     $('#statusbar').html("Cancellazione in corso..."); 
                                                     $('#statusbar').load("cancellaofferte/1/");
						     //aggiornaofferte();
                                  			});
 $('#cancellaofferte').click(function(event) {  event.preventDefault();
                                                $('#statusbar').html("Cancellazione in corso..."); 
                                                $('#statusbar').load("cancellaofferte/0/");
						//aggiornaofferte();
					     });

 $('#cancellaultimoacquisto').click(function(event) { event.preventDefault();
                                                      $('#statusbar').html("Cancellazione in corso..."); 
                                                      $('#statusbar').load("cancellaacquistati/1/");
						      //aggiornacquisti();
						    });
 $('#cancellaacquisti').click(function(event) { event.preventDefault(); 
                                                $('#statusbar').html("Cancellazione in corso..."); 
                                                $('#statusbar').load("cancellaacquistati/0/");
						//aggiornacquisti();
                                  });
 $('#resettaasta').click(function(event) { event.preventDefault();
                                           $('#statusbar').html("Reset in corso..."); 
                                           $('#statusbar').load("resettaasta/");
					   //aggiornatutto();
               				 });
 $('#annullachiamata').click(annullachiama);
 $('#precedente').button().click(annullachiama);
 aggiornamento_periodico();
/* setInterval(function() {
    aggiornascheda();
    aggiornaofferte();
    aggiornacquisti();
    aggiornachiamati();
    resocontoallenatori();
 }, 2000);
 aggiornascheda();
 aggiornaofferte();
 aggiornacquisti();
 aggiornachiamati();
 resocontoallenatori();
*/
 
});
