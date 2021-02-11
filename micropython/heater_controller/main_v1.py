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