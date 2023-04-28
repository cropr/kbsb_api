## Change Club Details

We hereby confirm the change of the data of {{ idclub }}: {{ name_short }}, {{ name_long }}.


### Details

  - Long name: {{ name_long }}
  - Short name: {{ name_short }}
  - Federation: {{ federation }}
  - Main Email Address: {{ email_main }}
  - Email administration: {{ email_admin }}
  - Email finance: {{ email_finance }}
  - E-mail interclub: {{ email_interclub }}
  - Website: {{ website }}

### Address

  - Venue: <br> {{ venue }}
  - Postal address: <br> {{ address }}

### Bank details

  - Account name: {{ bankaccount_name }}
  - IBAN: {{ bankaccount_iban }}
  - BIC: {{ bankaccount_bic }}

### Board Members

{% for p in bm %}
 - {{ p.function }}: {{ p.first_name}} {{ p.last_name }}
{% endfor %}

### Access rights ClubAdmin

{% for p in clubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


### Access rights InterclubAdmin

{% for p in interclubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


The RBCF board