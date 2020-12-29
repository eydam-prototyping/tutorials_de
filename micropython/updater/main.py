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

def saveError(e):
    s = uio.StringIO()
    sys.print_exception(e, s)
    data = {
        "Name": type(e).__name__,
        "Text": e.args[0],
        "Time": "%04d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[0:6],
        "Trace": s.getvalue(),
        "Platform": sys.platform,
        "Version": sys.version,
        "ResetCause": machine.reset_cause(),
        "UniqueID": ubinascii.hexlify(machine.unique_id()),
        "StackUse": micropython.stack_use(),
        "Temperature": (esp32.raw_temperature()-32)*5/9,
        "Freq": machine.freq()
    }
    if "version.json" in uos.listdir():
        with open("version.json", "r") as f:
            version_info = ujson.load(f)
            data["FileVersionInfo"] = version_info

    with open("lastErr.json", "w") as f:
        ujson.dump(data, f) 
    print(ujson.dumps(data))

try:
    i = 1 / 0.0
except Exception as e:
    print("-----")
    saveError(e)
    print("-----")
    