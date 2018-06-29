<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Schemas - schema.org</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
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

<br/>See also the <a href="{{staticPath}}/docs/releases.html">releases</a> page for recent updates and project history.<br/>

<br />
We also have a small set of <a href="{{staticPath}}/DataType">primitive data types</a> for numbers, text, etc. More details about the data model, etc. are available <a href="{{staticPath}}/docs/datamodel.html">here</a>.
<br />

 <h2 id="ext">Extensions</h2>

 <p>As schema.org has grown, we have developed mechanisms for <a href="/docs/extension.html">community extension</a> as a way of adding more detailed descriptive vocabulary that builds on the schema.org core.</p>

 <p><b>Hosted</b> extensions are managed and published as part of the schema.org project, with their design often led by one of more dedicated community groups.</p>

 <p><b>External</b> extensions live elsewhere in the Web, typically managed by other organizations with their own processes and collaboration mechanisms.
   Please consult external documentation for full details of their vocabulary, versioning system and release history.</p>

 <h3 id="hosted">Hosted Extensions</h3>

<p>
Specialized terms from hosted extensions can be used alongside core schema.org terms like <a href="/Event">Event</a> and <a href="/Person">Person</a>.
For example in the <a href="http://auto.schema.org/">auto</a> extension there is a property for <a href="/emissionsCO2">emissionsCO2</a>,
and in the <a href="http://bib.schema.org/">bibliographic extension</a> we have a property <a href="/publisherImprint">publisherImprint</a>.
</p>

<p>Using the <a href="{{staticPath}}/docs/extension.html">extension mechanism</a> the core vocabulary is extended by the following hosted extensions:</p>
<ul>
{% for ext in extensions %}
	<li>{{ ext | safe }}</li>
{% endfor %}
</ul>


<p><b>Note</b>: the 'pending' and 'meta' hosted extensions are part of schema.org's schema development process.</p>
<p id="ext_pending">
  We use the 'pending' extension as a staging area for new schema.org terms that are under discussion and review.
  Implementors and publishers are cautioned that terms in the <a href="http://pending.schema.org">pending</a> extension
  may lack consensus and that terminology and definitions could still change significantly after community and <a href="/docs/about.html#cgsg">steering group</a> review.
  Consumers of schema.org data who encourage use of such terms are <em>strongly encouraged</em>
  to update implementations and documentation to track any evolving changes, and to share early implementation feedback with the <a href="http://www.w3.org/community/schemaorg">wider community</a>.
</p>

<p id="ext_meta">
The 'meta' extension is primarily for vocabulary used internally within schema.org to support technical definitions and
schema.org site functionality. These terms are not intended for general usage in the public Web.
</p>
<p id="attic"><strong>Attic</strong> ({{attic | safe}}) is a special extension area where terms are archived when deprecated from the core and other extensions, or removed from <a href="http://pending.schema.org">pending</a> as not accepted into the full vocabulary. References to terms in the attic area are not normally displayed unless accessed via the term identifier or via the {{attic | safe}} home page. Implementors and data publishers are cautioned not to use terms in the attic area.
</p> 

<p>
Unlike other core and extension terms, these extensions may be updated at any time without the need for a full <a href="/docs/releases.html">release</a>.
</p>

<h3 id="extext">External Extensions</h3>

<p>The schema.org <a href="/docs/about.html#cgsg">steering group</a> does not officially approve external extensions - they are fully independent.
  We list here some notable extensions that extend schema.org in interesting and useful ways.</p>

<ul>
  <li><a href="http://gs1.org/voc/">GS1 Web Vocabulary</a> (<a href="http://blog.schema.org/2016/02/gs1-milestone-first-schemaorg-external.html">blog post</a>)</li>
</ul>
<br/><br/><br/>
  </div>


<div id="footer"><p>
  <a href="../docs/terms.html">Terms and conditions</a></p>
</div>

</body>
</html>
