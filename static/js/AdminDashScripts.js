var checklist = document.getElementById("checklist");
var items = checklist.querySelectorAll("li");

for(var i=1; i<(items.length-1); i++) {
	items[i].addEventListener("click", onClick);
}

function onClick() {
	for(var i=1; i<(items.length-1); i++) {
	    items[i].className= "menu";
    }
	if(this.className == "menu") {
		this.className = "hidemenu";
	}
}
