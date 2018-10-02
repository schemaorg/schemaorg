<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Home - {{ sitename }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css">
</head>
<body>
{% include 'basicPageHeader.tpl' with context %}

  <div id="mainContent">



  <h1>Welcome to {{ sitename }}</h1>


<p>
    Schema.datacommons.org is a collaborative, community activity with a mission to create,
    maintain, and promote Blah blah blah....
</p>

<br/>
</div>



<div id="footer"><p>
  <a href="docs/terms.html">Terms and conditions</a></p>
</div>

<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-52672119-1', 'auto');
  ga('send', 'pageview');

</script>



<p><br/></p>

</body>
</html>
