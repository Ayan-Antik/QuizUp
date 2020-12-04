/*function showPrompt() {
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
var timeLeft = 10;
$('#timer').text("Time Left: "+timeLeft+" sec");

var timer = setInterval(function() {
    timeLeft--;
    $('#timer').text("Time Left: "+timeLeft+" sec");
    if(timeLeft==0) {
      clearInterval(timer);
      //$('form').submit();
    }
  }, 1000);*/

const FULL_DASH_ARRAY = 283;
const WARNING_THRESHOLD = 6;
const ALERT_THRESHOLD = 3;

const COLOR_CODES = {
  info: {
    color: "green"
  },
  warning: {
    color: "orange",
    threshold: WARNING_THRESHOLD
  },
  alert: {
    color: "red",
    threshold: ALERT_THRESHOLD
  }
};

const TIME_LIMIT = 10;
let timePassed = 0;
let timeLft = TIME_LIMIT;
let timerInterval = null;
let remainingPathColor = COLOR_CODES.info.color;

function reset()
{  onTimesUp();
    //console.log(timePassed, timeLeft, timerInterval, remainingPathColor, TIME_LIMIT);
    timePassed = 0;
    timeLft = TIME_LIMIT;
    timerInterval = null;
    remainingPathColor = COLOR_CODES.info.color;
    //console.log(timePassed, timeLeft, timerInterval, remainingPathColor, TIME_LIMIT);
    document.getElementById("app").innerHTML = `
    <div class="base-timer">
      <svg class="base-timer__svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g class="base-timer__circle">
          <circle class="base-timer__path-elapsed" cx="50" cy="50" r="45"></circle>
          <path
            id="base-timer-path-remaining"
            stroke-dasharray="283"
            class="base-timer__path-remaining ${remainingPathColor}"
            d="
              M 50, 50
              m -45, 0
              a 45,45 0 1,0 90,0
              a 45,45 0 1,0 -90,0
            "
          ></path>
        </g>
      </svg>
      <span id="base-timer-label" class="base-timer__label">${formatTime(
        timeLft
      )}</span>
    </div>
    `;

    startTimer();

}

function onTimesUp() {
  clearInterval(timerInterval);
}

function startTimer() {
  timerInterval = setInterval(() => {
    timePassed = timePassed += 1;
    timeLft = TIME_LIMIT - timePassed;
    document.getElementById("base-timer-label").innerHTML = formatTime(
      timeLft
    );
    setCircleDasharray();
    setRemainingPathColor(timeLft);

    if (timeLft === 0) {

      //console.log("TIME UP");
      onTimesUp();
    }
  }, 1000);
  //console.log("Time Interval: ", timerInterval)
}

function formatTime(time) {

  const minutes = Math.floor(time / 60);
  let seconds = time % 60;

  if (seconds < 10) {

    seconds = `0${seconds}`;


  }


  return `${minutes}:${seconds}`;
}

function setRemainingPathColor(timeLeft) {
  const { alert, warning, info } = COLOR_CODES;
  if (timeLeft <= alert.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(warning.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(alert.color);
  } else if (timeLeft <= warning.threshold) {
    document
      .getElementById("base-timer-path-remaining")
      .classList.remove(info.color);
    document
      .getElementById("base-timer-path-remaining")
      .classList.add(warning.color);
  }
}

function calculateTimeFraction() {
  const rawTimeFraction = timeLft / TIME_LIMIT;
  return rawTimeFraction - (1 / TIME_LIMIT) * (1 - rawTimeFraction);
}

function setCircleDasharray() {
  const circleDasharray = `${(
    calculateTimeFraction() * FULL_DASH_ARRAY
  ).toFixed(0)} 283`;
  document
    .getElementById("base-timer-path-remaining")
    .setAttribute("stroke-dasharray", circleDasharray);
}


