<!DOCTYPE html>
<html lang="en">
<!-- Generated from genericTermPageHeader.tpl -->
<head>
  {% include 'headtags.tpl' with context %}
	{% if noindexpage %}<meta name="robots" content="noindex">{% endif %}
    <title>{{ entry }} - {{ sitename }} {{ titletype}}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{{ desc }}" />


<script type="text/javascript">
      $(document).ready(function(){
        prettyPrint();
        setTimeout(function(){

  $(".atn:contains(itemscope), .atn:contains(itemtype), .atn:contains(itemprop), .atn:contains(itemid), .atn:contains(time), .atn:contains(datetime), .atn:contains(datetime), .tag:contains(time) ").addClass('new');
  $('.new + .pun + .atv').addClass('curl');

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
            $('pre.' + $this.data('selects'), $p).addClass('selected');
          });
        }, 0);
      });
</script>

<style>

  .pln    { color: #444;    } /* plain text                 */
  .tag    { color: #515484; } /* div, span, a, etc          */
  .atn,
  .atv    { color: #314B17; } /* href, datetime             */
  .new    { color: #660003; } /* itemscope, itemtype, etc,. */
  .curl   { color: #080;    } /* new url                    */

  table.definition-table {
    border-spacing: 3px;
    border-collapse: separate;
  }
  
  #morecheck {
	  outline: none;
  }
#morecheck:checked + div { display: none; }
  

</style>
<link rel="canonical" href="https://schema.org/{{ entry }}" />
</head>
<body class="{{ sitemode }}">

{% include 'basicPageHeader.tpl' with context %}
  <div id="mainContent" vocab="{{ vocabUri }}" typeof="{{ rdfs_type }}" resource="{{ vocabUri }}{{ entry }}">
  {{ ext_mappings | safe }}

<!-- webapp will assemble the rest elsewhere -->
<!-- Will need at least:  </div></body></html> -->
<!-- end of genericTermPageHeader.tpl -->
  

