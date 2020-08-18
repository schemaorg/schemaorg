{% if term.supersedes|length > 0 %}
	<table class="definition-table"><thead><tr><th><a href="{{href_prefix}}supersedes.html">supersedes</a></th></tr></thead>
	<tr><td><code><a href="{{href_prefix}}{{term.supersedes}}.html">{{term.supersedes}}</a></td></tr>
     </table>
{% endif %}
{% if term.supersededBy|length > 0 %}
	<table class="definition-table"><thead><tr><th><a href="{{href_prefix}}supersededBy.html">supersededBy</a></th></tr></thead>
	<tr><td><code><a href="{{href_prefix}}{{term.supersededBy}}.html">{{term.supersededBy}}</a></td></tr>
     </table>
{% endif %}

{% for ack in term.acknowledgements %}
    {% if loop.first %}
	<h4  id="acks">Acknowledgement</h4>
    {% endif %}
	<p>{{ack |safe}}</p>
    {% if loop.last %}<br/>{% endif %}
{% endfor %}

{% for source in term.sources %}
    {% if loop.first %}
	<h4  id="acks">Source</h4>
    {% endif %}
	<p><a href="{{href_prefix}}{{source}}">{{source}}</a></p>
    {% if loop.last %}<br/>{% endif %}
{% endfor %}

