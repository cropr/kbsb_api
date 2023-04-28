## Venues Interclub 2022-2023

We hereby confirm the Interclub venues for club {{ idclub }}:  {{ name_long }} for the interclub season 2022-2023

{% for v in venues %}

 - Address: {{ v.address }}
 - Capacity: {{ v.capacity }}
 - Email: {{ v.email }}
 - Telephone: {{ v.phone }}
 - Not available on: {{ v.notavailable | join(', ')}}

{% endfor %}

het KBSB bestuur