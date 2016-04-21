<!-- Header start from basicPageHeader.tpl -->
<div id="container">
	<div id="intro">
		<div id="pageHeader">
			<div class="wrapper">
				<div id="sitename">
				<h1>
					<a href="/">{{ sitename }}</a>
				</h1>
				</div>
				<div id="cse-search-form" style="width: 400px;"></div>
<script type="text/javascript" src="//www.google.com/jsapi"></script>
<script type="text/javascript">
google.load('search', '1', {language : 'en', style : google.loader.themes.ESPRESSO});
google.setOnLoadCallback(function() {
var customSearchControl = new google.search.CustomSearchControl('013516846811604855281:nj5laplixaa');
customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
var options = new google.search.DrawOptions();
options.enableSearchboxOnly("/docs/search_results.html", null, false, '#');
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
	        {% if menu_sel == "Documentation" %}
	        <li class="activelink">
	        {% else %}
	        <li>
	        {% endif %}
				<a href="/docs/documents.html">Documentation</a>
			</li>
	        {% if menu_sel == "Schemas" %}
	        <li class="activelink">
	        {% else %}
	        <li>
	        {% endif %}
				<a href="/docs/schemas.html">Schemas</a>
			</li>
			<li>
	        {% if home_page == "True" %}
				<a href="{{staticPath}}/docs/about.html">About</a>
	        {% else %}
				<a href="/">Home</a>
	        {% endif %}
			</li>
		</ul>
	</div>
</div>
<div style="padding: 14px; float: right;" id="languagebox"></div>


{% if mybasehost in [ "webschemas.org", "localhost"] %}
<div id="pertermwebschemasnote" style="padding: 0.7em; background-color:#d9edf7; color: #000; border: 1px solid #bce8f1; border-bottom: none;"><b>Note</b>: you are viewing the <a href="http://webschemas.org/">webschemas.org</a> development
	version of <a href="http://schema.org/">schema.org</a>.  See <a href="/docs/howwework.html">How we work</a> for more details.
</div>
{% endif %}

{% if "pending" in sitename %}
<div id="pertermwebschemasnote" style="padding: 0.7em; background-color:#fcf8e3; color: #000; border: 1px solid #faebcc;"><b>pending section</b>: these terms are <a href="/docs/howwework.html#pending">pending</a> wider review. Feedback is welcomed!
</div>
{% endif %}

<!-- Header end from basicPageHeader.tpl -->
