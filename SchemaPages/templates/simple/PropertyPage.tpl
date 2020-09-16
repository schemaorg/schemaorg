<!DOCTYPE html>
<html lang="en">
<!-- Generated from PropertyPage.tpl -->
<head>
    <title>{{ term.label }} - {{ sitename }}</title>
    <meta charset="utf-8" >
    <link rel="shortcut icon" type="image/png" href="util/favicon.ico"/>
    <link rel="stylesheet" type="text/css" href="util/schemaorg.css" />
    <link rel="stylesheet" type="text/css" href="util/prettify.css" />
    <script type="text/javascript" src="util/prettify.js"></script>
    
</head>
<body>
    {% set TERMTYPE = "Property" %}
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
	    {% include 'InfoBlock.tpl' with context %}

	    <div><h2>Values expected to be one of these types</h2>
	        {% for type in term.rangeIncludes %}<a href="{{href_prefix}}{{type}}.html">{{ type }}</a>{% if not loop.last %}, {% endif %}{% endfor %}
	    </div>
	    <div><h2>Used on these types</h2>
	        {% for type in term.domainIncludes %}<a href="{{href_prefix}}{{type}}.html">{{ type }}</a>{% if not loop.last %}, {% endif %}{% endfor %}
	    </div>

		<!-- List subproperties -->
	    {% set SUBLABEL = "Sub-properties" %}
	    {% set SUBLIST = term.subs %}
	    	{% include 'Subs.tpl' with context %}

		<!-- list surce references and acknowledgements -->
		{% include 'Ackblock.tpl' with context %}
		
    </div> <!-- mainContent -->
</body>
</html>
