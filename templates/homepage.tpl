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


{% import 'ext.tpl' as ext with context %}

{% if mybasehost in [ "sdo-deimos.appspot.com", "sdo-phobos.appspot.com", "sdo-ganymede.appspot.com", "sdo-gozer.appspot.com", "sdo-callisto.appspot.com", "webschemas.org", "sdo-scripts.appspot.com", "localhost" ] %}

<!--<p id="lli" class="layerinfo">
Note: This is {{ mybasehost }}. you are viewing an unstable work-in-progress preview of <a href="http://schema.org/">schema.org</a>.
See the draft <b><a href="{{staticPath}}/docs/releases.html">releases</a></b> page to learn more about this version ({{ SCHEMA_VERSION }}).
</p>-->

{% endif %}


{% if ENABLE_HOSTED_EXTENSIONS and extComment != "" %}
  {{ ext.overview() }}

<p>
  {{extComment |safe}}
</p>

{% elif ENABLE_HOSTED_EXTENSIONS and host_ext == "test001" %}
  {{ ext.overview(name="Test Extension", abbrev="test1") }}

  <p>This is purely here for testing, please ignore.</p>

  <p><br/></p>

{% else %}


  <h1>Welcome to Schema.org</h1>


<p>
    Schema.org is a collaborative, community activity with a mission to create,
    maintain, and promote schemas for structured data on the
    Internet, on web pages, in email messages, and beyond.
</p>

<p>
    Schema.org vocabulary can be used with many different encodings,
    including RDFa, Microdata and JSON-LD. These vocabularies cover
    entities, relationships between entities and actions, and can
    easily be extended through a well-documented extension model. Over 10 million sites use
    Schema.org to markup their web pages and email messages.
    Many applications from Google, Microsoft, Pinterest, Yandex and others
    already use these vocabularies to power rich, extensible experiences.
</p>
<p>
    Founded by Google, Microsoft, Yahoo and Yandex,
    Schema.org vocabularies are developed by an open <a href="https://www.w3.org/community/schemaorg">community</a> process,
    using the <a
    href="http://lists.w3.org/Archives/Public/public-schemaorg">public-schemaorg@w3.org</a>
     mailing list and through <a href="http://github.com/schemaorg/schemaorg">GitHub</a>.
</p>

<p>
   A shared vocabulary makes it easier for webmasters and developers to decide
   on a schema and get the maximum benefit for their efforts.
   It is in this spirit that the founders, together with the
   larger community have come together - to provide a shared collection of schemas.
 </p>

<p>
    We invite you to <a href="docs/gs.html">get started</a>!
</p>
<p>
    View our blog at <a href="http://blog.schema.org">blog.schema.org</a> or see <a href="/docs/releases.html">release history</a> for version {{ SCHEMA_VERSION }}.
</p>

<br/>
</div>


{% endif %}

{{ ext_contents | safe }}

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

{{ ext.debugInfo() | safe }}

</body>
</html>
