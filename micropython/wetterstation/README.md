# Wetterstation

In diesem Tutorial möchte ich zeigen, wie man mit einem SolidCircuit-HV3, einem ESP32 und einem Raspberry Pi eine Wetterstation bauen kann. Die Sensoren, die ich nutze, habe ich günstig bei Amazon gekauft. Um ein paar Halterungen herzustellen, habe ich einen 3D-Drucker verwendet. 

# Sensoren

![Sensoren](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/wetterstation/img/Sensoren_1.jpg)

Die typischen Messgrößen, die man bei einer Wetterstation aufnimmt, sind Temperatur, Luftfeuchtigkeit, Niederschlagsmenge, Windstärke, Windrichtung. Manchmal auch noch der Luftdruck. Ich will zusätzlich noch die Beleuchtungsstärke, Lautstärke und die Energie, die eine Solarzelle erzeugen würde, aufzeichnen.

* **Temperatur, Luftfeuchtigkeit, Luftdruck** will ich mit einem BME280-Sensor von Bosch messen. Diese gibt es auf einer kleinen Platine mit der nötigen Beschaltung ab ca. 5-6 Euro bei Amazon. Einfach nach BME280 suchen oder hier klicken: [Amazon](https://www.amazon.de/gp/product/B07FS95JXT/ref=ppx_yo_dt_b_asin_image_o01_s01?ie=UTF8&psc=1)
* **Niederschalgsmenge, Windstärke und Windrichtung** sind nicht ganz so günstig zu haben. Ich habe mir hier ein paar Bauteile auf Amazon rausgesucht. Messgeräte für [Niederschalgsmenge](https://www.amazon.de/gp/product/B00QDMBXUA/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1), [Windstärke](https://www.amazon.de/gp/product/B00QDMBQGG/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1) und [Windrichtung](https://www.amazon.de/gp/product/B00QDMBU80/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1) gibt es zusammen für ca. 60 Euro. Die Teile kommen aber aus China, deswegen sollte man sich hier auf ca. 3-4 Wochen Lieferzeit einstellen.
* **Beleuchtungsstärke** messe ich mit einem BH1750-Sensor. Diesen gibt es im 3er-Pack für ca. 8 Euro hier: [Amazon](https://www.amazon.de/gp/product/B07VF15XJJ/ref=ppx_yo_dt_b_asin_title_o01_s01?ie=UTF8&psc=1). Da ich diesen Sensor nicht einfach so dem Wetter aussetzen möchte, habe ich mir ein paar [Glaslinsen](https://www.amazon.de/gp/product/B07VF15XJJ/ref=ppx_yo_dt_b_asin_title_o01_s01?ie=UTF8&psc=1) bestellt, mit denen ich mir ein kleines Gehäuse bauen kann um den Sensor zu schützen.
* **Lautstärke** zu messen ist gar nicht so einfach und einen wirklich gut geeigneten fertigen Sensor habe ich auch nicht gefunden. Und viel Geld dafür ausgeben möchte ich auch nicht. Deswegen habe ich mir ein kleines [Mikrofon](https://www.amazon.de/gp/product/B07PXP8BQ7/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1) (3 Stück für 9 Euro) gekauft. Damit kann ich zwar keine Messwerte ermitteln die zu einer allgemein gültigen Skala passen (die Einheit dB an den Messwert zuhängen wäre falsch), aber für Aussagen wie "um 15 Uhr ist es lauter als um 3 Uhr" reicht es allemal.
* **Solarzellen** gibt es auch günstig bei Amazon. Da ich die Energie nicht nutzen möchte (das würde die Schaltung nur komplizierter machen und die Messung verfälschen, außerdem lohnt es sich nicht wirklich), sondern sie über einen Widerstand "verbrennen" möchte, sollte die Solarzelle möglichst klein sein.

# Schaltung

Die Schaltung, die ich verwende, habe ich euch hier aufgezeichnet:  

![PCB](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/wetterstation/img/wetterstation_Steckplatine.png)

Zuerst habe ich die Spannungsversorgungsleisten oben und unten durch setzen der Lötbrücken (unten links im Bild) aktiviert. Alternativ können hier auch Pinheader eingelötet werden, die mit Jumpern geschlossen werden. Das ist vor allem dann sinnvoll, wenn man Teile der Schaltung abschalten können möchte oder den Stromverbrauch messen möchte. In diesem Projekt brauche ich es allerdings nicht. 

Danach habe ich den ESP32 auf dem SolidCircuit-HV3 aufgelötet. Hier ist es vielleicht eine gute Idee, Pinheader zu verwenden. Wenn durch einen ungewollten Kurzschluss der ESP32 zerstört wird, müssen so nicht alle 38 Lötverbindungen getrennt werden, sondern nur eine Steckverbindung. Nicht vergessen, die 5V und GND-Verbindungsleitung zu setzen. Die 3.3V des ESP32 würde ich **nicht** mit den 3.3V des SolidCircuit verbinden, weil es (erstens) nicht nötig ist und (zweitens) haben wir so zwei getrennte 3.3V Versorgungsspannungen. Einmal für den ESP32 und einmal für alles andere. Sollte ein anderer Verbraucher plötzlich mehr Strom ziehen, stürzt der ESP32 nicht sofort ab.

Als nächstes kommen die Sensoren. Hier arbeite ich mich von links nach rechts durch:
* das **Mikrofon** braucht die 3.3V Versorgungsspannung, GND und gibt ein analoges Signal zurück. Weiter Beschaltung ist nicht nötig. 
* der **BME280** braucht auch 3.3V Versorgungsspannung, GND und er kommuniziert über den I2C-Bus. Für diesen Bus sind 2 4.7kOhm-Pull-Up-Widerstände nötig. Damit ist der erste Stecker voll.
* die Geräte am zweiten Stecker teilen sich eine GND-Leitung. Der **Regensensor** und der **Windstärkemesser** (Anemometer) bestehen intern einfach nur aus einem Reed-Kontakt. Hier müssen also nur Impulse gezählt werden. Dazu einfach einen 10kOhm-Pull-Up-Widerstand an die Signalleitung (welche der beiden ist egal) und die andere an GND. So liegt die Signalleitung bei geöffnetem Reed-Kontakt auf 3.3V und bei geschlossenem Reed-Kontakt auf GND.
* Die **Solarzelle** wird mit einem Kontakt (-) an GND verbunden und mit dem zweiten an einen Analog-Pin. Um die Solarzelle zu belasten (Leerlaufspannung ist nicht wirklich interessant), wird ein Widerstand parallel geschaltet. Wie groß er sein muss, ist gar nicht so leicht zu sagen, weil bei den billigen Solarzellen bei Amazon oftmals kein Datenblatt vorhanden ist. Bei meinen ist eine Spannung von 2V und ein Strom von 120mA angegeben. 2V/120mA=16,6Ohm, deswegen würde ich mal mit einem 22Ohm Widerstand im ersten Versuch starten. Der Widerstand muss mindestens für eine Leistung von 2V*120mA = 0.24W ausgelegt sein. Ggf. kann man hier zwei Widerstände parallel oder in Reihe schalten, um eine höhere Leistung zu erreichen.
* Den **Beleuchtungsmesser** baue ich neben die Solarzelle. Er wird auch über I2C angebunden.
* Der **Windrichtungssensor** besteht aus 8 Reed-Kontakten und 8 unterschiedlich großen Widerständen. Je nachdem, welche Kontakte geschlossen sind, ergibt sich ein anderer Gesamtwiderstand. Daraus kann dann die Windrichtung geschlossen werden.

Hier nocheinmal die Schaltung als Schaltplan, da es auf dem SolidCircuit doch etwas voll geworden ist.

![Schematic](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/wetterstation/img/wetterstation_Schaltplan.png)

# Software

In [diesem Tutorial](https://github.com/eydam-prototyping/tutorials_de/tree/master/raspberry_pi/smart_home_server) habe ich gezeigt, wie man sich eine kleine Smart-Home-Zentrale einrichten kann. Diese werde ich für dieses Tutorial nutzen. Ich werde mit dem ESP32 über das MQTT-Protokoll die Messwerte an den Raspberry Pi senden und sie dort mit Grafana darstellen.

In [diesem Tutorial](https://github.com/eydam-prototyping/tutorials_de/tree/master/micropython/ESP32_installation) habe ich gezeigt, wie man die Firmware auf dem ESP32 installiert. Das ist Voraussetzung für den Rest des Tutorials.

## WiFi
Zunächst muss ich mich ins WLAN einloggen. Wie das geht, habe ich in [diesem Snippet](https://github.com/eydam-prototyping/tutorials_de/blob/master/snippets/micropython-wifi-login.md) erklärt. Hier kopiere ich den Code einfach:

```python
# main.py
import network
import ujson
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True) 

with open("credentials.json", "r") as f:
    credentials = ujson.load(f)

nets = [x for x in nets if x[0].decode("ascii") in credentials["wifi"]]  

i = -1
ssid = ""
while not wlan.isconnected():
    i = i + 1 if i < len(nets)-1 else 0
    ssid = nets[i][0].decode("ascii")
    pwd = credentials["wifi"][ssid]
    bssid = nets[i][1]
    print("connecting to " + ssid)
    wlan.connect(ssid, pwd, bssid=bssid)
    retry = 0
    while (not wlan.isconnected()) and (retry < 5): 
        time.sleep(2)
        retry += 1

print("connected to wifi " + ssid)
```

Um auszuprobieren, ob das auch alles funktioniert, kopiere ich die Dateien `credentials.json` ([siehe Snippet](https://github.com/eydam-prototyping/tutorials_de/blob/master/snippets/micropython-wifi-login.md)) und `main.py` mit Hilfe von `rshell` auf den ESP32:

```shell
> rshell -p COM5
Using buffer-size of 32
Connecting to COM5 (buffer-size 32)...
Trying to connect to REPL  connected
Testing if ubinascii.unhexlify exists ... Y
Retrieving root directories ... /boot.py/
Setting time ... Nov 21, 2020 15:26:22
Evaluating board_name ... pyboard
Retrieving time epoch ... Jan 01, 2000
Welcome to rshell. Use the exit command to exit rshell.

> cp ./micropython/wetterstation/credentials.json /pyboard
> cp ./micropython/wetterstation/main.py /pyboard
> ls -l /pyboard
   139 Jan  1 2000  boot.py
   216 Nov 21 15:28 credentials.json
   690 Nov 21 15:28 main.py
```

Wenn ich dann die REPL starte und den ESP32 neu starte (Reset-Knopf), dann bekomme ich folgende Ausgabe:
```shell
repl
Entering REPL. Use Control-X to exit.
>
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.

 [RESET-Button]

>>> ets Jun  8 2016 00:22:57

rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:2
load:0x3fff0018,len:4
load:0x3fff001c,len:5008
ho 0 tail 12 room 4
load:0x40078000,len:10600
ho 0 tail 12 room 4
load:0x40080400,len:5684
entry 0x400806bc
I (548) cpu_start: Pro cpu up.
I (548) cpu_start: Application information:
I (548) cpu_start: Compile time:     Sep  2 2020 03:00:08
I (551) cpu_start: ELF file SHA256:  0000000000000000...
I (557) cpu_start: ESP-IDF:          v3.3.2
I (562) cpu_start: Starting app cpu, entry point is 0x40082f30

...

I (8294) network: CONNECTED
I (8374) wifi:AP's beacon interval = 102400 us, DTIM period = 1
I (9054) event: sta ip: 192.168.178.45, mask: 255.255.255.0, gw: 192.168.178.1
I (9054) network: GOT_IP
connected to wifi FRITZ!Box 7490
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>> 
```

Es hat also funktioniert.

## MQTT

Danach verbinde ich mich zum MQTT-Server. Dazu brauchen wir die Bibliothek "umqtt.robust". Einen Snippet, wie man die Bibliothek downloaden und einbinden kann, habe ich euch [hier](https://github.com/eydam-prototyping/tutorials_de/blob/master/snippets/micropython-upip.md) gezeigt. Jetzt kopiere ich ihn einfach nur und erstelle einen MQTT-Client.

```python
# main.py
...
print("connected to wifi " + ssid)

try:
    from umqtt.robust import MQTTClient
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    from umqtt.robust import MQTTClient

import ubinascii
import machine

client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, "192.168.178.128", 1883)
client.connect()
```

[hier kommt noch was]

## Lautstärke messen

Um die Lautstärke zu messen, habe ich mir folgendes überlegt: 
* das Mikrofon gibt ein analoges Signal aus (Auslenkung der Membran), das um einen Mittelwert schwingt. Ein leises Signal ist eine kleine Änderung des Mittelwerts, ein lautes Signal ist eine große Änderung. 
* der Mittelwert ist nicht konstant. Ich habe festgestellt, dass sich der Mittelwert ändert. Woran das liegt, weiß ich nicht genau. Ich vermute, es hängt mit dem Luftdruck zusammen. Das muss ich in meiner Berechnung berücksichtigen.
* ich habe mich dazu entschlossen, den Wert des Analogsignals jede Millisekunde zu messen (`adc_val`). Der Mittelwert (`adc_mean`) ist der Durchschnitt des Analogsignals. Ich will alle 10 Sekunden einen Messwert bilden, was bedeuten würde, ich muss 10s/1ms = 10.000 Messwerte zwischenspeichern. Da mir das zuviel Speicher verbraucht, berechne ich den Mittelwert mit dem EWMA-Filter (Exponentially Weighted Moving Average). Die Überlegung dahinter: der Mittelwert berechnet sich zu 99.99% aus dem alten Mittelwert und zu 0.01% aus dem gerade gemessenen Wert. Also: 
```python
adc_mean = 0.9999 * adc_mean + 0.0001 * adc_val
```
* wie der EWMA-Filter funktioniert, habe ich im Jupyter-Notebook "EWMA-Filter" erklärt.
