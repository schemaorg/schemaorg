
{%- macro overview(name='', abbrev='') -%}

<div class="extinfo">
<h3>Schema.org Hosted Extension: {{ name }}</h3>
<p>Schema.org is a set of extensible schemas that enables webmasters to embed structured data on their web pages for use by search engines and other applications. 
For more details, see the <a href="/">homepage</a>.

</p>
<p>This is the front page for the <em>{{name}}</em> extension, whose short name is: {{ abbrev }}</p>
</div>

{%- endmacro %}


{%- macro debugInfo() -%}

<div style="clear: both; float: left; font-size: smaller; margin: 1em;">
 <dl>
  <dt>SCHEMA_VERSION:</dt><dd>{{ SCHEMA_VERSION }}</dd>
  <dt>ENABLE_JSONLD_CONTEXT:</dt><dd>{{ ENABLE_JSONLD_CONTEXT }}</dd>
  <dt>ENABLE_CORS:</dt><dd>{{ ENABLE_CORS }}</dd>
  <dt>os_host:</dt><dd>{{ os_host }}</dd>
  <dt>host_ext:</dt><dd>{{ host_ext }}</dd>
 </dl>
</div>

{%- endmacro %}
