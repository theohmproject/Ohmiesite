
var contentsLoaded = false;

window.addEventListener('scroll', function() {
  element = document.getElementById("content");
  var a = element.scrollTop;
  var b = element.scrollHeight - element.clientHeight;
  var c = a / b;
  if (c > 0.2 && contentsLoaded == false) {
    init_contents();
    contentsLoaded = true;
  }
});

// Load html page into div element..
function load_page(element, path, tag) {
    var html = '<object type="text/html" data="' + path + '" ></object>';
    appendList(element, html);
    var nav = '<a href="#">' + tag + '</a>';
    appendList(element+'_nav', nav);
}

function appendList(list, item) {
  var ul = document.getElementById(list);
  var li = document.createElement("li");
  li.innerHTML = item;
  ul.appendChild(li);
}

function init_contents() {
  console.log("Load More Page..");
  ajax_load_page("karmanode_load", "/htm/karmanode-install.htm", "Install");
  //load_page("karmanode_load", "htm/karmanode-install.htm", "Install");
}

function ajax_load_page(element, path, tag) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', path, true);
  xhr.onreadystatechange = function() {
      if (this.readyState !== 4) return;
      if (this.status !== 200) return;
      //document.getElementById(element).innerHTML = this.responseText;
      appendList(element, this.responseText);
      var nav = '<a href="#">' + tag + '</a>';
      appendList(element+'_nav', nav);
  };
  xhr.send();
}
