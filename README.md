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
Pobieranie danych z serwisu copernicus skutkuje zauważalnie dłuższym czasem wykonania.

Aplikacja domyślnie działa pod adresem 127.0.0.1:5000.

Aby uzyskać dane pogodowe należy zadać zapytanie w ponmiższym formacie:

/api/weather?latitude_start=**latitude_start**&latitude_end=**latitude_end**&longitude_start=**longitude_start**&longitude_end=**longitude_end**&variables=**variables**&time_start=**time_start**&time_end=**time_end**

- **latitude_start** - początek szerokości geograficznej w formacie zmiennoprzecinkowym z kropką
- **latitude_end** - koniec szerokości geograficznej w formacie zmiennoprzecinkowym z kropką
- **longitude_start** - początek długości geograficznej w formacie zmiennoprzecinkowym z kropką
- **longitude_end** - koniec długości geograficznej w formacie zmiennoprzecinkowym z kropką
- **variables** - oczekiwane dane pogodowe oddzielone od siebie przecinkiem
- **time_start** - początek czasu dla którego chcemy uzyskać dane w formacie Unix time
- **time_end** - koniec czasu dla którego chcemy uzyskać dane w formacie Unix time (podanie tej samej wartości co w polu **time_start** spowoduje zwrócenie danych dla punktu czasu)


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

## Instalation
### Anaconda
Run: \
    ```conda create --name <envname> --file requirements.txt``` \
In order to install all the required libraries for the app to function.

Currently only conda installation is supported due to some libraries not being compatible with pip
