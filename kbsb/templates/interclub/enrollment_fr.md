## Inscription Interclubs 2022-2023

Nous confirmons par la présente l'inscription de {{ idclub }} : {{ name_short }}, {{ name_long }} pour la saison interclubs 2022-2023

Les équipes suivantes étaient inscrites :

  - équipes en division 1 : **{{ teams1 }}**
  - équipes en division 2 : **{{ teams2 }}**
  - équipes en division 3 : **{{ teams3 }}**
  - équipes en division 4 : **{{ teams4 }}**
  - équipes en division 5 : **{{ teams5 }}**


{%- set grouping = {
    "0": "Pas de préférence",
    "1": "1 groupe",
    "2": "2 groupes opposés"
}  %}
{%- set splitting = {
    "1": "En une seule série",
    "2": "En plusieurs séries"
}  %}


Vœux:

 - Equipes regroupées par numéro d'appariement: {{ grouping [wishes.grouping] }}
 - Répartition des équipes dans la même division: {{ splitting [wishes.split] }}
 - Préférences régionales: {{ wishes.regional }}
 - Remarques: {{ wishes.remarks }}

La facture suivra plus tard

le conseil d'administration de la FRBE