<!DOCTYPE html>
<html lang="en">
<!-- Generated from DataTypePage.tpl -->
<head>
    <title>{{ term.label }} - {{ sitename }}</title>
    <meta charset="utf-8" >
    <link rel="shortcut icon" type="image/png" href="util/favicon.ico"/>
    <link rel="stylesheet" type="text/css" href="util/schemaorg.css" />
    <link rel="stylesheet" type="text/css" href="util/prettify.css" />
    <script type="text/javascript" src="util/prettify.js"></script>
    
</head>
<body>
    {% set TERMTYPE = "DataType" %}
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
	    {% include 'InfoBlock.tpl' with context %}

	    <div><h2>Specific Properties</h2>
	        {% for prop in term.properties %}<a href="{{href_prefix}}{{prop}}.html">{{ prop }}</a>{% if not loop.last %}, {% endif %}{% endfor %}
	    </div>
		
	    <div>
	        {% for type in term.expectedTypeFor %}
	        {% if loop.first %}<h2>Expected Type For</h2>{% endif %}<a href="{{href_prefix}}{{type}}">{{ type }}</a>{% if not loop.last %}, {% endif %}{% endfor %}
	    </div>

	    <div>
	        {% for sub in term.subs %}
	        {% if loop.first %}<h2>More Specific Data Types</h2>{% endif %}<a href="{{href_prefix}}{{sub}}.html">{{ sub }}</a>{% if not loop.last %}, {% endif %}{% endfor %}
	    </div>

		<!-- list source references and acknowledgements -->
		{% include 'Ackblock.tpl' with context %}
		
    </div> <!-- mainContent -->
</body>
</html>
