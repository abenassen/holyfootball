$(function() {
 $('.pill').button().click(function() {
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
 });
 $.ajaxSetup({ cache: false }); // This part addresses an IE bug. without it, IE will only load the first number and will never refresh
   setInterval(function() {
   console.log("ciao");
   $('#textarea').load('/chat/messages');
   }, 3000); // the "3000" here refers to the time to refresh the div. it is in milliseconds.
 });

});

