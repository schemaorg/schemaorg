<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Home - {{ sitename }}</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css">

</head>
<body>

{% include 'basicPageHeader.tpl' with context %}

  <div id="mainContent">


{% import 'ext.tpl' as ext with context %}

{% if myhost in [ "sdo-phobos.appspot.com", "sdo-ganymede.appspot.com", "sdo-gozer.appspot.com", "sdo-tully.appspot.com", "sdo-lenny.appspot.com", "webschemas.org", "sdo-scripts.appspot.com", "localhost" ] %}

<p id="lli" class="layerinfo">
Note: This is {{ myhost }}. you are viewing an unstable work-in-progress preview of <a href="http://schema.org/">schema.org</a>.
See the draft <b><a href="{{staticPath}}/docs/releases.html">releases</a></b> page to learn more about this version.
</p>

{% endif %}


{% if ENABLE_HOSTED_EXTENSIONS and host_ext == "bib" %}
  {{ ext.overview(name="Bibliographic Extension", abbrev="bib") }}
  <p>
  You are viewing the Bibliographic Extension within <a href="http://schema.org/">schema.org</a>.
  It defines terms such as <a href="/Audiobook">Audiobook</a>, <a href="/Thesis">Thesis</a>, <a href="/ComicStory">ComicStory</a>, and  <a href="/workTranslation">workTranslation</a>.
   For more details see the W3C BibExtend Community Group's <a href="http://www.w3.org/community/schemabibex/wiki/Bib.schema.org-1.0">wiki</a>.
  <br/>This should be considered a pre-final preview release; final changes may be made after wider <a href="https://github.com/schemaorg/schemaorg/issues/699">community review</a>.
  </p>

{% elif ENABLE_HOSTED_EXTENSIONS and host_ext == "auto" %}
  {{ ext.overview(name="Auto Extension", abbrev="auto") }}

  <p>  You are viewing the Auto Extension within <a href="http://schema.org/">schema.org</a>.
  It defines terms such as <a href="/MotorizedBicycle">MotorizedBicycle</a> and adds terms to <a href="/Car">Car</a>. For more details
  see the W3C <a href="https://www.w3.org/community/gao/">Automotive Ontology Working Group</a>.
  <br/>This should be considered a pre-final preview release; final changes may be made after wider <a href="https://github.com/schemaorg/schemaorg/issues/704">community review</a>.
</p>

  <p><br/></p>

{% elif ENABLE_HOSTED_EXTENSIONS and host_ext == "fibo" %}
  {{ ext.overview(name="FIBO Extension", abbrev="fibo") }}

  <p>  You are viewing the FIBO Extension within <a href="http://schema.org/">schema.org</a>.
  It defines terms such as <a href="/FinancialProduct">FinancialProduct</a> and adds terms to <a href="/BankOrCreditUnion">BankOrCreditUnion</a>. For more details
  see the W3C <a href="">FIBO ????? Working Group</a>.
  <br/>This should be considered a preview release; final changes may be made after wider <a href="">community review</a>.
</p>

  <p><br/></p>

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
    Schema.org is sponsored by Google, Microsoft, Yahoo and Yandex.
    The vocabularies are developed by an open <a href="https://www.w3.org/community/schemaorg">community</a> process,
    using the <a
    href="http://lists.w3.org/Archives/Public/public-schemaorg">public-schemaorg@w3.org</a>
     mailing list and through <a href="http://github.com/schemaorg/schemaorg">GitHub</a>.
</p>

<p>
   A shared vocabulary makes it easier for webmasters and developers to decide
   on a schema and get the maximum benefit for their efforts.
   It is in this spirit that the sponsors, together with the
   larger community have come together, to provide a shared collection of schemas.
 </p>

<p>
    We invite you to <a href="docs/gs.html">get started</a>!
</p>
<p>
    View our blog at <a href="http://blog.schema.org">blog.schema.org</a> or see <a href="/docs/releases.html">release history</a>.
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

{{ ext.debugInfo() }}

</body>
</html>
