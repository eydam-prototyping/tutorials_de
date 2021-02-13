# main.py v9
import ep_logging
import ep_wifi
import ep_config
import heater_http
import onewire
import ds18x20
import machine
import ubinascii
import statemachine

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

ow = onewire.OneWire(machine.Pin(4))
ds = ds18x20.DS18X20(ow)

ht_config = ep_config.config("ht_config.json")
ht_config.load()
thresh = ht_config.get("")

ds_config = ep_config.config("ds_config.json")
ds_config.load()
temps = ds_config.get("")

sm = statemachine.setup(
    lambda name: temps[name]["value"] if (name in temps) and ("value" in temps[name]) else 0,
    lambda name: thresh.get(name, 0)
)
sm.init()
sm.step_until_stationary()

def read_temps(timer, ds, temps, sm):
    ds.convert_temp()
    for key in temps:
        temps[key]["value"] = ds.read_temp(ubinascii.unhexlify(temps[key]["id"]))
    sm.step()

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: read_temps(timer, ds, temps, sm))

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()