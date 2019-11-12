<!DOCTYPE html>
<html lang="en">
<head>
  {% include 'headtags.tpl' with context %}
    <title>Full Hierarchy - {{ sitename }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
	$("#thing_tree").hide();
	$("#ext_thing_tree").hide();
    $("#full_thing_tree").show();
});
</script>
<style>
    ul {
        flex-wrap: wrap;
    }
    .scroll-ul{
        max-width:100%;
        min-width:300px;
        overflow-x: scroll;
        height: auto;
        border: 0;
    }
    @media all and (min-width: 500px ){
        .scroll-ul {
            line-height: 160%;
        }
    }
    @media all and (max-width: 500px ){
        .scroll-ul {
            line-height: 200%;
        }
    }
</style>

</head>
<body style="text-align: center;">

{% include 'docsBasicPageHeader.tpl' with context %}

<div style="text-align: left; margin-left: 8%; margin-right: 8%">

<h3>Full Hierarchy</h3>

<p>
Schema.org is defined as two hierarchies: one for textual property values, and one for the things that they describe. 
</p> 

<p>This is the main schema.org hierarchy: a collection of types (or "classes"), each of which has one or more parent types. Although a type may have more than one super-type, here we show each type in one branch of the tree only. There is also a parallel hierarchy for <a href="#datatype_tree">data types</a>.</p>

<br/>
<!--
<div>Select vocabulary view:<br/>
    <div>
        <label><input type="radio" name="viewSel" value="local"> {{local_button}}</label>
        <label><input type="radio" name="viewSel" value="full"  checked="checked"> {{full_button}}</label>
		{% if ext_button != "" %}
        	<label><input type="radio" name="viewSel" value="ext"> {{ext_button}}</label>
		{% endif %}
	</div>
</div>
-->
	

{% if thing_tree != "" %}
    <div class="scroll-ul" id="thing_tree">
    {{ thing_tree | safe }}
    </div>
{% endif %}
{% if full_thing_tree != ""  %}
<!--<div class="display: none" id="full_thing_tree">-->
<div class="scroll-ul" id="full_thing_tree">
{{ full_thing_tree | safe }}
</div>
{% endif %}
{% if ext_thing_tree != ""  %}
    {% if ext_button != "" %}
    	<div class="display: none" id="ext_thing_tree">
    	{{ ext_thing_tree | safe }}
    	</div>
    {% endif %}
{% endif %}
{% if datatype_tree != "" %}
    <div class="scroll-ul" id="datatype_tree">
    {{ datatype_tree | safe }}
    </div>
{% endif %}



<p>An <em>experimental</em> <a href="http://d3js.org">D3</a>-compatible <a href="/docs/tree.jsonld">JSON</a> version is also available.</p>
<br/><br/>

</div>
</body>
</html>

