## Spielorte Interclub 2022-2023

Hiermit bestätigen wir die Spielorte des Clubs {{ idclub }}: {{ name_long }} für die Interclubs-Saison 2022-2023

{% for v in venues %}

 - Adresse: {{ v.address }}
 - Kapazität: {{ v.capacity }}
 - E-mail: {{ v.email }}
 - Telefon: {{ v.phone }}
 - Nicht verfügbar auf: {{ v.notavailable | join(', ')}}

{% endfor %}

Der KSB-Vorstand