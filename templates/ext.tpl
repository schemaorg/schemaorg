
{%- macro overview() -%}

<div class="extinfo">
<h3>Schema.org Section: {{ host_ext }}</h3>
<p>Schema.org is a set of extensible schemas that enables webmasters to embed structured data on their web pages for use by search engines and other applications.
For more details, see the <a href="http://{{ mybasehost }}:{{ myport }}/">homepage</a>.

</p>
<!--
<p>This is the front page for the <em>{{ extName }}</em>, whose short name is: <code>{{ host_ext }}</code></p>
-->
</div>

{%- endmacro %}





{%- macro debugInfo() -%}
  {% if debugging %}
    {{ debugging | safe }}
  {% endif %}
{%- endmacro %}
