# Heizungssteuerung mit dem ESP32 - Teil 2

Beim letzten mal haben wir den ESP32 soweit bekommen, dass wir ihn über WiFi konfigurieren konnten. Seit dem habe ich die Datei `nw_config.py` etwas aufgehübscht (eigentlich nur CSS) und einen Teil aus der `main.py` in die neu erstellte `heater_http.py` ausgelagert. Einfach nur der Übersichtlichkeit halber.

Dieses Tutorial startet also bei `main_v7.py`, `heater_http_v1.py` und `nw_config_v3.html`. Meine `main.py` sieht jetzt so aus:

```python
# main.py v7
import ep_logging
import ep_wifi
import heater_http

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

http_server = heater_http.setup(wlan, logger_http)
http_server.start()
```

In diesem Teil wollen wir uns der Temperaturmessung widmen.

## Temperaturmessung mit DS18B20-Sensoren

Wer schon einmal vor dem Problem stand, mit einem Microcontroller Temperaturen messen zu müssen, kennt ihn wahrscheinlich: den DS18B20-Temperatursensor von Dallas. Er wird über den 1-Wire-Bus angesprochen. Das bedeutet, wir können mehrere Sensoren mit nur einem Pin am ESP32 auslesen. Auch die Beschaltung ist einfach: wir brauchen lediglich einen 4.7kOhm-PullUp-Widerstand an der Datenleitung. 

Damit ich das alles nicht frei-fliegend verdrahten muss, löte ich die Bauteile auf eine Platine auf. Ich habe dafür eine Lochrasterplatine mit Spannungsversorgung, Relais und einigen Steckern entworfen, die in ein wetterfestes Gehäuse passt. Wenn du also vorhast, dieses Tutorial nachzubauen und mich unterstützen willst könntest du ja eine meiner Platinen kaufen: [SolidCircuit HV3](https://www.eydam-prototyping.com/product/solidcircuit-hv3/).

Auf diese Platine löte ich zuerst den ESP32 auf und schließe ihn an die Spannungsversorgung an. Ich habe die Platine nicht speziell für dieses Projekt entworfen, sondern wollte so variabel wie möglich sein. Deswegen habe ich 3-8-polige JST-XH-Stecker vorgesehen, es spricht aber auch nichts dagegen, nur einen 3-poligen Stecker einzulöten. Für die DS18B20-Sensoren brauche ich ja nicht mehr.
Als nächstes kommen die Lötbrücken und der der PullUp-Widerstand. Ich schließe die Sensoren an GPIO4 an. Zum Testen habe ich mir an einen Sensor einen Stecker gekrimpt.

[Bild]

OK, das wars erst einmal mit dem Löten und Krimpen, jetzt kommt wieder Software. MicroPython wird bereits mit einem Modul zum Nutzen des 1-Wire-Busses ausgeliefert. Wir können es auf die Schnelle mal in der REPL ausprobieren. 

```python
>>> import onewire
>>> import ds18x20
>>> import machine
>>> ow = onewire.OneWire(machine.Pin(4))    # Bus initialisieren auf GPIO4
>>> ds = ds18x20.DS18X20(ow)
>>> roms = ds.scan()                        # nach angeschlossenen Slaves suchen
>>> roms
[bytearray(b'(!a\x85\x13\x19\x01\xb5')]     # Liste mit Slaves, hier nur einer
>>> import ubinascii
>>> ubinascii.hexlify(roms[0])              # die Seriennummer lesbar
b'28216185131901b5'
>>> ds.convert_temp()                       # allen angeschlossenen Slaves den Befehl zum messen geben
>>> ds.read_temp(roms[0])                   # Temperatur auslesen
22.625
```

Das hat ja schon mal ziemlich gut funktioniert. Der Nachteil daran, dass alle Sensoren an einem Pin hängen ist, dass ich anhand der Adresse wissen muss, welcher Sensor welche Temperatur misst. Und da die Adresse auf den Sensoren leider nicht draufsteht, brauchen wir eine Möglichkeit, um die Adressen den Messstellen zuzuordnen. Das schreit doch schon wieder nach einer Konfigurations-Webseite.

Im Prinzip wisst ihr schon, wie das geht. Wir brauchen wieder eine HTML-Datei, eine Konfigurationsdatei und eine neue Funktion, die für uns die angeschlossenen Sensoren ermittelt. Also los geht's. 

Die Konfigurationsdatei ist wieder eine JSON-Datei, diesmal mit dem Namen `ds_config.json`. Darin steht ein Dictionary, in der die Namen der Messstellen den Sensoren zugeordnet sind.

```json
# ds_config.json
{
    "T_Ofen": {
        "id": "28216185131901b5"
    }
}
```

In unserer `heater_http.py` ergänzen wir die Route für die neue Config-Datei und die Funktion zum auslesen der Sensoren. Achtung: setup bekommt `ds` als neuen Parameter:

```python
# heater_http.py v2

...

def setup(wlan, logger, ds):

    ...

    def scan_ds(ds):
        roms = ds.scan()
        return [{"id": ubinascii.hexlify(rom), "value": ds.read_temp(rom)} for rom in roms]

    ...

    

    crs_ds = ep_rest_server.config_rest_server(
        config_file="./ds_config.json",
        logger=logger
    )

    srs = ep_rest_server.sensor_rest_server(
        [
            ("^wifinets$", lambda path: scan_wifi(wlan)),
            ("^ds18b20$", lambda path: scan_ds(ds)),
            ("^reset$", lambda path: machine.reset()),
        ],
        logger=logger
    )

    routes = [
        ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
        ("^\/?rest/ds\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_ds.serve(sock, req)), 
        ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
        ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
    ]

```

In unserer `main.py` erzeugen wir das `ds`-Objekt. Achtung: die Sensoren führen die Messungen nur dann durch, wenn wir es ihnen sagen. Es wäre also sinnvoll, diese Messungen regelmäßig dirchzuführen. Dazu bieten sich Timer an:

```python
# main.py v8

...

import onewire
import ds18x20
import machine

...

ow = onewire.OneWire(machine.Pin(4))
ds = ds18x20.DS18X20(ow)

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: ds.convert_temp())

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()
```

Jetzt noch die HTML-Datei erstellen (siehe `ds_config.py`) und wir sollten unsere Sensoren zuordnen können:

[Bild]

