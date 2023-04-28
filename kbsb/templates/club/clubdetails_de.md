## Clubdetails ändern

Hiermit bestätigen wir die Änderung der Daten von {{ idclub }}: {{ name_short }}, {{ name_long }}.


### Einzelheiten

  - Langer Name: {{ name_long }}
  - Kurzname: {{ name_short }}
  - Föderation: {{ federation }}
  - Haupt-E-Mail-Adresse: {{ email_main }}
  - E-Mail-Verwaltung: {{ email_admin }}
  - Finanz-E-Mail: {{ email_finance }}
  - E-Mail-Interclub: {{ email_interclub }}
  - Webseite: {{ website }}

### Adresse

  - Spielirt: <br> {{ venue }}
  - Postanschrift: <br> {{ address }}

### Bankdaten

  - Kontoname: {{ bankaccount_name }}
  - IBAN: {{ bankaccount_iban }}
  - BIC: {{ bankaccount_bic }}

### Vorstandsmitglieder

{% for p in bm %}
 - {{ p.function }}: {{ p.first_name}} {{ p.last_name }}
{% endfor %}

### Zugriffsrechte ClubAdmin

{% for p in clubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


### Zugriffsrechte InterclubAdmin

{% for p in interclubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


der KSB-Vorstand