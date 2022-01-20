<!-- Properties for Term: {{propertiesFor.id}}-->

{% for prop in propertiesFor.properties %}
    {% if loop.first %}
        <tr class="supertype"><th class="supertype-name" colspan="3">Properties from <a   href="{{href_prefix}}{{propertiesFor.id}}.html">{{propertiesFor.id}}</a></th></tr>
    {% endif %}
	
    <tr><td class="prop-nam" scope="row"><code><a href="{{href_prefix}}{{prop.id}}.html">{{prop.id}}</a></code></td>
        <td class="prop-ect">{% for ect in prop.rangeIncludes %}{% if not loop.first %}&nbsp; or <br/>{% endif %}<a href="{{href_prefix}}{{ect}}.html">{{ect}}</a>{% endfor %}</td>
        <td class="prop-desc">{{ prop.comment | safe}}
    </tr>
{% endfor %}
