import ep_network
import os
import machine
import urequests
import ujson
import ep_updater
import utime
import sys
import uio
import micropython
import esp32
import ubinascii
import uos

wlan = ep_network.connect_to_wifi()
updater = ep_updater.updater()
updater.run()

try:
    i = 1 / 0.0
except Exception as e:
    ep_updater.saveError(e)
    