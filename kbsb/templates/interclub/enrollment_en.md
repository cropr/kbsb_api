`## Registration Interclub 2022-2023

We hereby confirm the registration of {{ idclub }}: {{ name_short }}, {{ name_long }} for the interclub season 2022-2023

The following teams were entered:

  - teams in division 1: **{{ teams1 }}**
  - teams in division 2: **{{ teams2 }}**
  - teams in division 3: **{{ teams3 }}**
  - teams in division 4: **{{ teams4 }}**
  - teams in division 5: **{{ teams5 }}**



{%- set grouping = {
    "0": "Geen Voorkeur",
    "1": "1 groep",
    "2": "2 tegengestelde groepen"
}  %}
{%- set splitting = {
    "1": "In 1 reeks",
    "2": "In meerdere reeksen"
}  %}


Wishes:

 - Teams grouped by pairing number: {{ grouping [wishes.grouping] }}
 - Distribution of teams in same division: {{ splitting [wishes.split] }}
 - Regional preferences: {{ wishes.regional }}
 - Remarks: {{ wishes.remarks }}
 
The invoice will follow later

the RBCF board`