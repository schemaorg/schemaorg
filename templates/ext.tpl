
{%- macro overview(name='', abbrev='') -%}

<div class="extinfo">
<h3>Schema.org Hosted Extension: {{ name }}</h3>
<p>Schema.org is a set of extensible schemas that enables webmasters to embed structured data on their web pages for use by search engines and other applications.
For more details, see the <a href="http://{{ mybasehost }}:{{ myport }}/">homepage</a>.

</p>
<p>This is the front page for the <em>{{name}}</em>, whose short name is: <code>{{ abbrev }}</code></p>
</div>

{%- endmacro %}





{%- macro debugInfo() -%}

{% if not debugging %}<div style="display: none;">{%- endif %}

<div style="clear: both; float: left; text-align: left; font-size: xx-small; color: #888 ; margin: 1em; line-height: 100%;">
 <ul>
  <li>SCHEMA_VERSION: {{ SCHEMA_VERSION }} </li>
  <li>ENABLE_HOSTED_EXTENSIONS:  {{ ENABLE_HOSTED_EXTENSIONS  }} </li>
  <li>host_ext: {{ host_ext }} </li>
  <li>myhost: {{ myhost }} </li>
  <li>myport: {{ myport }} </li>
  <li>mybasehost: {{ mybasehost }} </li>
  <li>debugging: {{ debugging }} </li>
 </ul>
</div>

{% if not debugging %}</div>{%- endif %}



{%- endmacro %}
