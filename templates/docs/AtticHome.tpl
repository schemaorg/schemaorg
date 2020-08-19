<!DOCTYPE html>
<html lang="en">
<!-- Generated from Home.tpl -->
    {% include 'docs/DocsHead.tpl' with context %}
<body>
    {% include 'PageHeader.tpl' with context %}
    <div id="mainContent">
<h3>Schema.org Section: attic</h3>
<p>Schema.org is a set of extensible schemas that enables webmasters to embed structured data on their web pages for use by search engines and other applications.
For more details, see the <a href="http://None:/">homepage</a>.

</p>

<p>
  The attic area is an archive area for terms which are no longer part of the core vocabulary or its extensions. <em>Attic</em> terms are preserved here to satisfy previous links to them.<br/>

Implementors and publishers are gently encouraged not to use terms in the attic area.
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