# main.py #v2
import ep_logging
import ep_wifi
import heater_http
import onewire
import ds18x20
import machine

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

ow = onewire.OneWire(machine.Pin(4))
ds = ds18x20.DS18X20(ow)

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: ds.convert_temp())

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()