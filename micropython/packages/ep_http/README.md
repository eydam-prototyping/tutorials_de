# Eydam-Prototyping: ep_http

Simple Library to run a http-server on an ESP32 or other MicroPython-enabled device.
If you want to support my work, checkout my github repo.

## Usage

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

# Classes:

* `ep_http.http_server` is the main class, that listens to the port, handels incomming connections, parses the requests and forwards them to the corresponding routes. 
  * Most important parameter are the routes. Those are a list of 2 tuples, consisting of a regex-String and a function, that handels the request. The tuples are gone through one after another until a regex-String matches. 
* `ep_file_server.file_server` servers files.
* `ep_rest_server.config_rest_server` is a minimal REST-Server to edit config-files. Currently only a reduced set of instructions is supported.
* `ep_rest_server.sensor_rest_server` is also a minimal REST-Server, that accepts only GET-Requests. It is made to read sensor data.