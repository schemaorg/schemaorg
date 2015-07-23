<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Schema.org - Full Releases</title>
    <meta name="description" content="Schema.org is a set of extensible schemas that enables webmasters to embed
    structured data on their web pages for use by search engines and other applications." />
    <link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />
    <basxe href="{{ base_href }}" ></base>
</head>
<body style="text-align: left;">

    <div id="container">
        <div id="intro">
            <div id="pageHeader">
                <div class="wrapper">
                    <h1>schema.org</h1>

                    <div id="cse-search-form" style="width: 400px;"></div>

                    <script type="text/javascript" src="//www.google.com/jsapi"></script>
                    <script type="text/javascript">
                    google.load('search', '1', {language : 'en', style : google.loader.themes.ESPRESSO});
                    google.setOnLoadCallback(function() {
                        var customSearchControl = new google.search.CustomSearchControl('013516846811604855281:nj5laplixaa');
                        customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
                        var options = new google.search.DrawOptions();
                        options.enableSearchboxOnly("../docs/search_results.html", null, false, '#');
                        customSearchControl.draw('cse-search-form', options);
                    }, true);
                    </script>


                </div>
            </div>
        </div>
    </div>

    <div id="selectionbar">
        <div class="wrapper">
            <ul>
                <li >
                    <a href="/docs/documents.html">Documentation</a></li>
                    <li class="activelink">
                        <a href="/docs/schemas.html">Schemas</a></li>
                        <li >
                            <a href="/">Home</a></li>
                        </ul>
                    </div>

                </div>
                <div style="padding: 14px; float: right;" id="languagebox"></div>




<div style="margin-left: 8%; margin-right: 8%">

<h1>Schema.org versions</h1>

<p>See the <a href="/docs/releases.html">releases page</a> for a longer and more detailed history of schema.org releases.</p>

<p>The following snapshot(s) of schema.org releases are available:</p>

<ul>
{% for release in releases %}
  <li><a href="/version/{{release}}">{{release}}</a></li>
{% endfor %}
</ul>


<br/><br/>
</div>

