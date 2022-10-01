      $(document).ready(function(){
        prettyPrint();
        setTimeout(function(){

  $(".atn:contains(itemscope), .atn:contains(itemtype), .atn:contains(itemprop), .atn:contains(itemid), .atn:contains(time), .atn:contains(datetime), .atn:contains(datetime), .tag:contains(time) ").addClass('new');
  $('.new + .pun + .atv').addClass('curl');
  window.structured = [];
  $('.ds-tab.structure').on('loadstructuredview', async function(){
    var $this = $(this);
    $key = $this.data('ex');
    if(window.structured.indexOf($key) == -1) {
        window.structured.push($key);

        $jdata = $('.payload.' + $key).html();
 
        const html1 = await prettyMarkupHtml($jdata);

        $('.structureout.' + $key).html( html1);

        var val = await prettyMarkupText($jdata);
        $('.structuretext.' + $key).html(val);
        

    }
});
  }, 500);
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
  }, 500);
  setTimeout(function(){

  $(".atn:contains(property), .atn:contains(typeof) ").addClass('new');
  $('.new + .pun + .atv').addClass('curl');

        }, 500);
        setTimeout(function() {
          $('.ds-selector-tabs .selectors a').click(function() {
            var $this = $(this);
            var $p = $this.parents('.ds-selector-tabs');
            $('.selected', $p).removeClass('selected');
            $this.addClass('selected');
            $('.ds-tab.' + $this.data('selects'), $p).addClass('selected').trigger('loadstructuredview');
            
          });
        }, 0);
        clip = new ClipboardJS('.clip');
        clip.on('success', function(e) {
            $but = e.trigger.className;
            $targ = $but.split(" ").pop();
            var targsel = '.tooltiptext.' + $targ;

            var tip = $(targsel);
            tip.text('Copied!');
            tip.addClass('show');
            e.clearSelection();
            setTimeout(function() {
                tip.removeClass('show');
            }, 2500);
            });
    
        clip.on('error', function(e) {
            var tip = $('.tooltip .tooltiptext');
            tip.text(fallbackMessage('copy'));
            tip.addClass('show');
        });
        $('.tooltip .tooltiptext').mouseleave(function(){
            $(this).removeClass('show');
        });

    });

    function jumpmenuopen(){
      $('#jumpmenu').removeClass('jumpclosed');
      $('#jumpmenu').addClass('jumpopen');
    }
    function jumpmenuclose(){
      $('#jumpmenu').removeClass('jumpopen');
      $('#jumpmenu').addClass('jumpclosed');
    }

