## Spielerliste Interclub 2022-2023

Hiermit bestätigen wir die Spielerliste von {{ idclub }}: {{ name_short }}, {{ name_long }} für die Interclub-Saison 2022-2023

### Spieler

 Nr | Name | ID-Nummer | Verein | Elo |
 -  | - | - | - | -
{% for p in players %}
{{ loop.index }} | {{ p.first_name}} {{ p.last_name}} |  {{ p.idnumber}} | {{ p.idclub }} | {{ p.assignedrating}}
{% endfor %}

### Teaminhaber
 
{% for t in teams %}
 - {{ t.name}}: {{ t.titular|join(' ') }}
{% endfor %}

### Ausgehende Transfers

{% for to in transfersout %}
 - {{ to.first_name}} {{ to.last_name}} ({{ to.idnumber }}) naar club {{id.visitingclub }}
{% endfor %}

het KBSB bestuur