<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Schemas - schema.org</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />
</head>
<body onload="updatetext()">

{% include 'basicPageHeader.tpl' with context %}


  <div id="mainContent" class="faq">


<h2>Schema.org for Developers</h2>

<p>
This is a placeholder page for developer-oriented information about schema.org. In particular it gives access to machine-readable representations of our schemas.
</p>


<h2 id="conneg">Machine Readable Term Definitions</h2>

<p>Machine-readable definitions of individual terms is availble as RDFa, embeded into the term page html. It is also available in other formats by accessing term URLs, using the <a href="https://www.w3.org/TR/swbp-vocab-pub/#negotiation">Linked Data Content Negotiation</a> technique of providing the required type in an HTTP Accept header value.  The same content is also available by providing an appropriate suffix to the term URL.  For example the Triples definition for the <a href="{{staticPath}}/Book">Book</a> Type can bet retrieved with the following URL <a href="{{staticPath}}/Book.nt">{{staticPath}}/Book.nt</a>.</p>
<p>The currently supported format types, relevant Accept values and url suffixes are:</p>
	<ul><li>JSON-LD - application/ld+json - .jsonld</li>
		<li>RDF/XML - application/rdf+xml - .rdf</li>
		<li>Triples - text/plain - .nt</li>
		<li>Turtle - application/x-turtle - .ttl</li>
		<li>CSV - text/csv - .csv</li></ul>
		
<p><strong>Note:</strong> This is currently an experimental feature</p>

<h2 id="defs">Vocabulary Definition Files</h2>

<p>To assist developers, files containing the definition of the core Schema.org vocabulary and its extensions are available for download in common RDF formats.</p>

<p>Older releases can be found (under data/releases/) at <a href="https://github.com/schemaorg/schemaorg">GitHub</a>.

<p>Select the file and format required and click Download.  
<br/>Note: File <em>schema</em> contains the definition of the core vocabulary, <em>all-layers</em> contains definitions for the core and all the extensions.</p>

<p>
	<table padding="2" width="600">
	<tr><td width="30%">
			File: <select id="filename"  onchange="updatetext()">
				<option value="{{staticPath}}/version/latest/schema">schema</option>
				<option value="{{staticPath}}/version/latest/all-layers">all-layers</option>
				{% for ext in extensions %}
					<option value="{{staticPath}}/version/latest/ext-{{ ext | safe }}">{{ ext | safe }}</option>
				{% endfor %}
			</select>
	</td>
	<td width="30%">
		Format:  <select id="fileext" onchange="updatetext()">
				<option value=".nt">Triples</option>
				<option value=".nq">Quads</option>
				<option value=".jsonld">JSON-LD</option>
				<option value=".rdf">RDF/XML</option>
				<option value=".ttl">Turtle</option>
				<option value=".csv">CSV</option>
		</select>
	</td>
	<td width="30%">
		<div id ="csvsel">
			For: <select id="csvfmt" onchange="updatetext()">
				<option value="-types">Types</option>
				<option value="-properties">Properties</option>
				<option value="-enumvalues">Enumeration Values</option>
			</select>
		</div>
	</td>
	</tr>
	<tr><td colspan="3">
		<div id="label"></div>
	<tr><td colspan="3" align="centre">
		<input type="button" onclick="dowloadfunc();" value="Download"></input>
	</td></tr>
		
	</table>
</p>
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
