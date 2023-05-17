$(document).ready(function(){
    setTimeout(function(){
        const targets = Array.from(document.getElementsByClassName("jumptarget"));
        const selectors = document.getElementById("jumpselections");
        for (let i = 0; i < targets.length; i++) {
          let target = targets[i];
          targetId = target.getAttribute('id');
          targetTitle = target.getAttribute('title');
          const el = document.createElement('a');
          el.textContent = targetTitle;
          el.setAttribute('title',targetTitle);
          el.setAttribute('href',"#"+targetId);
          el.className  = "jumpselector";
          selectors.appendChild(el);
        }
        
      }, 500);
      setTimeout(function(){
        $('#jumphead').click(function() {
          console.log("Head Clicked\n");
          if($('#jumpmenu').hasClass('jumpclosed')){
            console.log('closed\n');
            jumpmenuopen();
          } else {
            console.log('open\n');
            jumpmenuclose();
          }
        });
        $('.jumpselector').click(jumpmenuclose);
      }, 500);   })    


function jumpmenuopen(){
    $('#jumpmenu').removeClass('jumpclosed');
    $('#jumpmenu').addClass('jumpopen');
  }
function jumpmenuclose(){
    $('#jumpmenu').removeClass('jumpopen');
    $('#jumpmenu').addClass('jumpclosed');
  }
