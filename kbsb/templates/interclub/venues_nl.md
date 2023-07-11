## Speellokalen Interclub 2023-2024

Hierbij bevestigen wij de speellokalen van club {{ idclub }}: {{ name }} voor het interclubseizoen 2023-2024

{% for v in venues %}

 - Adres: {{ v.address }}
 - Capaciteit: {{ v.capacity }}
 - e-mail: {{ v.email }}
 - Telefoon: {{ v.phone }}
 - Niet beschikbaar op: {{ v.notavailable | join(', ')}}


{% endfor %}

het KBSB bestuur