<!DOCTYPE html>
<html lang="en">
<!-- Generated from Home.tpl -->
    {% include 'docs/DocsHead.tpl' with context %}
<body>
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
    <h3>Schema.org Section: pending</h3>
    <p>Schema.org is a set of extensible schemas that enables webmasters to embed structured data on their web pages for use by search engines and other applications.
    For more details, see the <a href="http://None:/">homepage</a>.

    </p>

    <p>
      The Pending Section is a staging area for work-in-progress terms which have yet to be accepted into the core vocabulary. <em>Pending</em> terms are subject to change and should be used with caution.<br/><br/>

    Implementors and publishers are cautioned that terms in the pending extension may lack consensus and that terminology and definitions could still change significantly after community and steering group review. Consumers of schema.org data who encourage use of such terms are strongly encouraged to update implementations and documentation to track any evolving changes, and to share early implementation feedback with the wider community.
    </p>
    {% for c in sectionterms %}
        {% set cat = sectionterms[c] %}
        {% if loop.first %}<h3>{{termcount}} Terms defined in the 'pending' section.</h3>{% endif %}
        {% for term in cat["Type"] %}
            {%if loop.first %}<br/>{{c}} Types ({{cat["Type"]|length}})<br/>{% else %}, {% endif %}{{ sdotermlink(term)|safe }}
            {% if loop.last %}<br/>{% endif %}
        {% endfor %}
        {% for term in cat["Property"] %}
            {%if loop.first %}<br/>{{c}} Properties ({{cat["Property"]|length}})<br/>{% else %}, {% endif %}{{ sdotermlink(term)|safe}}
            {% if loop.last %}<br/>{% endif %}
        {% endfor %}
        {% for term in cat["Enumeration"] %}
            {%if loop.first %}<br/>{{c}} Enumerations ({{cat["Enumeration"]|length}})<br/>{% else %}, {% endif %}{{ sdotermlink(term)|safe}}
            {% if loop.last %}<br/>{% endif %}
        {% endfor %}
        {% for term in cat["Enumerationvalue"] %}
            {%if loop.first %}<br/>{{c}} Enumeration Members ({{cat["Enumerationvalue"]|length}})<br/>{% else %}, {% endif %}{{ sdotermlink(term)|safe}}
            {% if loop.last %}<br/>{% endif %}
        {% endfor %}
        {% for term in cat["Datatype"] %}
            {%if loop.first %}<br/>{{c}} Datatypes ({{cat["Datatype"]|length}})<br/>{% else %}, {% endif %}{{ sdotermlink(term)|safe}}
            {% if loop.last %}<br/>{% endif %}
        {% endfor %}
    {% endfor %}    
    </div> <!-- mainContent -->
	{% include 'PageFooter.tpl' with context %}
</body>
</html>