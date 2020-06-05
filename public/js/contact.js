
// Contact Form Submit
function contact_form_submit(el, e) {
  e.preventDefault();

  var XHR = new XMLHttpRequest();

  XHR.ontimeout = function () {
    return console.error("Contact Request - Request timed out.");
  };

  XHR.addEventListener("load", function (event) {
    console.log(event.currentTarget.responseText);
    if (XHR.status === 200) {
        json = JSON.parse(XHR.responseText);
        if (json.status == true) {
          if (json.response == false) {
            error_message.style = "display: block;";
            success_message.style = "display: none;";
            error_message_div.innerHTML = json.message;
          } else {
            success_message.style = "display: block;";
            error_message.style = "display: none;";
          }
        } else {
          error_message.style = "display: block;";
          success_message.style = "display: none;";
        }
        fadeOut(document.getElementById('contact_form_container'), 1, 0);
    } else {
        console.error("Contact Request - No Response");
        error_message.style = "display: block;";
        success_message.style = "display: none;";
        error_message_div.innerHTML = "An Internal Error has Occurred.";
    }
  });

  var x = new FormData(el);
  var c = x.entries();
  c.hasNext = function hasNext() {
    const r = this.next();
    this.current = r.value;
    return !r.done;
  };
  var count = 0;
  while (c.hasNext()) {
    count++;
  }

  var entries = x.entries();
  var params = "";
  var jsonObject = {};
  entries.hasNext = function hasNext() {
    const r = this.next();
    this.current = r.value;
    return !r.done;
  };
  while (entries.hasNext()) {
    params += entries.current[0] + '='+ entries.current[1];
    count--;
    if (count > 0) {
        params += "&";
    }
    jsonObject[entries.current[0]] = entries.current[1];
  }

  XHR.addEventListener("error", function (event) {
    console.error(event);
  });

  //XHR.open("POST", window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/contact_submit");
  XHR.open("POST", window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/api/contact_submit");

  XHR.timeout = 7300;
  XHR.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

  XHR.send(JSON.stringify(jsonObject));
}

var clickskip = false;

function fadeOut(obj, from, to) {
  var box = obj;
  if (clickskip == true) {
    box.style.opacity = to;
    box.style = "display: none;";
    return;
  }
  if (from <= to) {
    box.style.opacity = to;
    box.style = "display: none;";
    return;
  } else {
    box.style.opacity = from;
    setTimeout(function() {
      fadeIn(obj, from - 0.02, to);
    }, 37)
  }
}

function fadeIn(obj, from, to) {
  var box = obj;
  if (clickskip == true) {
    box.style.opacity = to;
    //box.style = "display: block;";
    return;
  }
  if (from >= to) {
    box.style.opacity = to;
    return;
  } else {
    box.style.opacity = from;
    setTimeout(function() {
      fadeIn(obj, from + 0.02, to);
    }, 35)
  }
}
