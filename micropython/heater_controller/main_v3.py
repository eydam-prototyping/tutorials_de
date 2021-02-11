# main.py #v3
import network
import time
import ep_logging
import ep_http
import ep_file_server

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# Set DHCP host name to recognize the device in your router
wlan.config(dhcp_hostname="Heater")
# Replace your SSID and password
wlan.connect("<SSID>", "<password>")

while not wlan.isconnected():
    time.sleep(1)

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

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