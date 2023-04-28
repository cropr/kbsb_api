## Wijziging Clubgegevens 

Hierbij bevestigen wij de wijziging van de gegevens van {{ idclub }}: {{ name_short }}, {{ name_long }}.


### Details

 - Lange naam: {{ name_long }}
 - Korte naam: {{ name_short }}
 - Federatie: {{ federation }}
 - Hoofd E-mailadres: {{  email_main }}
 - E-mail administratie: {{  email_admin }}
 - E-mail financiën: {{  email_finance }}
 - E-mail interclub: {{  email_interclub }}
 - Website: {{ website }}

### Adres

 - Speellokaal: <br> {{ venue }} 
 - Postadres: <br> {{ address }}

### Bankgegevens

 - Naam rekening: {{ bankaccount_name }}
 - IBAN: {{ bankaccount_iban }}
 - BIC: {{ bankaccount_bic }}

### Bestuursleden

{% for p in bm %}
 - {{ p.function }}: {{ p.first_name}} {{ p.last_name }}
{% endfor %}

### Toegangsrechten ClubAdmin

{% for p in clubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


### Toegangsrechten InterclubAdmin

{% for p in interclubadmin %}
 - {{ p.first_name }} {{ p.last_name}} 
{% endfor %}


het KBSB bestuur