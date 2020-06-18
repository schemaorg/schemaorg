<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Full Release Summary: Schema.org - {{requested_version}} - {{ releasedate }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />

    <base href="{{ base_href }}" ></base>
</head>
<body style="text-align: left;">

<div style="margin-left: 8%; margin-right: 8%">

{% include 'basicPageHeader.tpl' with context %}

<h1>Schema.org version {{ requested_version }}</h1>

<dl>

 <dt>Version:</dt>
 <dd>{{requested_version}}</dd>

 <dt>URL:</dt>
 <dd><a href="http://schema.org/version/{{requested_version}}/">http://schema.org/version/{{requested_version}}/</a></dd>

 <dt>Published:</dt>
 <dd>{{ releasedate }}</dd>

 <dt>Alternate formats: </dt>
  <dd>
     {% if requested_version != liveversion %}
     This release is also available in <a href="schema.rdfa">RDFa/RDFS</a>, <a href="schema.nt">N-Triples</a>
     {% endif %}

     {% if requested_version == liveversion %}
     This release, full core and extension definition files in N-Triples, Quads, JSON-LD, and Turtle formats, are also available for <a href="/docs/developers.html#defs">download</a>.
     {% endif %}
</dd>

<p>
<b>Overview:</b>
This is a <a href="/version/">full release</a> summary for schema.org. It describes in one document the terms (types, properties and enumerations) included in this version of schema.org.
The <a href="http://schema.org/">live site</a> offers various other page-by-page <a href="/docs/schemas.html">views</a> that include more information and examples.
Note that schema.org release numbers are not generally included when you <em>use</em> schema.org. In contexts (e.g. related standards work) when a particular
release needs to be cited, this document provides the appropriate URL.
</p>

<p>See the <a href="/docs/releases.html">releases page</a> for information about other schema.org releases.</p>

<p>
<b>Status:</b> this document represents a stable release of schema.org, and is automatically generated from the underlying canonical RDFS-based schema data. Although
the formal schema dataset associated with this release will not change, we may update the formatting (tracked as
<a href="https://github.com/schemaorg/schemaorg/issues/484">issue #484</a>), layout and other details of this document to
improve the presentation of this information. Similarly, the encoding and publication details (RDFa/RDFS etc.) for the machine-readable schema file may evolve; however the
data encoded should be considered canonical and frozen for each release. We solicit <a href="http://github.com/schemaorg/schemaorg/issues">advice</a> on data formats
that are useful for publishers and consumers of schema.org data.
</p>

<p>The structure of this document is simple: it provides an alphabetic list of types, and then <a href="#propaz">properties</a>, as they are defined in this version of schema.org.</p>

<h4>Type hierarchy</h4>

<div id="alltypes">
<small>
{{ thing_tree | safe }}
</small>
</div>

<h2>Types</h2>

{% for term in az_types %}

<div>
  <h4 id="term_{{term}}" name="term_{{term}}">{{term}}</a></h4>

<p>
  <div>{{ az_type_meta[term]['comment'] }} </div>

  <p>Properties used on this type: {{ az_type_meta[term]['props4type'] }} </p>
  <p>Properties whose values are of this type: {{ az_type_meta[term]['props2type'] }} </p>

  <small><a href="#intro">[^top]</a></small>
</p>

</div>

{% endfor %}


<h2>Properties</h2>


<p id="propaz">
<b>A-Z:</b>
<small>
{% for term in az_props %}
<a href="#term_{{term}}">{{term}}</a>
{% endfor %}
</small>
</p>

{% for term in az_props %}

  <h4 id="term_{{term}}" name="term_{{term}}">{{ term }}</a></h4>
  <p>
  <div>{{ az_prop_meta[term]['comment'] }} </div>
  <dl>
     <dt><b>Relevant types</b>:</dt>
     <dd> {{ az_prop_meta[term]['domainlist'] }}  </dd>
     <dt><b>Values</b>:</dt>
     <dd> {{ az_prop_meta[term]['rangelist'] }}  </dd>
 </dl>

  <small><a href="#intro">[^top]</a></small>
  </p>
{% endfor %}



<br/><br/>
</div>

