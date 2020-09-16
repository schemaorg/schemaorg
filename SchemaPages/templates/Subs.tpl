<!-- List subs (Subtypes/subproperties/enumeration members/etc.) for Term -->

{% for sub in SUBLIST %}
    {% if loop.first %}
     <br/><b><a  id="subtypes" title="Link: #subtypes" href="#subtypes" class="clickableAnchor" >{{SUBLABEL}}</a></b><ul>
    {% endif %}
	<li> <a href="{{href_prefix}}{{sub}}.html">{{sub}}</a> </li>
    {% if loop.last %}
     </ul>
    {% endif %}
{% endfor %}
