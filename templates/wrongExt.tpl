<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>- {{ sitename }}</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css">

</head>
<body>
	
{% include 'basicPageHeader.tpl' with context %}

  <div id="mainContent">
	<h1>Schema.org Extensions</h1>

	<p>
		The term '{{ target }}' is not in the schema.org core vocabulary, but is described by the following extension(s):
	</p> 
	<ul>
	{% for ext in extensions %}
		  <li><a href="{{ext['href']}}">{{ext['text']}}</a></li>
	{% endfor %}
	</ul>

  </div>

</body>
</html>
