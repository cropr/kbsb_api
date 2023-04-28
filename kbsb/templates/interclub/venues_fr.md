## Salles de jeux Interclubs 2022-2023

Nous confirmons par la présente les salles de jeux du cercle {{ idclub }}:  {{ name_long }} pour la saison interclubs 2022-2023

{% for v in venues %}

 - Adresse: {{ v.address }}
 - Capacité: {{ v.capacity }}
 - e-mail: {{ v.email }}
 - Téléphone: {{ v.phone }}
 - Indisponible aux dates: {{ v.notavailable | join(', ')}}


{% endfor %}

Le conseil d'administration de la FRBE