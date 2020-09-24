<!-- Properties block for term: {{term.id}}-->

<!-- Identify if this term or one of its supertypes has any associated proprtyies -->

{% if term.properties|length > 0 %}{% set propstodisplay = True %}{% endif %}
{% for t in term.termStack %}
	  {% if t.properties|length > 0 %}{% set propstodisplay = True %}{% endif %}
{% endfor %}

{% if propstodisplay %}
	<table class="definition-table">
	    <thead>
	      <tr><th>Property</th><th>Expected Type</th><th>Description</th></tr>
	  </thead>
	  {% set propertiesFor = term %}{% include 'PropertiesForTerm.tpl' with context %}

	  {% for t in term.termStack %}
	      {% set propertiesFor = t %}{% include 'PropertiesForTerm.tpl' with context %}
	  {% endfor %}

	 </table>
{% endif %}
