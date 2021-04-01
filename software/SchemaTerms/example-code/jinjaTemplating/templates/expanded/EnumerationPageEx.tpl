<!DOCTYPE html>
<html lang="en">
<!-- Generated from EnumerationPageEx.tpl -->
<head>
    <title>{{ term.label }} - {{ sitename }}</title>
    <meta charset="utf-8" >
    <link rel="shortcut icon" type="image/png" href="util/favicon.ico"/>
    <link rel="stylesheet" type="text/css" href="util/schemaorg.css" />
    <link rel="stylesheet" type="text/css" href="util/prettify.css" />
    <script type="text/javascript" src="util/prettify.js"></script>
    
</head>
<body>
    {% set TERMTYPE = "Enumeration" %}
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
	    {% include 'InfoBlock.tpl' with context %}
		
		<!-- Show properties (if any) associated with term and its supertypes -->
	    {% include 'PropertiesBlock.tpl' with context %} 
		
		<!-- List properties that have this term as an Expected type -->
	    {% include 'TargetFor.tpl' with context %}
		
		<!-- List enumeration members -->
	    {% set SUBLABEL = "Enumeration members" %}
	    {% set SUBLIST = term.enumerationMembers %}
		    {% include 'Subs.tpl' with context %}

		<!-- List subtypes -->
	    {% set SUBLABEL = "Enumeration Subtypes" %}
	    {% set SUBLIST = term.subs %}
	    	{% include 'Subs.tpl' with context %}
			
		<!-- list surce references and acknowledgements -->
		{% include 'Ackblock.tpl' with context %}

    </div> <!-- mainContent -->
</body>
</html>
