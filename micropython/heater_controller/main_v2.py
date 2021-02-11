# main.py #v2
import network
import time
import ep_logging

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
