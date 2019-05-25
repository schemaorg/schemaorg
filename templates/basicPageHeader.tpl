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
				<div id="cse-search-form" style="width: 400px;"><div class="gcse-searchbox-only" data-resultsUrl="{{ docsdir }}search_results.html"></div></div>
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
</div>

{% include 'topnotes.tpl' with context %}

<!-- Header end from basicPageHeader.tpl -->
