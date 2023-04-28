## Speellokalen Interclub 2022-2023

Hierbij bevestigen wij de speellokalen van club {{ idclub }}: {{ name_long }} voor het interclubseizoen 2022-2023

{% for v in venues %}

 - Adres: {{ v.address }}
 - Capaciteit: {{ v.capacity }}
 - e-mail: {{ v.email }}
 - Telefoon: {{ v.phone }}
 - Niet beschikbaar op: {{ v.notavailable | join(', ')}}


{% endfor %}

het KBSB bestuur