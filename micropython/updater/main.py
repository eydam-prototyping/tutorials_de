import ep_network
import os
import machine
import urequests
import ujson
import ep_updater

wlan = ep_network.connect_to_wifi()
#updater = ep_updater.updater()
#updater.run()

try:
    i = 1 / 0.0
except Exception as e:
    print(e)
