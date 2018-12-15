<!-- Header start from topnotes.tpl -->

{% if mybasehost in [ "webschemas.org", "localhost"] %}
<div class="devnote"><b>Note</b>: you are viewing the
	<a href="http://webschemas.org/">webschemas.org</a> development
	version of <a href="http://schema.org/">schema.org</a>.
	See <a href="{{ docsdir }}howwework.html">How we work</a> for more details.
</div>
{% endif %}

{% if sitename != "schema.org" and SUBDOMAINS == True %}
<div class="pendnote">
	<b><a href="{{staticPath}}">core</a></b> + <a href="{{extensionPath}}">{{host_ext}}</a>
	({{extName}}): {{extDD|safe}}</div>
{% endif %}

<!-- Header end from topnotes.tpl -->
