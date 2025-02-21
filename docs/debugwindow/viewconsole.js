$(document).ready(function(){
     setTimeout(function(){

    var debugDiv = document.createElement('div');
    debugDiv.id = "DebugDiv";
    debugDiv.style.cssText = 'position:absolute;width:100%;height:500px;overflow:auto;z-index:100;text-align:left;color:yellow;background:#000;';
    document.body.appendChild(debugDiv);
    $('#DebugDiv').animate({
        scrollTop: $('#DebugDiv').get(0).scrollHeight
    }, 2000);
    window.DEBUG = {}
    let logger = document.getElementById("DebugDiv");
                
                // Adding log method from our console object
                window.DEBUG.log = text =>
                {
                    let element = document.createElement("div");
                    let txt = document.createTextNode(text);
                
                    element.appendChild(txt);
                    logger.appendChild(element);
                }
                window.DEBUG.log("Debug output:");
    }, 500);
});
