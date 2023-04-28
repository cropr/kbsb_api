## Spelerslijst Interclub 2022-2023

Hierbij bevestigen wij de spelerslijst van {{ idclub }}: {{ name_short }}, {{ name_long }} voor het interclubseizoen 2022-2023

### Spelers

 Nr | Naam | Stamnummer | Club | Elo |
 -  | - | - | - | -
{% for p in players %}
{{ loop.index }} | {{ p.first_name}} {{ p.last_name}} |  {{ p.idnumber}} | {{ p.idclub }} | {{ p.assignedrating}}
{% endfor %}

### Ploegtitularissen
 
{% for t in teams %}
 - {{ t.name}}: {{ t.titular|join(' ') }}
{% endfor %}

### Uitgaande transfers

{% for to in transfersout %}
 - {{ to.first_name}} {{ to.last_name}} ({{ to.idnumber }}) naar club {{id.visitingclub }}
{% endfor %}

het KBSB bestuur