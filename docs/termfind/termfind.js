let termlist = [];
function loadSuggestions(){
    if(termlist.length == 0){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            termlist = this.responseText.split("\n");
        }
        };
        xhttp.open("GET", "/docs/termfind/termlist.txt", true); 
        xhttp.send();
    }
}
function suggest(value){
    //console.log(value);
    loadSuggestions();
    //console.log(termlist.length);
    if(value.length > 2){
        var matches = termslookup(value);
        displayMatches(matches,value);
        document.getElementById("suggestionwrap").classList.add("show");
    }else{
        document.getElementById("suggestionwrap").classList.remove("show");
        document.getElementById("suggestions").innerHTML = "";
    }
}

function selectmatch(row){
    var label = row.getElementsByClassName("matchlabel")[0].textContent;
    document.getElementById("termfind").value = "";
    window.location.href = "/" + label
}
function displayMatches(matches,value){
    let lookup = value.toLowerCase();
    var html = '<div class="matchtable">';
    for(let i=0;i<matches.length;i++){
        html += '<div class="matchrow" onclick="selectmatch(this)">'
        line = matchPrep(matches[i],lookup);
        html += line;
        html += '</div>';
    }
    html += '</div>';
    document.getElementById("suggestions").innerHTML = html;
}

function matchPrep(row,lookup){
    let len = lookup.length;
    parts = row.split(' ');
    label = parts[0];
    type = parts[1];
    index = label.toLowerCase().indexOf(lookup);
    var htmlrow = '<div class="matchlabel">';
    if(index > 0){
        htmlrow += label.substring(0,index);
    }
    htmlrow += '<span class="matchchars">';
    htmlrow += label.substring(index,index + len);
    htmlrow += '</span>';
    htmlrow += label.substring(index + len);
    htmlrow += '</div>';

    htmlrow += '<div class="matchtype">';
    switch(type){
        case "t":
            htmlrow += "Type";
            break;
            case "p":
            htmlrow += "Property";
            break;
            case "d":
            htmlrow += "Data Type";
            break;
            case "e":
            htmlrow += "Enumeration";
            break;
            case "v":
            htmlrow += "Enumeration Value";
            break;            
    }
    htmlrow += '</div>';
    
    return htmlrow;
}

function termslookup(lookupvalue){
    lookupvalue = lookupvalue.toLowerCase();
    //Get matches
    ret = termlist.filter(function(value){
        return value.toLowerCase().indexOf(lookupvalue) >= 0;
    });
    //Sort them
    ret.sort(function(s1, s2){
        var l=s1.toLowerCase(), m=s2.toLowerCase();
        return l===m?0:l>m?1:-1;
    });
    //Find startswith matches
    let pre = [];
    for(let i = 0; i < ret.length; i++){
        if(ret[i].toLowerCase().startsWith(lookupvalue)){
            pre.push(ret[i]);
        } 
    }
    // Pull them out of match list
    for(let i = 0;i<pre.length;i++){
        index = ret.indexOf(pre[i]);
        ret.splice(index,1);
    }
    // Put them at the beginning
    ret = pre.concat(ret);
    //console.log(ret);
    return ret;
}
