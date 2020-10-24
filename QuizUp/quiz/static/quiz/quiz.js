function showPrompt() {
  var message;
  if($('input[type="radio"]:checked').length<2) {
    message = "You haven't answered all questions! ";
  }
  else {
    message = "You have answered all questions! ";
  }
  message += "Do you wanna submit right now?";
  if(confirm(message)) {
    $('form').submit();
  }
}

// Timer
var timeLeft = 5;
$('#timer').text("Time Left: "+timeLeft+" sec");

var timer = setInterval(function() {
    timeLeft--;
    $('#timer').text("Time Left: "+timeLeft+" sec");
    if(timeLeft==0) {
      clearInterval(timer);
      //$('form').submit();
    }
  }, 1000);
