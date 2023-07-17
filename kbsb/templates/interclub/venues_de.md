## Spielorte Interclubs 2023-2024

Hiermit bestätigen wir die Spielorte des Clubs {{ idclub }}: {{ name_long }} für die Interclubs-Saison 2023-2024

{% for v in venues %}

 - Adresse: {{ v.address }}
 - Kapazität: {{ v.capacity }}
 - E-mail: {{ v.email }}
 - Telefon: {{ v.phone }}
 - Nicht verfügbar auf: {{ v.notavailable | join(', ')}}

{% endfor %}

Der KSB-Vorstand