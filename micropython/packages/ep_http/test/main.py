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
    
def default_route(sock, request):
    print("default")
    print(request)        

fs = ep_file_server.file_server(
    html_dir="/html/",
    default_file="rest.html"
)

crs = ep_rest_server.config_rest_server(
    config_file="./config.json"
)

def scan_wifi(path):
    print("Path: " + path)
    global wlan
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

srs = ep_rest_server.sensor_rest_server(
    [
        ("^wifinets$", scan_wifi)
    ]
)

routes = [
    ("^\/?files\/([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: fs.serve(sock, req)),
    ("^\/?rest\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs.serve(sock, req)),
    ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
    ("^(favicon\\.ico)$", lambda sock, req: fs.serve(sock, req)),
    ("^(.*)$", default_route),
]

s = ep_http.http_server(routes=routes, micropython_optimize=True, debug=True)
print("Starting HTTP-Server: " + wlan.ifconfig()[0])
s.start()