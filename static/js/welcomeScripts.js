var checklist = document.getElementById("checklist");
var items = checklist.querySelectorAll("li");

for(var i=0; i<items.length; i++) {
	items[i].addEventListener("click", onClicking);
}

function onClicking() {
	if(this == items[2]){
		if(items[3].className != "hidemenu"){
			items[0].className = "menu";
			this.className = "hidemenu";
		}
	}
	else if(this == items[3]){
		if(items[2].className != "hidemenu"){
			items[0].className = "menu";
			this.className = "hidemenu";
		}
	}
}

function openAboutForm() {
  if(items[3].className != "hidemenu" ) {
  	document.getElementById("aboutForm").style.display = "block";
  }
}


function openContactForm() {
  if(items[2].className != "hidemenu") {
  	document.getElementById("contactForm").style.display = "block";
  }
}

function closeAboutForm() {
 	document.getElementById("aboutForm").style.display = "none";
 	for(var i=0; i<items.length; i++) {
	    items[i].className= "menu";
    }
    items[0].className= "hidemenu";
}

function closeContactForm() {
 	document.getElementById("contactForm").style.display = "none";
 	for(var i=0; i<items.length; i++) {
	    items[i].className= "menu";
    }
    items[0].className= "hidemenu";
}