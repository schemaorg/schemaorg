

<ul>{% for item in type.subtypes recursive %}
  <li class="outer-li"><a href="/{{ item.id|e }}">{{ item.id|e }}</a>
      <ul class="inner">
    {% if item.subtypes %}
        <li class="li-loop">{{ loop(item.subtypes) }}</li>
    {% endif %}
      </ul>
  </li>{% endfor %}</ul>
