var myInput = document.getElementById("pswd");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");

// When the user clicks on the password field, show the message box
myInput.onfocus = displayerror;

// When the user clicks outside of the password field, hide the message box


// When the user starts to type something inside the password field
myInput.onkeyup = function() {
   var upperCaseLetters = /[A-Z]/g;
   var numbers = /[0-9]/g;
   var lowerCaseLetters = /[a-z]/g;

   err(upperCaseLetters);
   err(lowerCaseLetters);
   err(numbers);

  function err (constraints) {
      if(myInput.value.match(constraints)) 
      {  
        capital.classList.remove("invalid");
        capital.classList.add("valid");
      } 
      else {
        capital.classList.remove("valid");
        capital.classList.add("invalid");
      }
  }

  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } 
  else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
  
}