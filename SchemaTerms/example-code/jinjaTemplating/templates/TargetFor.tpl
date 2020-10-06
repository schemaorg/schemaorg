{% for prop in term.expectedTypeFor %}
  {% if loop.first %}
	<br/><div id="incoming">Instances of <a href="{{href_prefix}}{{term.id}}.html">{{term.id}}</a> {{INSERT}} may appear as a value for the following properties</div>
	<table class="definition-table">
    <thead><tr><tr><th>Property</th><th>On Types</th><th>Description</th></tr></thead>
  {% endif %}
  <tr><td class="prop-nam" scope="row"><code><a href="{{href_prefix}}{{prop.id}}.html">{{prop.id}}</a></code></td>
      <td class="prop-ect">{% for ect in prop.domainIncludes %}{% if not loop.first %}&nbsp; or <br/>{% endif %}<a href="{{href_prefix}}{{ect}}.html">{{ect}}</a>{% endfor %}</td>
      <td class="prop-desc">{{ prop.comment | safe}}
  </tr> 
  
  {% if loop.last %}
	 </table>
  {% endif %}
{% endfor %}
