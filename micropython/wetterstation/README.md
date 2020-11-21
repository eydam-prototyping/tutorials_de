# Wetterstation

In diesem Tutorial möchte ich zeigen, wie man mit einem SolidCircuit-HV3, einem ESP32 und einem Raspberry Pi eine Wetterstation bauen kann. Die Sensoren, die ich nutze, habe ich günstig bei Amazon gekauft. Um ein paar Halterungen herzustellen, habe ich einen 3D-Drucker verwendet. 

# Sensoren

![Sensoren](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/wetterstation/img/Sensoren_1.jpg)

Die typischen Messgrößen, die man bei einer Wetterstation aufnimmt, sind Temperatur, Luftfeuchtigkeit, Niederschlagsmenge, Windstärke, Windrichtung. Manchmal auch noch der Luftdruck. Ich will zusätzlich noch die Beleuchtungsstärke, Lautstärke und die Energie, die eine Solarzelle erzeugen würde, aufzeichnen.

* **Temperatur, Luftfeuchtigkeit, Luftdruck** will ich mit einem BME280-Sensor von Bosch messen. Diese gibt es auf einer kleinen Platine mit der nötigen Beschaltung ab ca. 5-6 Euro auf Amazon. Einfach nach BME280 suchen oder hier klicken: [Amazon](https://www.amazon.de/gp/product/B07FS95JXT/ref=ppx_yo_dt_b_asin_image_o01_s01?ie=UTF8&psc=1)
* **Niederschalgsmenge, Windstärke und Windrichtung** sind nicht ganz so günstig zu haben. Ich habe mir hier ein paar Bauteile auf Amazon rausgesucht. Messgeräte für [Niederschalgsmenge](https://www.amazon.de/gp/product/B00QDMBXUA/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1), [Windstärke](https://www.amazon.de/gp/product/B00QDMBQGG/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1) und [Windrichtung](https://www.amazon.de/gp/product/B00QDMBU80/ref=ppx_yo_dt_b_asin_image_o08_s00?ie=UTF8&psc=1) gibt es zusammen für ca. 60 Euro. Die Teile kommen aber aus China, deswegen sollte man sich hier auf ca. 3-4 Wochen Lieferzeit einstellen.
* **Beleuchtungsstärke** messe ich mit einem BH1750-Sensor. Diesen gibt es im 3er-Pack für ca. 8 Euro hier: [Amazon](https://www.amazon.de/gp/product/B07VF15XJJ/ref=ppx_yo_dt_b_asin_title_o01_s01?ie=UTF8&psc=1). Da ich diesen Sensor nicht einfach so dem Wetter aussetzen möchte, habe ich mir ein paar [Glaslinsen](https://www.amazon.de/gp/product/B07VF15XJJ/ref=ppx_yo_dt_b_asin_title_o01_s01?ie=UTF8&psc=1) bestellt, mit denen ich mir ein kleines Gehäuse bauen kann um den Sensor zu schützen.
* **Lautstärke** zu messen ist gar nicht so einfach und einen wirklich gut geeigneten fertigen Sensor habe ich auch nicht gefunden. Und viel Geld dafür ausgeben möchte ich auch nicht. Deswegen habe ich mir ein kleines [Mikrofon](https://www.amazon.de/gp/product/B07PXP8BQ7/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1) (3 Stück für 9 Euro) gekauft. Damit kann ich zwar keine Messwerte ermitteln die zu einer allgemein gültigen Skala passen, aber für Aussagen wie "um 15 Uhr ist es lauter als um 3 Uhr" reicht es allemal.

# Schaltung

# Software

In [diesem Tutorial](https://github.com/eydam-prototyping/tutorials_de/tree/master/raspberry_pi/smart_home_server) habe ich gezeigt, wie man sich eine kleine Smart-Home-Zentrale einrichten kann. Diese werden wir für dieses Tutorial nutzen. Wir werden mit dem ESP32 über das MQTT-Protokoll die Messwerte an den Raspberry Pi senden und sie dort mit Grafana darstellen.

In [diesem Tutorial](https://github.com/eydam-prototyping/tutorials_de/tree/master/micropython/ESP32_installation) habe ich gezeigt, wie man die Firmware auf dem ESP32 installiert. Das ist Voraussetzung für den Rest des Tutorials.

Zunächst müssen wir uns ins WLAN einloggen. Wie das geht, habe ich in [diesem Snippet](https://github.com/eydam-prototyping/tutorials_de/blob/master/snippets/micropython-wifi-login.md) erklärt. Hier kopiere ich den Code einfach:

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
>>> rshell -p COM5
Using buffer-size of 32
Connecting to COM5 (buffer-size 32)...
Trying to connect to REPL  connected
Testing if ubinascii.unhexlify exists ... Y
Retrieving root directories ... /boot.py/
Setting time ... Nov 21, 2020 15:26:22
Evaluating board_name ... pyboard
Retrieving time epoch ... Jan 01, 2000
Welcome to rshell. Use the exit command to exit rshell.

>>> cp ./micropython/wetterstation/credentials.json /pyboard
>>> cp ./micropython/wetterstation/main.py /pyboard
>>> ls -l /pyboard
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
I (0) cpu_start: App cpu up.
I (572) heap_init: Initializing. RAM available for dynamic allocation:
I (579) heap_init: At 3FFAFF10 len 000000F0 (0 KiB): DRAM
I (585) heap_init: At 3FFB6388 len 00001C78 (7 KiB): DRAM
I (591) heap_init: At 3FFB9A20 len 00004108 (16 KiB): DRAM
I (598) heap_init: At 3FFBDB5C len 00000004 (0 KiB): DRAM
I (604) heap_init: At 3FFCA9E8 len 00015618 (85 KiB): DRAM
I (610) heap_init: At 3FFE0440 len 00003AE0 (14 KiB): D/IRAM
I (616) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM
I (623) heap_init: At 4009DE28 len 000021D8 (8 KiB): IRAM
I (629) cpu_start: Pro cpu start user code
I (312) cpu_start: Starting scheduler on PRO CPU.
I (0) cpu_start: Starting scheduler on APP CPU.
I (130) wifi:wifi driver task: 3ffd10c8, prio:23, stack:3584, core=0
I (574) system_api: Base MAC address is not set, read default base MAC address from BLK0 of EFUSE
I (574) system_api: Base MAC address is not set, read default base MAC address from BLK0 of EFUSE
I (624) wifi:wifi firmware version: 44aa95c
I (624) wifi:config NVS flash: enabled
I (624) wifi:config nano formating: disabled
I (624) wifi:Init dynamic tx buffer num: 32
I (624) wifi:Init data frame dynamic rx buffer num: 32
I (634) wifi:Init management frame dynamic rx buffer num: 32
I (634) wifi:Init management short buffer num: 32
I (644) wifi:Init static rx buffer size: 1600
I (644) wifi:Init static rx buffer num: 10
I (644) wifi:Init dynamic rx buffer num: 32
I (744) phy: phy_version: 4180, cb3948e, Sep 12 2019, 16:39:13, 0, 0
I (744) wifi:mode : sta (3c:71:bf:96:f1:e8)
I (754) wifi: STA_START
I (2804) network: event 1
connecting to FRITZ!Box 7490
I (3014) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1
I (3864) wifi:state: init -> auth (b0)
I (3864) wifi:state: auth -> init (8a0)
I (3864) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1
I (3874) wifi: STA_DISCONNECTED, reason:202
authentication failed
I (5924) wifi: STA_DISCONNECTED, reason:205
I (6044) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1
I (6044) wifi:state: init -> auth (b0)
I (6054) wifi:state: auth -> init (8a0)
I (6054) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1
I (6054) wifi: STA_DISCONNECTED, reason:202
authentication failed
I (8114) wifi: STA_DISCONNECTED, reason:205
I (8234) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1
I (8234) wifi:state: init -> auth (b0)
I (8244) wifi:state: auth -> assoc (0)
I (8254) wifi:state: assoc -> run (10)
I (8284) wifi:connected with FRITZ!Box 7490, aid = 8, channel 1, BW20, bssid = e0:28:6d:d4:0a:5f
I (8284) wifi:security type: 3, phy: bgn, rssi: -61
I (8284) wifi:pm start, type: 1

I (8294) network: CONNECTED
I (8374) wifi:AP's beacon interval = 102400 us, DTIM period = 1
I (9054) event: sta ip: 192.168.178.45, mask: 255.255.255.0, gw: 192.168.178.1
I (9054) network: GOT_IP
connected to wifi FRITZ!Box 7490
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>> 
```

Es hat also funktioniert :)

Danach verbinde ich mich zum MQTT-Server. Dazu brauchen wir die Bibliothek "umqtt.robust". Einen Snippet, wie man die Bibliothek downloaden und einbinden kann, habe ich euch [hier]() gezeigt. Jetzt kopiere ich ihn einfach nur und erstelle einen MQTT-Client

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


