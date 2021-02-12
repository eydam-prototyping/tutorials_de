# Heizungssteuerung mit dem ESP32

Die Steuerung meiner Heizung ist schon ziemlich alt und bevor sie komplett ausfällt, dachte ich, ich baue mir eine eigene Steuerung, die ich selbst warten und im Notfall auch selbst reparieren kann. Ich habe die Steuerung schon vor langer Zeit auf einen Raspberry Pi umgestellt. Dieser ist nun schon in die Jahre gekommen und für so eine simple Aufgabe eigentlich überdimensioniert. Deshalb möchte ich die Steuerung auf einen ESP32 umstellen. Ehrlich gesagt spricht auch nichts dagegen, den Raspberry Pi noch weiter zu nutzen, aber ich habe Spaß am basteln und brauche mal wieder ein neues Projekt.

Hier mal die Anforderungsliste an die neue Steuerung:
* ESP32 als Controller
* MicroPython als Programmiersprache. Ich hab in der letzten Zeit schon einiges an Erfahrung damit sammeln können und bin echt begeistert.
* Temperaturen werden mit dem DS18B20 gemessen. Er ist günstig, genau und ich habe schon einges an Erfahrung damit gesammelt.
* LCD-Display zum anzeigen aktueller Werte
* Weboberfläche zum konfigurieren
* Daten senden per MQTT

Ich möchte die Hardware Schritt für Schritt aufbauen, so wie ich die Software dazu programmiere. Deswegen fange ich zuerst einmal mit den Dingen an, für die ich keine weitere Hardware brauche, außer den ESP32 an sich. Also beginne ich mit der Installation von MicroPython auf dem ESP32, der WiFi-Verbindung und dann der Weboberfläche.

## Installation von MicroPython

Wie man MicroPython und die benötigten Tools auf dem (Windows) PC installiert, habe ich bereits in [diesem Tutorial beschrieben.](https://github.com/eydam-prototyping/tutorials_de/tree/master/micropython/ESP32_installation). Deswegen hier nur kurz die Schritte zusammengefasst:

Nachdem die Tools auf dem PC installiert sind, löschen wir den Flash des ESP32:

```shell
> esptool.py --port COM5 erase_flash
```

und flashen danach das aktuelle MicroPython-Image auf den ESP32:

```shell
> esptool.py --chip esp32 --port COM5 write_flash -z 0x1000 ./esp32-idf4-20200902-v1.13.bin
```

Zum testen, ob das auch wirklich funktioniert hat, verbinden wir uns mir `rshell` mit dem ESP32:

```shell
> rshell -p COM5
Using buffer-size of 32
Connecting to COM5 (buffer-size 32)...
Trying to connect to REPL . connected
Testing if ubinascii.unhexlify exists ... Y
Retrieving root directories ... /boot.py/
Setting time ... Feb 11, 2021 22:00:58
Evaluating board_name ... pyboard
Retrieving time epoch ... Jan 01, 2000
Welcome to rshell. Use the exit command to exit rshell.
```

Wenn eure Ausgabe ungefähr so aussieht und kein Fehler angezeigt wird, hat alles funktioniert.

## WiFi-Verbindung

Nun, da MicroPython installiert ist, können wir mit dem eigentlichen programmieren anfangen.

Wir legen die Datei `main.py` an. Ich erweitere diese Datei hier Schritt für Schritt. Damit du die einzelnen Schritte nachvollziehen kannst, ergänze ich die Version im Dateinamen. Die erste Version nenne ich also `main_v1.py`, sie muss aber `main.py` heißen, es funktioniert.

Und noch ein Hinweis: Meine Kommentare im Code sind auf Englisch, damit ich das Tutorial später leichter ins Englische übersetzen kann.

```python
# main.py v1
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# Set DHCP host name to recognize the device in your router
wlan.config(dhcp_hostname="Heater")
# Replace your SSID and password
wlan.connect("<SSID>", "<password>")

while not wlan.isconnected():
    time.sleep(1)

print("WiFi connected")
```

Diese Datei kopieren wir auf den ESP32 mit (`rshell` läuft noch), wechseln in die REPL und starten den ESP32 dann mit STRG+D neu:

```shell
> cp main.py /pyboard
> repl
[CTRL+D]
MPY: soft reboot
Wifi connected
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>>
```

Ich habe mir ein kleines Logger-Modul geschrieben, mit dem ich Log-Ausgaben komfortabler anzeigen und sie später auch an einen SYSLOG-Server senden lassen kann. Dieses Modul kannst du dir [hier](https://github.com/eydam-prototyping/tutorials_de/tree/master/micropython/packages/ep_logging) herunterladen und dananch auf den ESP32 kopieren.

```shell
> cp ep_logging.py /pyboard
```

Alternativ kannst du sie auch mit `upip` installieren. Dazu musst dein ESP32 mit dem Internet verbunden sein. Dann kannst du die REPL starten und folgendes eingeben:

```python
import upip
upip.install("micropython-eydam-prototyping-logging")
```

In der `main.py` importieren wir dann das Modul, initialisieren den Logger und ersetzen die `print`-Ausgabe. Jetzt initialiseren wir den Logger als `colored_logger`, ersetzen ihn aber später als `syslog_logger`. Das können wir aber erst mit bestehender Netzwerkverbindung machen. Deswegen erfolgt das Initialisieren erst nach dem Verbinden mit dem Netzwerk:

```python
# main.py v2

...

import ep_logging

...

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

```

Wir werden hier später noch einiges ändern, für jetzt soll es aber erst einmal ausreichen. Weiter geht es mit dem HTTP-Server.

## HTTP-Server zum konfigurieren

Damit der ESP32 eine Weboberfläche bekommt, muss er auf Anfragen, die standardmäßig auf Port 80 ankommen, antworten. Wie das grundsätzlich funktioniert, habe ich [hier](https://www.eydam-prototyping.com/2021/01/12/micropython-wifi-konfigurieren-mit-einfachem-http-server/) beschrieben. Ich habe diese Funktionalität noch einmal erweitert und in einem weiteren Modul zusammengefasst, dass du dir [hier](https://github.com/eydam-prototyping/tutorials_de/tree/master/micropython/packages/ep_http) herunterladen kannst. Alternativ kannst du wieder `upip` verwenden. Zusätzlich brauchst du noch das Modul `ep_config`. Also:

```python
import upip
upip.install("micropython-eydam-prototyping-config")
upip.install("micropython-eydam-prototyping-ep-http")
```

Damit wir auch etwas zum Anzeigen haben, erstellen wir uns die Datei `index.html` im Ordner `html` mit folgendem Inhalt:

```html
<!-- index.html -->
<html>
    <head>
        <title>Heater Controller</title>
    </head>
    <body>
        <h1>Hello World</h1>
    </body>
</html>
```

Und kopieren sie uns schon mal auf den ESP32:

```shell
> mkdir /pyboard/html
> cp /html/index.html /pyboard/html
```

Damit der ESP32 sie auch anzeigt, ergänzen wir die Datei `main.py` um folgenden Inhalt:

```python
# main.py v3

...

import ep_http
import ep_file_server

...

logger_http = ep_logging.colored_logger(appname="http")

fs = ep_file_server.file_server(
    html_dir="/html/",
    default_file="index.html",
    logger=logger_http
)

routes = [
    ("^(.*)$", lambda sock, req: fs.serve(sock, req)),  # every route is forwarded to file server
]

http_server = ep_http.http_server(routes=routes, micropython_optimize=True, logger=logger_http)
http_server.start()
```

Wenn wir den ESP32 jetzt neu starten und seine IP-Adresse in den Browser eingeben, sollten wir den Schriftzug "Hello World" angezeigt bekommen. Die IP-Adresse bekommen wir über unseren Router heraus, oder wir lassen sie uns anzeigen mit dem Befehl:

```python
wlan.ifconfig()
```

Was passiert hier? Der `http_server` lauscht auf Port 80 (Standard für HTTP) und nimmt die Anfrage entgegen. Dann parst er die empfangenen Daten und schaut die Routen von oben nach unten durch und übergibt die Anfrage an die Reoute, die passt. Der Regex-String `^(.*)$` bedeutet: Anfang des Strings (`^`) - dann irgendein Zeichen (`.`) belibig oft (`*`) - Ende des Strings (`$`). Es wird also jede Anfrage an den `file_server` weitergeleitet. Dieser schaut dann, ob die angefragte Datei vorhanden ist und gibt sie zurück, falls möglich.

Wie bereits erwähnt, wollen wir aber auch Konfigurationen vornehmen und müssen dazu Dateien verändern können. Dafür habe ich eine mini-REST-Server gebaut, mit dem du Config-Dateien bearbeiten kannst. Dafür brauchst du zunächst mal eine Config-Datei im json-Format. Wir erstellen uns die Datei `network_config.json`:

```json
// network_config.json
{
    "wifi_config": {
        "ap_ssid": "ESP32",
        "ap_pass": "eydam-protoyping",
        "dhcp_hostname": "ESP32"
    },
    "wifi_nets": [
        {
            "ssid": "ssid1",
            "pass": "pass1"
        },
        {
            "ssid": "ssid2",
            "pass": "pass2"
        }
    ]
}
```

Und kopieren sie auf den ESP32.

Wir könnten hier auch etwas anderes reinschreiben. Dem dem Rest-Server ist das egal. Ich nutze diese Datei aber später, um daraus direkt die WiFi-Einstellungen zu laden. Wenn ihr das nicht machen wollt, kann eure Datei auch anders aussehen.

Im erstem Block (`wifi_config`) machen wir generelle WiFi-Einstellungen. Unter welchem namen der ESP im Router auftaucht und falls wir uns nicht mit einem bestehenden WiFi verbinden können, wie unser Access-Point heißen soll und welches Passwort er haben soll. 

Im zweiten Block (`wifi_nets`) haben wir eine Liste mit SSIDs und Passwörtern, mit denen wir uns verbinden können. Falls ein Netz mal ausfällt, können wir uns mit einem anderen verbinden.

Diese Datei wollen wir jetzt über den Webbrowser bearbeiten können. Dazu fügen wir die neue Route hinzu:

```python
# main.py v4

...

import ep_rest_server

...

crs_nw = ep_rest_server.config_rest_server(
    config_file="./network_config.json",
    logger=logger_http
)

routes = [
    ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
    ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
]

...

```

Wir können uns den Inhalt der Datei jetzt schon anzeigen lassen, indem wir die IP-Adresse des ESP32 in den Webbrowser eingeben, gefolgt von `/rest/nw`.

Das bearbeiten machen wir in einer neuen HTML-Seite, die wir `nw_config.html` nennen. Du kannst dir den Inhalt der Datei `nw_config_v1.html` kopieren und sie dann auf den ESP32 in den Ordner `html` kopieren. Hierin ist nur HTML und Javascript. Die Erklärungen dazu würde ich mal überspringen. 

Jedenfalls, wenn du jetzt alles auf den ESP32 kopierst, ihn neu startest und die Seite `http://<ip-des-ESP32>/nw_config.html` besuchst, solltest du eine Webseite angezeigt bekommen, die kurz nach dem laden die Config-Datei nachlädt. Wenn du auf dieser Seite Änderungen machst und unten auf den Button "Speichern" klickst, erscheint unter dem Button die Nachricht "OK" und zeigt damit an, dass die Daten auf dem ESP32 gespeichert wurden. Wenn du die Seite aktualisierst, sollten die geänderten Daten erscheinen. In der Tabelle WiFi-Netze gibt es die Spalte BSSID. Die kannst du jetzt erstmal ignorieren.

Es wäre ja jetzt noch komfortabel, wenn wir uns die verfügbaren WiFi-Netze anzeigen lassen können. Dafür habe ich das Modul `sensor_rest_server` vorgesehen. Ich habe es eigentlich vorgesehen, um Sensoren auszulesen. Aber man kann das WiFi-Modul ja auch irgendwie als Sensor betrachten. Um es zu nutzen erweitere die Datei `main.py` folgendermaßen:

```python
# main.py v5
...

import ubinascii

...

def scan_wifi(wlan):
    nets = wlan.scan()
    result = []
    for ssid, bssid, channel, rssi, authmode, hidden in nets:
        net = {
            "ssid": ssid.decode("ascii"),
            "bssid": ubinascii.hexlify(bssid).upper(),
            "channel": channel,
            "rssi": rssi,
            "authmode": authmode,
            "hidden": hidden
        }
        result.append(net)
    return result

...

srs = ep_rest_server.sensor_rest_server(
    [
        ("^wifinets$", lambda path: scan_wifi(wlan)),
    ],
    logger=logger_http
)

routes = [
    ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
    ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
    ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
]

```

Der `sensor_rest_server` führt Funktionen aus, die ihm übergeben werden. Wenn wir ihm also eine Liste mit Regex-Strings und den dazugehörigen Funktionen geben (die Funktionen müssen ein Objekt zurück geben, was sich in einen JSON-String überführen lässt), dann können wir die Funktionen vom Webbrowser aus aufrufen und uns das Ergebnis anschauen. Wenn du jetzt also `http://<ip-des-ESP32>/sensor/wifinets` in die Adresszeile eingibtst, solltest du eine Liste mit den Verfügbaren WiFi-Netzen bekommen. Hinweis: Ich muss meinen ESP32 manchmal über den Reset-Button neu starten, damit ich ein Ergebnis bekomme.

Wir brauchen jetzt nur unsere `nw_config.html` anpassen, damit wir uns die Netze anzeigen lassen können (siehe `nw_config_v2.html`).
Meine Seite sieht jetzt so aus:
![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/nw_config_1.png "nw_config.html")
Probier mal aus, ob alles funktioniert.

Jetzt bekommt die Spalte BSSID auch eine Bedeutung. Damit können wir unser WiFi-Netz eindeutig identifizieren, falls wir mehrere mit dem gleichen Namen haben sollten. Du kannst also bestimmen, mit welchem AccessPoint genau sich dein ESP32 verbinden soll. Wenn du die Zelle leer lässt, wird der AccessPoint mit dem stärksten Signal verwendet.

Damit wir die so erstellte Konfiguration auch nutzen, nehmen wir zum verbinden mit dem WiFi mein Modul `ep_wifi` (Installieren wieder mit `upip.install("micropython-eydam-prototyping-wifi")`). Diesem Modul kannst du die Config-Datei übergeben. Das Modul probiert dann Netz für Netz durch, bis es es sich mit einem Verbinden konnte. Falls keines gefunden werden konnte, wird ein neues Netz aufgemacht, mit dem du dich dann verbinden kannst und den ESP32 so konfigurieren kannst.

Achso, wir können den ESP32 über diesen `sensor_rest_server` auch neustarten. Das habe ich in diesen Schritt mal mit eingebaut:

```python
# main.py v6

...

import machine
import ep_wifi

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()
...

srs = ep_rest_server.sensor_rest_server(
    [
        ("^wifinets$", lambda path: scan_wifi(wlan)),
        ("^reset$", lambda path: machine.reset()),      # zum neustarten
    ],
    logger=logger_http
)

```

Wenn du jetzt `http://<ip-des-ESP32>/sensor/reset` aufrufst, dann bekommst du keine Seite zurückgegeben, sondern der ESP32 startet neu.

So, Zeit für eine kurze Pause. Weiter gehts dann im nächsten Kapitel. Du kannst ja als kleine Hausaufgabe die Webseiten ein bisschen schöner gestalten. Ein bisschen CSS und das ganze sieht viel besser aus.