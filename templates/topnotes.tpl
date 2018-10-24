<!-- Header start from topnotes.tpl -->

{% if mybasehost in [ "localhost"] %}
<div class="devnote"><b>Note</b>: you are viewing the
	<!-- <a href="http://webschemas.org/">webschemas.org</a>--> development
	version of <a href="{{ sitename }}">{{ sitename }}</a>.
	See <a href="{{ docsdir }}howwework.html">How we work</a> for more details.
</div>
{% endif %}

{% if sitename != "schema.org" and host_ext != "" and extName != "" and extDD != "" %}
<div class="pendnote">
	<b><a href="{{staticPath}}">core</a></b> + <a href="{{extensionPath}}">{{host_ext}}</a>
	({{extName}}): {{extDD|safe}}</div>
{% endif %}

<!-- Header end from topnotes.tpl -->
