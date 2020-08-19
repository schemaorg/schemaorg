<!-- Header start from PageHeader.tpl -->
<div id="container">
	<div id="intro">
		<div id="pageHeader">
			<div class="wrapper">
				<div id="sitename">
    					<a href="/">{{ sitename }}</a>
                </div>
                <div id="cse-search-form" style="width: 400px;"><div class="gcse-searchbox-only" data-resultsUrl="/docs/search_results.html"></div></div>
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
				<a href="{{ docsdir }}documents.html">Documentation</a>
			</li>
	        {% if menu_sel == "Schemas" %}
	        <li class="activelink">
	        {% else %}
	        <li>
	        {% endif %}
				<a href="{{ docsdir }}schemas.html">Schemas</a>
			</li>
			<li>
	        {% if home_page == "True" %}
				<a href="{{ docsdir }}about.html">About</a>
	        {% else %}
				<a href="{{ homedir }}/">Home</a>
	        {% endif %}
			</li>
		</ul>
	</div>
</div> <!-- selectionbar -->
<div class="devnote"><b>Note</b>: you are viewing the
	<!-- <a href="http://webschemas.org/">webschemas.org</a>--> development
	version of <a href="schema.org">schema.org</a>.
	See <a href="/docs/howwework.html">How we work</a> for more details.
</div>

<!-- Header end from PageHeader.tpl -->
