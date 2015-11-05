<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>{{ entry }} - {{ sitename }}</title>
    <meta name="description" content="{{ desc }}" />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />
    <link href="/docs/prettify.css" type="text/css" rel="stylesheet" />
    <script type="text/javascript" src="/docs/prettify.js"></script>
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>

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

</head>
<body class="{{ sitemode }}">

{% include 'basicPageHeader.tpl' with context %}

  <div id="mainContent" vocab="http://schema.org/" typeof="{{ rdfs_type }}" resource="http://schema.org/{{ entry }}">
  {{ ext_mappings | safe }}



<!-- webapp will assemble the rest elsewhere -->

<!-- </div>
</body>
</html> -->
