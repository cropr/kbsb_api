## Modifier les détails du club

Nous confirmons par la présente la modification des données de {{ idclub }}: 
{{ name_short }}, {{ name_long }}.

### Détails

 - Nom long: {{ name_long }}
 - Nom court: {{ name_short }}
 - Fédération: {{ federation }}
 - Adresse e-mail principale: {{ email_main }}
 - Adresse e-mail administration: {{ email_admin }}
 - Adresse e-mail financier : {{ email_finance }}
 - Adresse e-mail interclub : {{ email_interclub }}
 - Site Web: {{ website }}

### Adresse

  - Salle de jeux : <br> {{ venue }}
  - Adresse postale : <br> {{ address }}

### Coordonnées bancaires

  - Nom du compte : {{ bankaccount_name }}
  - IBAN : {{ bankaccount_iban }}
  - BIC : {{ bankaccount_bic }}

### Membres du conseil d'administration

{% for p in bm %}
 - {{ p.function }}: {{ p.first_name}} {{ p.last_name }}
{% endfor %}

### Droits d'accès ClubAdmin

{% for p in clubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


### Droits d'accès InterclubAdmin

{% for p in interclubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


le conseil d'administration de la FRBE