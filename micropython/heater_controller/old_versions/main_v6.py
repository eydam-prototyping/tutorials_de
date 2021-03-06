# main.py v6
import network
import time
import ep_logging
import ep_http
import ep_file_server
import ep_rest_server
import ubinascii
import machine
import ep_wifi

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

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

fs = ep_file_server.file_server(
    html_dir="/html/",
    default_file="index.html",
    logger=logger_http
)

crs_nw = ep_rest_server.config_rest_server(
    config_file="./network_config.json",
    logger=logger_http
)

srs = ep_rest_server.sensor_rest_server(
    [
        ("^wifinets$", lambda path: scan_wifi(wlan)),
        ("^reset$", lambda path: machine.reset()),
    ],
    logger=logger_http
)

routes = [
    ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
    ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
    ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
]

http_server = ep_http.http_server(routes=routes, micropython_optimize=True, logger=logger_http)
http_server.start()