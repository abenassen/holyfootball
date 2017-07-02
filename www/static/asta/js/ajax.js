$(function() {
 var fun = function() {
  $('#textarea').scrollTop($('#textarea')[0].scrollHeight);
  //console.log($("#login").val()+ $("#chattext").val());
  $.ajax({
    // the URL for the request
    url: "/chat/messages/",
    // the data to send (will be converted to a query string)
    data: {
    login: $("#login").val(),
    txt: $("#chattext").val()
    },
    // whether this is a POST or GET request
    type: "GET",
    // the type of data we expect back
    dataType : "html",
    // code to run if the request succeeds;
    // the response is passed to the function
    success: function(txt) {
    $("#textarea").val(txt);
    $("#chattext").val("");  
    },
    // code to run if the request fails; the raw request and
    // status codes are passed to the function
    error: function( xhr, status ) {
    console.log( "Sorry, there was a problem!" );
    },
    // code to run regardless of success or failure
    complete: function( xhr, status ) {
    //alert( "The request is complete!" );
    }
  });
  event.preventDefault();
 };
 setInterval(function() { 
 //console.log("updated!");
 $.get('/chat/messages/', function(result) {
    $('#textarea').val(result);
});
 }, 1000);
 $('.pill').button().click(fun);
 $('#chattext').keypress(function(e) {
  if(e.which == 13) fun();
 });
});
