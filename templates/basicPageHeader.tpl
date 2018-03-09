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
				<div id="cse-search-form" style="width: 400px;"><gcse:searchbox-only resultsUrl="/docs/search_results.html"></gcse:searchbox-only></div>
<script type="text/javascript" src="//www.google.com/jsapi"></script>

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
<div class="devnote"><b>Note</b>: you are viewing the
	<a href="http://webschemas.org/">webschemas.org</a> development
	version of <a href="http://schema.org/">schema.org</a>.
	See <a href="/docs/howwework.html">How we work</a> for more details.
</div>
{% endif %}

{% if sitename != "schema.org" %}
<div class="pendnote">
	<b><a href="{{staticPath}}">core</a></b> + <a href="{{extensionPath}}">{{host_ext}}</a>
	({{extName}}): {{extDD|safe}}</div>
{% endif %}

<!-- Header end from basicPageHeader.tpl -->
