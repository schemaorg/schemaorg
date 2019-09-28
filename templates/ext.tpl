
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

{% if not debugging %}<div style="display: none;">{%- endif %}

<div style="clear: both; float: left; text-align: left; font-size: xx-small; color: #888 ; margin: 1em; line-height: 100%;">
 <ul>
  <li>SCHEMA_VERSION: {{ SCHEMA_VERSION }} </li>
  <li>PYTHONAPP_VERSION: {{ PYTHONAPP_VERSION }} </li>
  <li>ENABLE_HOSTED_EXTENSIONS:  {{ ENABLE_HOSTED_EXTENSIONS  }} </li>
  <li>host_ext: {{ host_ext }} </li>
  <li>myhost: {{ myhost }} </li>
  <li>myport: {{ myport }} </li>
  <li>mybasehost: {{ mybasehost }} </li>
  <li>debugging: {{ debugging }} </li>
  <li>AppEngine Version: {{ appengineVersion }} </li>
 </ul>
</div>

{% if not debugging %}</div>{%- endif %}



{%- endmacro %}
