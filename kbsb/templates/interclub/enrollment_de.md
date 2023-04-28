## Anmeldung Interclubs 2022-2023

Hiermit bestätigen wir die Anmeldung von {{ idclub }}: {{ name_short }}, {{ name_long }} für die Interclubs-Saison 2022-2023

Folgende Mannschaften waren gemeldet:

  - Mannschaften in Division 1: **{{ teams1 }}**
  - Mannschaften in Division 2: **{{ teams2 }}**
  - Mannschaften in Division 3: **{{ teams3 }}**
  - Mannschaften in Division 4: **{{ teams4 }}**
  - Mannschaften in Division 5: **{{ teams5 }}**



{%- set grouping = {
    "0": "keine Präferenz",
    "1": "1 Gruppe",
    "2": "2 entgegengesetzte Gruppen"
}  %}
{%- set splitting = {
    "1": "In 1 Einzelserie",
    "2": "In mehrere Serien"
}  %}


Wünsche:

 - Teams gruppiert nach Paarung-Nummer: {{ grouping [wishes.grouping] }}
 - Verteilung der Teams in derselben Division: {{ splitting [wishes.split] }}
 - Regionale Präferenzen: {{ wishes.regional }}
 - Bemerkungen: {{ wishes.remarks }}
 
Die Rechnung folgt später

der KSB-Vorstand