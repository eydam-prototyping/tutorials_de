# Mit einem ESP32/ESP8266 und Micropython ins WiFi einloggen

Da ich viel unterwegs bin und ab und zu auch mal von unterwegs aus entwickle, muss ich meine Geräte immer wieder in unterschiedliche WiFi-Netze einloggen. Da ich nicht ständig neue Login-Daten eingeben möchte, habe ich mir ein kleines Script gebastelt, was schaut, welches Netz verfügbar ist und dann versucht, sich dort einzuloggen. 
Ein weiteres Feature: Wenn mehrere WiFi's mit dem gleichen Namen gefunden werden, wird versucht, sich zuerst mit dem WiFi mit dem stärksten Signal zu verbinden.

Zunächst den WiFi-Treiber aktivieren und nach verfügbaren Netzen suchen. Die Netze werden nach Signalstärke sortiert:
```python
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True) 
```

Die bekannten Wifi-Netze werden in `credentials.json` gespeichert:
```json
{
    "wifi": {
        "ssid1": "password1",
        "ssid2": "password2"
    }
}
```

Diese Datei wird dann geladen:
```python
import ujson

with open("credentials.json", "r") as f:
    credentials = ujson.load(f)
```

Dann wird geschaut, für welches der gefundenen Netze auch ein Passwort vorhanden ist. Achtung: die SSID ist noch ein Binary-String und muss zum Vergleichen decodiert werden:
```python
nets = [x for x in nets if x[0].decode("ascii") in credentials["wifi"]]  
```

`nets` ist jetzt eine Liste mit den Netzen, für die ein Passwort vorhanden ist. Als nächstes wird solange versucht sich zu verbinden, bis es bei einem der Netze funktioniert:

```python
i = -1       # Zählvariable
ssid = ""   # WiFi, zu dem man sich verbinden konnte
while not wlan.isconnected():
    i = i + 1 if i < len(nets)-1 else 0
    ssid = nets[i][0].decode("ascii")
    pwd = credentials["wifi"][ssid]
    bssid = nets[i][1]
    wlan.connect(ssid, pwd, bssid=bssid)
    retry = 0
    # etwas Zeit zum Verbinden gewähren
    while (not wlan.isconnected()) and (retry < 5): 
        time.sleep(2)
        retry += 1

print("connected to wifi " + ssid)
```

Sollte es nicht möglich sein, sich zu einem Netz zu verbinden, bleibt das Script in einer Endlosschleife.

Hier der komplette Code:

```python
import network
import ujson

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
    wlan.connect(ssid, pwd, bssid=bssid)
    retry = 0
    while (not wlan.isconnected()) and (retry < 5): 
        time.sleep(2)
        retry += 1

print("connected to wifi " + ssid)
```
