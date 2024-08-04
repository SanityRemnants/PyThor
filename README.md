## Czym jest PyThor
PyThor jest biblioteką mająca pozwalać użytkownikowi na dostęp do morskie danych i prognóz pogodowych udostępnianych przez National Oceanic and Atmospheric Administration oraz Copernicus Marine Service.

## Używanie biblioteki i konstrukcja zapytań
Aby kożystać z danych zapewnianych przez Copernicus Marine Service konieczne jest posiadanie darmowego konta w [serwisie](https://data.marine.copernicus.eu/register). Po utworzeniu konta dane do logowania należy podać w pliku config.yaml uzupełniając o dane poniższy fragment pliku:
```
coppernicus_acount:
  username: ""
  password: ""
```
Konto wymagane jest jedynie do uzyskania danych dotyczących pływów i prądów morskich, do używania pozostałych funkcjonalności biblioteki konto nie jest wymagane.

Aplikacja domyślnie działa pod adresem 127.0.0.1:5000.

Aby uzyskać dane pogodowe należy zadać zapytanie w ponmiższym formacie:

127.0.0.1:5000/api/weather?latitude_start=[](https://placehold.it/150/ffffff/ff0000?text=latitude_start)&latitude_end=<span style="color:red">latitude_end</span>&longitude_start=<span style="color:red">longitude_start</span>&longitude_end=<span style="color:red">longitude_end</span>&variables=<span style="color:blue">variables</span>&time_start=<span style="color:yellow">time_start</span>&time_end=<span style="color:yellow">time_end</span>



## przykładowy get:
[http://127.0.0.1:5000/api/weather?latitude_start=36&latitude_end=37&longitude_start=15&longitude_end=16&variables=wave_direction,wave_height,wave_period,wind_direction,wind_speed&time_start=1715415818&time_end=1715441018](http://127.0.0.1:5000/api/weather?latitude_start=36&latitude_end=37&longitude_start=15&longitude_end=16&variables=wave_direction,wave_height,wave_period,wind_direction,wind_speed&time_start=1715415818&time_end=1715441018)

## parametry pogodowe:
- wave_direction
- wave_height
- wave_period
- wind_direction
- wind_speed
- sea_current_speed
- sea_current_direction
- tide_height
