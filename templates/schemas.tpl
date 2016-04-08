<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Schemas - schema.org</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />
</head>
<body>

{% include 'basicPageHeader.tpl' with context %}


  <div id="mainContent" class="faq">


<h1>Organization of Schemas</h1>
The schemas are a set of 'types', each associated with a set of properties. The types are arranged in a hierarchy.<br/>
{{ counts | safe }}<br/>

<br />Browse the full hierarchy:
<ul>
  <li><a href="{{staticPath}}/Thing">One page per type</a></li>
  <li><a href="full.html">Full list of types, shown on one page</a></li>
</ul>
<br />

Or you can jump directly to a commonly used type:
<ul>
  <li>Creative works: <a href="{{staticPath}}/CreativeWork">CreativeWork</a>, <a href="{{staticPath}}/Book">Book</a>, <a href="{{staticPath}}/Movie">Movie</a>, <a href="{{staticPath}}/MusicRecording">MusicRecording</a>, <a href="{{staticPath}}/Recipe">Recipe</a>, <a href="{{staticPath}}/TVSeries">TVSeries</a> ...</li>
  <li>Embedded non-text objects: <a href="{{staticPath}}/AudioObject">AudioObject</a>, <a href="{{staticPath}}/ImageObject">ImageObject</a>, <a href="{{staticPath}}/VideoObject">VideoObject</a></li>
  <li><a href="{{staticPath}}/Event">Event</a></li>
  <li><a href="{{staticPath}}/docs/meddocs.html">Health and medical types</a>: notes on the health and medical types under <a href="{{staticPath}}/MedicalEntity">MedicalEntity</a>.</li>
  <li><a href="{{staticPath}}/Organization">Organization</a></li>
  <li><a href="{{staticPath}}/Person">Person</a></li>
  <li><a href="{{staticPath}}/Place">Place</a>, <a href="{{staticPath}}/LocalBusiness">LocalBusiness</a>, <a href="{{staticPath}}/Restaurant">Restaurant</a> ...</li>
  <li><a href="{{staticPath}}/Product">Product</a>, <a href="{{staticPath}}/Offer">Offer</a>, <a href="{{staticPath}}/AggregateOffer">AggregateOffer</a></li>
  <li><a href="{{staticPath}}/Review">Review</a>, <a href="../AggregateRating">AggregateRating</a></li>
  <li><a href="{{staticPath}}/Action">Action</a></li>
</ul>

<br/>Using the <a href="{{staticPath}}/docs/extension.html">extension mechanism</a> the core vocabulary is extended by the following hosted extensions:
<ul>
{% for ext in extensions %}
	<li>{{ ext | safe }}</li>
{% endfor %}
</ul>

<br/>See also the <a href="{{staticPath}}/docs/releases.html">releases</a> page for recent updates and project history.<br/>

<br />
We also have a small set of <a href="{{staticPath}}/DataType">primitive data types</a> for numbers, text, etc. More details about the data model, etc. are available <a href="{{staticPath}}/datamodel.html">here</a>.
<br />
<br />


  </div>


<div id="footer"><p>
  <a href="../docs/terms.html">Terms and conditions</a></p>
</div>

</body>
</html>
