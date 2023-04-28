## Playerlist Interclub 2022-2023

With this email we confirm the player list for {{ idclub }}: {{ name_short }}, {{ name_long }} for the interclub season 2022-2023

### Players

 N. | Name | ID number | Club | Elo |
 -  | - | - | - | -
{% for p in players %}
{{ loop.index }} | {{ p.first_name}} {{ p.last_name}} |  {{ p.idnumber}} | {{ p.idclub }} | {{ p.assignedrating}}
{% endfor %}

### Titulars team
 
{% for t in teams %}
 - {{ t.name}}: {{ t.titular|join(' ') }}
{% endfor %}

### outgoing transfers

{% for to in transfersout %}
 - {{ to.first_name}} {{ to.last_name}} ({{ to.idnumber }}) naar club {{id.visitingclub }}
{% endfor %}

The baord of the RBCF 