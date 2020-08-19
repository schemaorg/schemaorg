<!DOCTYPE html>
<html lang="en">
<!-- Generated from TermPageEx.tpl -->
    {% if term.termType == "Type" %}{% set TERMTYPE = "Type" %}
    {% elif term.termType == "Property" %}{% set TERMTYPE = "Property" %}
    {% elif term.termType == "Datatype" %}{% set TERMTYPE = "Data Type" %}
    {% elif term.termType == "Enumeration" %}{% set TERMTYPE = "Enumeration" %}
    {% elif term.termType == "Enumerationvalue" %}{% set TERMTYPE = "Enumeration Member" %}
    {% endif %}
    {% include 'terms/Head.tpl' with context %}
<body>
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
	    {% include 'terms/InfoBlock.tpl' with context %}
		
		{% if term.termType == "Type" or term.termType == "Datatype" or term.termType == "Enumeration" %}
            <!-- Show properties (if any) associated with term and its supertypes -->
    	    {% include 'terms/PropertiesBlock.tpl' with context %} 
		
    		<!-- List properties that have this term as an Expected type -->
    	    {% include 'terms/TargetFor.tpl' with context %}
        {% endif %}
        
        {% if term.termType == "Property" %}
            {% if term.inverse %}
            <p>Inverse-property: {{ sdotermlink(term.inverse)|safe }}</a></p>
            {% endif %}
            
            <table class="definition-table">
                <thead><tr><th>Values expected to be one of these types</th></tr></thead>
                <tr><td><code>
                {% for type in term.rangeIncludes %}{{ sdotermlink(type)|safe }}{% if not loop.last %}<br/>{% endif %}{% endfor %}
                </td></code></tr>
            </table>
            <table class="definition-table">
                <thead><tr><th>Used on these types</th></tr></thead>
                <tr><td><code>
                {% for type in term.domainIncludes %}{{ sdotermlink(type)|safe }}{% if not loop.last %}<br/>{% endif %}{% endfor %}
                </td></code></tr>
            </table>
        {% endif %}
        	
		{% if term.termType == "Enumeration" %}
            <!-- List enumeration members -->
    	    {% set SUBLABEL = "Enumeration members" %}
    	    {% set SUBLIST = term.enumerationMembers %}
    		    {% include 'terms/Subs.tpl' with context %}
        {% endif %}

		
        <!-- List subtypes/subproperties -->
        {% if term.termType != "Enumerationvalue" %}
            {% if term.termType == "Type" %}{% set SUBLABEL = "More specific Types" %}
            {% elif term.termType == "Datatype" %}{% set SUBLABEL = "More specific Data Types" %}
            {% elif term.termType == "Enumeration" %}{% set SUBLABEL = "Enumeration Subtypes" %}
            {% elif term.termType == "Property" %}{% set SUBLABEL = "Sub-properties" %}
            {% endif %}
    	    {% set SUBLIST = term.subs %}
    	    	{% include 'terms/Subs.tpl' with context %}
        {% endif %}
			
		<!-- list source references and acknowledgements -->
		{% include 'terms/Ackblock.tpl' with context %}

		<!-- list examples  -->
		{% include 'terms/Examplesblock.tpl' with context %}
		
    </div> <!-- mainContent -->
	{% include 'PageFooter.tpl' with context %}
</body>
</html>
