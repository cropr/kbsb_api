## Liste de force Interclubs 2022-2023

Nous confirmons la liste de force du cercle {{ idclub }}: {{ name_short }}, {{ name_long }} pour la saison interclubs 2022-2023

### Joueur

 No | Nom | Matricule | Cercle | Elo |
 -  | - | - | - | -
{% for p in players %}
{{ loop.index }} | {{ p.first_name}} {{ p.last_name}} |  {{ p.idnumber}} | {{ p.idclub }} | {{ p.assignedrating}}
{% endfor %}

### Titulaires des équipes
 
{% for t in teams %}
 - {{ t.name}}: {{ t.titular|join(' ') }}
{% endfor %}

### Transfers sortants

{% for to in transfersout %}
 - {{ to.first_name}} {{ to.last_name}} ({{ to.idnumber }}) naar club {{id.visitingclub }}
{% endfor %}

Le CA de la FRBE