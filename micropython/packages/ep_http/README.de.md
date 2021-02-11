# Eydam-Prototyping: ep_http

Eine Bibliothek, um auf einem ESP32 oder einem anderen MicroPython-fähigen Gerät einen kleinen http-Server zu starten.
Falls du mitarbeiten möchtest, schau mal in meinem Github-Repo vorbei.

## Nutzung

```python
# main.py

import ep_file_server
import ep_rest_server
import ep_http
import network
import time 
import ubinascii

wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("<SSID>", "<Password>")

while not wlan.isconnected():
    time.sleep(1)
print("Connected")

# just return files to client
fs = ep_file_server.file_server(
    html_dir="/html/",             # directory with files
    default_file="index.html"      # default file that is returned when no specific file is requested
)

# edit a json configuration file via rest api 
# currently supported: GET, PUT
crs = ep_rest_server.config_rest_server(
    config_file="./config.json"
)

# sensor reading for sensor_rest_server, must return json serializeable dict
def scan_wifi(path):
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

# return sensor reatings via rest api
# currently supported: GET
srs = ep_rest_server.sensor_rest_server(
    [
        ("^wifinets$", scan_wifi)   # assignment function <-> route
    ]
)

def default_route(sock, request):
    print("unhandled request")
    print(request)    

routes = [
    # files are available via http://<ip>/files/yourfile.html
    ("^\/?files\/([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: fs.serve(sock, req)),
    # configurations are available via http://<ip>/config/hierachy/of/json/file
    ("^\/?config\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs.serve(sock, req)),
    # sensor readings are available via http://<ip>/sensor/wifinets
    ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
    # favicon is forwarded to file server
    ("^(favicon\\.ico)$", lambda sock, req: fs.serve(sock, req)),
    # route, if nothing else matches
    ("^(.*)$", default_route),
]

s = ep_http.http_server(routes=routes, micropython_optimize=True)
print("Starting HTTP-Server: " + wlan.ifconfig()[0])
s.start()
```

# Klassen:

* `ep_http.http_server` ist die Hauptklasse, die am Port lauscht und die eingehenden Verbindungen bearbeitet (parst) und die Requests an die jeweiligen Routen weiterleitet. 
  * Wichtigster Parameter sind die Routen (`routes`). Sie sind eine Liste mit 2-Tupeln, bestehend aus einem Regex-String und einer Funktion, die den Socket und das geparste Request entgegen nimmt und damit irgendwas macht. Die Tupel werden von oben nach unten durchgegangen, bis ein Regex-String matcht. Die zugehörige Funktion wird dann aufgerufen.
* `ep_file_server.file_server` stellt Dateien bereit, die angefragt werden. Soll dein HTTP-Server nur HTML-Dateien anzeigen, dann bist du hier richtig
* `ep_rest_server.config_rest_server` ist ein minimaler REST-Server, mit dem Config-Dateien bearbeitet werden können. Aktuell hat er einen noch etwas eingeschränkten Funktionsumfang, aber einfache Anfragen funktionieren schon.
* `ep_rest_server.sensor_rest_server` ist ein REST-Server, der nur GET-Anfragen beantwortet. Hiermit sollen Sensoren ausgelesen werden.
