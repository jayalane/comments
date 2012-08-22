function reload_html(node, url, run_cb, filter_cb, class_name) {
    
    var req;  // Http request
    var new_node; 
    if (window.XMLHttpRequest) { // Non-IE browsers
        req = new XMLHttpRequest();
    } else if (window.ActiveXObject) { // IE
        req = new ActiveXObject("Microsoft.XMLHTTP");  
    }
    req.onreadystatechange = function () {
        if (req.readyState == 4) { // complete
            if (req.status == 200) { // OK
                new_node = get_or_make_child_node(node, class_name);
		if (filter_cb) {
                    new_node.innerHTML = filter_cb(req.responseText);
		} else {
                    new_node.innerHTML = req.responseText;
		}
            } else {
                new_node = get_or_make_child_node(node,class_name);
                new_node.innerHTML = req.statusText;
            }
            if (run_cb != null) {
                run_cb()
            }
        } else {
            new_node = get_or_make_child_node(node,class_name);
            if (new_node.innerHTML == "") {
                new_node.innerHTML = "Loading..."
            }
        }
    }
    try {  
        req.open("GET", url, true)
    } catch (e) {
        new_node = get_or_make_child_node(node);
        new_node.innerHTML = e; 
    }
    req.send(null); 
}

function get_or_make_child_node (node,class_name) {
    var ary = node.childNodes;
    var new_node;
    for (var i=0; i < ary.length;i++) {
        if (ary[i].nodeType == 1) {
            if (ary[i].className == class_name) {
            return ary[i];
            }
        }
    }
    if (node.className == class_name) {
        return node; // this allows me to be confused about the element
 
    }
    new_node = document.createElement('div');
    new_node.className = class_name;
    node.appendChild(new_node);
    return new_node;
}

function get_child_class (node, class_name) {
    var ary = node.childNodes;
    if (ary == null) {
        return null;
    }
    for (var i=0; i < ary.length;i++) {
        if (ary[i].nodeType == 1) {
            if (ary[i].className.valueOf() == class_name.valueOf()) {
                return ary[i];
            }
        }
    }
    return null;
}

function get_elements_by_class(node,searchClass,tag) {
    var classElements = new Array();
    var els = node.getElementsByTagName(tag);
    var elsLen = els.length;
    var pattern = new RegExp("\b"+searchClass+"\b");
    for (i = 0, j = 0; i < elsLen; i++) {
        if ( pattern.test(els[i].className) ) {
            classElements[j] = els[i];
            j++;
            alert("Got one!" + j + " " + els[i].className);
        }
    }
    return classElements;
}

function toggle_visible(the_node) {
    var node   = get_child_class(the_node, "hidable");
    var node_o = get_child_class(the_node, "hide-open");
    var node_c = get_child_class(the_node, "hide-closed");
    if (node == null) {
        return;
    }
    if (node.style.display == 'none') {
        node.style.display = '';
        // now open the click to hide
        node_o.style.display ='';
        node_c.style.display='none';
    } else {
        node.style.display = 'none';
        // now open the click to hide
        node_o.style.display ='none';
        node_c.style.display='';
    }
    return;
}


function cancel_click(e) {
    if (window.event) {
        window.event.cancelBubble = true;
        window.event.returnValue = false;
    }
    if (e && e.stopPropagation && e.preventDefault){
        e.stopPropagation();
        e.preventDefault();
    }
}

function add_event (elm, evType, fn, useCapture) {
    if (elm.addEventListener){
        elm.addEventListener(evType, fn, useCapture);
        return true;
    } else if (elm.attachEvent) {
        var r = elm.attachEvent('on' + evType, fn);
        return r;
    } else {
        elm['on' + evType] = fn;
    }
}

function standard_init(class_name, cb) {
    var ary = document.getElementsByTagName('div');
    if (ary == null) {
        return;
    }
    for (i = 0; i < ary.length; i++) {
        var el = ary[i];
        if (el.nodeType != 1) {
            continue;
        }
        if (el.className == class_name) {
            cb(el);
        }
    }
}
