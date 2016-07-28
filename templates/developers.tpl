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


<h1>Vocabulary Definition Files</h1>

<p>To assist developers, files containing the definition of the core Schema.org vocabulary and its extensions are available for download in common RDF formats.</p>

<p>Older releases can be found (under data/releases/) at <a href="https://github.com/schemaorg/schemaorg">GitHub</a>.

<p>Select the file and format required and click Download.  
<br/>Note: File <em>schema</em> contains the definition of the core vocabulary, <em>all-layers</em> contains definitions for the core and all the extensions.</p>

<p>
	<table padding="2">
	<tr><td>
			File: <select id="filename">
				<option value="{{staticPath}}/releases/{{version}}/schema">schema</option>
				<option value="{{staticPath}}/releases/{{version}}/all-layers">all-layers</option>
				{% for ext in extensions %}
					<option value="{{staticPath}}/releases/{{version}}/ext-{{ ext | safe }}">{{ ext | safe }}</option>
				{% endfor %}
			</select>
	</td>
	<td>
		Format:  <select id="fileext">
				<option value=".nt">Triples</option>
				<option value=".nq">Quads</option>
				<option value=".jsonld">JSON-LD</option>
				<option value=".ttl">Turtle</option>
		</select>
	</td></tr>
	<tr><td colspan="2" align="centre">
		<input type="button" onclick="dowloadfunc();" value="Download"></input>
	</td></tr>
		
	</table>
</p>
  </div>


<div id="footer"><p>
  <a href="../docs/terms.html">Terms and conditions</a></p>
</div>
<script>
function dowloadfunc(){
	path = document.getElementById("filename").value;
	ext = document.getElementById("fileext").value;
	//alert(path + ext);
	window.location.href = path + ext;
}
</script>
</body>
</html>
