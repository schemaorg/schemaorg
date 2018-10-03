<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Schemas - schema.datacommons.org</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
</head>
<body>

{% include 'docsBasicPageHeader.tpl' with context %}


  <div id="mainContent" class="faq">


<h1>Organization of Schemas</h1>
The schemas are a set of 'types', each associated with a set of properties. The types are arranged in a hierarchy.<br/>
{{ counts | safe }}<br/>

<br />Browse the full hierarchy:
<ul>
  <li><a href="{{staticPath}}/DCThingy">One page per type</a></li>
  <li><a href="full.html">Full list of types, shown on one page</a></li>
</ul>
<br />

Or you can jump directly to a commonly used type:
<ul>
  <li>Things: <a href="{{staticPath}}/StatisticalPopulation">StatisticalPopulation</a> ...</li>
</ul>


</body>
</html>
