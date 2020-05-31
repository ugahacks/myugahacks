

// Modal Image Gallery
function onClick(element) {
  document.getElementById("img01").src = element.src;
  document.getElementById("modal01").style.display = "block";
  var captionText = document.getElementById("caption");
  captionText.innerHTML = element.alt;
}

// Change style of navbar on scroll
window.onscroll = function() {myFunction()};
function myFunction() {
    var navbar = document.getElementById("myNavbar");

    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        navbar.className = "w3-bar" + " w3-card" + " w3-animate-top" + " uga-red";
    } else {
        navbar.className = navbar.className.replace(" w3-card w3-animate-top uga-red", "");
    }
}

// Used to toggle the menu on small screens when clicking on the menu button
function toggleFunction() {
    var x = document.getElementById("navDemo");
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else {
        x.className = x.className.replace(" w3-show", "");
    }
}

//Used to change navbar to red if there is no scrolling on the page.
window.onload = function() {
  var navbar = document.getElementById("myNavbar");
  var scroll = document.getElementById("noScroll");
  scroll = scroll == null;
  if(!scroll) {
      navbar.className = "w3-bar" + " w3-card" + " uga-red";
  }
}
