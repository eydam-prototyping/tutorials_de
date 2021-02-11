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
# main.py #v1
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.config(dhcp_hostname="Heater")
# Replace your SSID and password
wlan.connect("<SSID>", "<password>")

while not wlan.isconnected():
    time.sleep(1)

wlan.active(True)
# Set DHCP host name to recognize the device in your router

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

In der `main.py` importieren wir dann das Modul, initialisieren den Logger und ersetzen die `print`-Ausgabe. Jetzt initialiseren wir den Logger als `colored_logger`, ersetzen ihn aber später als `syslog_logger`. Das können wir aber erst mit bestehender Netzwerkverbindung machen. Deswegen erfolgt das Initialisieren erst nach dem Verbinden mit dem Netzwerk:

```python
# main.py #2

...

import ep_logging

...

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

```

Wir werden hier später noch einiges ändern, für jetzt soll es aber erst einmal ausreichen. Weiter geht es mit dem HTTP-Server.

## HTTP-Server zum konfigurieren


