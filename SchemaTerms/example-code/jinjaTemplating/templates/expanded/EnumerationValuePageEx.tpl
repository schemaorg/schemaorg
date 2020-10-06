<!DOCTYPE html>
<html lang="en">
<!-- Generated from EnumerationValuePageEx.tpl -->
<head>
    <title>{{ term.label }} - {{ sitename }}</title>
    <meta charset="utf-8" >
    <link rel="shortcut icon" type="image/png" href="util/favicon.ico"/>
    <link rel="stylesheet" type="text/css" href="util/schemaorg.css" />
    <link rel="stylesheet" type="text/css" href="util/prettify.css" />
    <script type="text/javascript" src="util/prettify.js"></script>
    
</head>
<body>
    {% set TERMTYPE = "Enumeration Member" %}
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
    {% include 'InfoBlock.tpl' with context %}
    <div>
        <br/>A member of the <a href="{{href_prefix}}{{ term.enumerationParent }}.html">{{ term.enumerationParent }}</a> enumeration type.
    </div>
    </div> <!-- mainContent -->
</body>
</html>
