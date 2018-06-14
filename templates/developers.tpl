<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Schemas - schema.org</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
</head>
<body onload="updatetext()">

{% include 'basicPageHeader.tpl' with context %}


  <div id="mainContent" class="faq">


<h2>Schema.org for Developers</h2>

<p>
This is a placeholder page for developer-oriented information about schema.org. In particular it gives access to machine-readable representations of our schemas.
</p>


<h2 id="conneg">Machine Readable Term Definitions</h2>

<p>Machine-readable definitions of individual terms are availble as RDFa, embeded into the term page html. It is also available in other formats by accessing term URLs, using the <a href="https://www.w3.org/TR/swbp-vocab-pub/#negotiation">Linked Data Content Negotiation</a> technique of providing the required type in an HTTP Accept header value.  The same content is also available by providing an appropriate suffix to the term URL.  For example the Triples definition for the <a href="{{staticPath}}/Book">Book</a> Type can bet retrieved with the following URL <a href="{{staticPath}}/Book.nt">{{staticPath}}/Book.nt</a>.</p>
<p>The currently supported format types, relevant Accept values, and url suffixes are:</p>
	<ul><li>JSON-LD - application/ld+json - .jsonld</li>
		<li>RDF/XML - application/rdf+xml - .rdf</li>
		<li>Triples - text/plain - .nt</li>
		<li>Turtle - application/x-turtle - .ttl</li>
		<li>CSV - text/csv - .csv</li></ul>

<p><strong>Note:</strong> This is currently an experimental feature</p>

<h2 id="defs">Vocabulary Definition Files</h2>

<p>To assist developers, files containing the definition of the core Schema.org vocabulary and its extensions are available for download in common RDF formats.</p>

<p>Older releases can be found (under data/releases/) at <a href="https://github.com/schemaorg/schemaorg">GitHub</a>.

<p>Select the file and format required and click Download.  The CSV format downloads are split accross two files: <em>Types</em> includes definitions of Types and Enumeration Values, including lists of associated properties; <em>Properties</em> contains property definitions.<br/>
<br/><strong>Note:</strong> File <em>schema</em> contains the definition of the core vocabulary; <em>bib</em> contains only the definitions for the bib.schema.org extension; <em>all-layers</em> contains definitions for the core plus all the extensions.</p>


	<table style="padding: 2px; width:600px">
	<tr><td style="width: 30%;">
			File: <select id="filename"  onchange="updatetext()">
				<option value="{{staticPath}}/version/latest/schema">schema</option>
				<option value="{{staticPath}}/version/latest/all-layers">all-layers</option>
				{% for ext in extensions %}
					<option value="{{staticPath}}/version/latest/ext-{{ ext | safe }}">{{ ext | safe }}</option>
				{% endfor %}
			</select>
	</td>
	<td style="width: 30%;">
		Format:  <select id="fileext" onchange="updatetext()">
				<option value=".nt">Triples</option>
				<option value=".nq">Quads</option>
				<option value=".jsonld">JSON-LD</option>
				<option value=".rdf">RDF/XML</option>
				<option value=".ttl">Turtle</option>
				<option value=".csv">CSV</option>
		</select>
	</td>
	<td style="width: 30%;">
		<div id ="csvsel">
			For: <select id="csvfmt" onchange="updatetext()">
				<option value="-types">Types</option>
				<option value="-properties">Properties</option>
				<!-- <option value="-enumvalues">Enumeration Values</option> -->
			</select>
		</div>
	</td>
	</tr>
	<tr><td colspan="3">
		<div id="label"></div>
	<tr><td colspan="3" style="text-align: center;">
		<input type="button" onclick="dowloadfunc();" value="Download"/>
	</td></tr>

	</table>
    <h3 style="margin-left: 50px;" id="experiments">Experimental/Unsupported</h3>

   <p>The following representations are <em>experimental</em> and may change or be removed in future releases.</p>

   <h4 id="d3rdfs">D3 RDFS in JSON-LD</h4>

   <p>
    A simplification of the Schema.org type hierarchy, in which each type has at most one super-type, represented
    in a hybrid format that combines JSON-LD, <a href="https://en.wikipedia.org/wiki/RDF_Schema">RDFS</a> and <a href="https://d3js.org/">D3</a>: <a href="{{staticPath}}/docs/tree.jsonld">tree.jsonld</a>.
  </p>
  <p>
    This file is made available to support developers using the <a href="https://d3js.org/">D3</a> JavaScript library for manipulating documents based on data.
    It uses JSON-LD to declare that D3's default "children" JSON field represents "subClassOf" relationships, but expressed in the
    reverse direction (<a href="https://bl.ocks.org/danbri/1c121ea8bd2189cf411c">example usage</a>).




   <h4 id="owl">OWL</h4>
    <p>As an experimental feature, an <a href="https://en.wikipedia.org/wiki/Web_Ontology_Language">OWL</a> definition file <a href="{{staticPath}}/docs/schemaorg.owl">schemaorg.owl</a> is available. It includes
        the core and all current extensions to the vocabulary.</p>
    <p>The structure of the file differs from the above vocabulary definition files, in that <code>schema:domainIncludes</code> &amp; <code>schema:rangIncludes</code>
        values are converted into <code>rdfs:domain</code> &amp; <code>rdfs:range</code> values using <code>owl:unionOf</code> to capture the multiplicity of values.
        Included in the range values are the, implicit within the vocabulary, default values of <a href="{{staticPath}}/Text">Text</a>, <a href="{{staticPath}}/URL">URL</a>,
        and <a href="{{staticPath}}/Role">Role</a>.</p>
    <p>This file has been made available to enable the representation of the vocabulary in some OWL-based modeling tools.
      The mapping into OWL is an approximation, and should not be considered an authoritative definition for Schema.org's terms; see <a href="{{staticPath}}/docs/datamodel.html">datamodel page</a> for details.
      As an experimental feature, there are no expectations as to its interpretation by any third party tools.</p>
    <br/>

  </div>


<div id="footer"><p>
  <a href="../docs/terms.html">Terms and conditions</a></p>
</div>
<script>
function getschemafilename(){
	path = document.getElementById("filename").value;
	ext = document.getElementById("fileext").value;
	csvfmt = ""
	if( ext == ".csv"){
		csvfmt = document.getElementById("csvfmt").value;
	}
	return (path + csvfmt + ext);
}

function updatetext(){

	if(document.getElementById("fileext").value == ".csv"){
		document.getElementById("csvsel").style.display = 'block';
	}
	else{
		document.getElementById("csvsel").style.display = 'none';
	}

	document.getElementById("label").innerHTML = getschemafilename();
}

function dowloadfunc(){
	//alert(path + ext);
	window.location.href = getschemafilename();
}


</script>
</body>
</html>
