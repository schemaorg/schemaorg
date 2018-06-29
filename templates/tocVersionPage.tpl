<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Schema.org - Full Releases</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <basxe href="{{ base_href }}" ></base>
</head>
<body style="text-align: left;">

{% include 'basicPageHeader.tpl' with context %}

<div style="margin-left: 8%; margin-right: 8%">

<h1>Schema.org versions</h1>

<p>See the <a href="/docs/releases.html">releases page</a> for a longer and more detailed history of schema.org releases.</p>

<p>The following snapshot(s) of schema.org releases are available:</p>

<ul>
{% for release in releases %}
  <li><a href="/version/{{release}}/">{{release}}</a></li>
{% endfor %}
</ul>

<p>Note that these snapshots currently contain only the schema.org core vocabulary. Information about <a href="/docs/extension.html">extensions</a> and older releases may be added later.</p>


<br/><br/>
</div>
