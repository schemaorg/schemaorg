<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>- {{ sitename }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css">

</head>
<body>
	
{% include 'basicPageHeader.tpl' with context %}

  <div id="mainContent">
	<h1>Schema.org Extensions</h1>

	<p>
		The term '{{ target }}' is not in the schema.org core vocabulary, but is defined in an <a href="/docs/extension.html">extension</a>:
	</p> 
	<ul>
	{% for ext in extensions %}
		  <li><a href="{{ext['href']}}">{{ext['text']}}: {{ target }}</a></li>
	{% endfor %}
	</ul>

        <p><strong>Note:</strong> extension terms can be used in schema.org markup in the normal manner; it is not necessary for markup publishers to indicate which extension  a term is currently in. Terms may move between extensions over time (e.g. from <a href="http://pending.schema.org/">pending</a> to the core) without the need for the corresponding markup to change.
        </p>
        <br/>

  </div>

</body>
</html>
