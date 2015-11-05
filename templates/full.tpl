<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Full Hierarchy - {{ sitename }}</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />

<script type="text/javascript">
$(document).ready(function(){
    $('input[type="radio"]').click(function(){
        if($(this).attr("value")=="local"){
            $("#full_thing_tree").hide();
            $("#ext_thing_tree").hide();
            $("#thing_tree").show(500);
        }
        if($(this).attr("value")=="full"){
            $("#thing_tree").hide();
            $("#ext_thing_tree").hide();
            $("#full_thing_tree").show(500);
        }
        if($(this).attr("value")=="ext"){
            $("#thing_tree").hide();
            $("#full_thing_tree").hide();
            $("#ext_thing_tree").show(500);
        }
     });
	$("#full_thing_tree").hide();
	$("#ext_thing_tree").hide();
});
</script>
</head>
<body style="text-align: left;">

{% include 'basicPageHeader.tpl' with context %}

<div style="margin-left: 8%; margin-right: 8%">

<h3>Full Hierarchy</h3>

<p>
Schema.org is defined as two hierarchies: one for textual property values, and one for the things that they describe. 
</p> 

<h4>Thing</h4>

<p>This is the main schema.org hierarchy: a collection of types (or "classes"), each of which has one or more parent types. Although a type may have more than one super-type, here we show each type in one branch of the tree only. There is also a parallel hierarchy for <a href="#datatype_tree">data types</a>.</p>

<br/>
<div>Select vocabulary view:<br/>
    <div>
        <label><input type="radio" name="viewSel" value="local" checked="checked"> {{local_button}}</label>
        <label><input type="radio" name="viewSel" value="full"> {{full_button}}</label>
		{% if ext_button != "" %}
        	<label><input type="radio" name="viewSel" value="ext"> {{ext_button}}</label>
		{% endif %}
	</div>
</div>
	

<div id="thing_tree">
{{ thing_tree | safe }}
</div>
<div class="display: none" id="full_thing_tree">
{{ full_thing_tree | safe }}
</div>
{% if ext_button != "" %}
	<div class="display: none" id="ext_thing_tree">
	{{ ext_thing_tree | safe }}
	</div>
{% endif %}
<div id="datatype_tree">
{{ datatype_tree | safe }}
</div>



<p>An <em>experimental</em> <a href="http://d3js.org">D3</a>-compatible <a href="/docs/tree.jsonld">JSON</a> version is also available.</p>
<br/><br/>

</div>

