
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
  console.log("List Appended");
}

function init_contents() {
  ajax_load_page("karmanode_load", "htm/karmanode-install.htm", "Install");
  //load_page("karmanode_load", "htm/karmanode-install.htm", "Install");
}

function ajax_load_page(element, path, tag) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', path, true);
  xhr.onreadystatechange = function() {
      if (this.readyState !== 4) return;
      if (this.status !== 200) return;
      //document.getElementById(element).innerHTML = this.responseText;
      appendList(element, this.responseTex);
      var nav = '<a href="#">' + tag + '</a>';
      appendList(element+'_nav', nav);
  };
  xhr.send();
}
