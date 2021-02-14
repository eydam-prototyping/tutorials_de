# main.py v10
import ep_logging
import ep_wifi
import ep_config
import heater_http
import onewire
import ds18x20
import machine
import ubinascii
import statemachine
import menu
import mqtt
import gc
import _thread
import json
gc.collect()

_thread.stack_size(8192)

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()
ip = wlan.ifconfig()[0]

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
get_temp = lambda name: temps[name]["value"] if (name in temps) and ("value" in temps[name]) else 0
sm, pump_state = statemachine.setup(
    get_temp,
    lambda name: thresh.get(name, 0)
)
sm.init()
sm.step_until_stationary()

def read_temps(timer, ds, temps, sm):
    ds.convert_temp()
    for key in temps:
        temps[key]["value"] = ds.read_temp(ubinascii.unhexlify(temps[key]["id"]))
    sm.step()
    mqtt_publish()
    gc.collect()

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: read_temps(timer, ds, temps, sm))

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()

m = menu.setup(get_temp, sm)
m.display_funcs["print_ssid"] = lambda: "{}".format(ssid)
m.display_funcs["print_ip"] = lambda: "{}".format(ip)
m.display_funcs["print_rssi"] = lambda: "{} db".format(wlan.status("rssi")) if wlan.isconnected() else "---"

nw_config = ep_config.config("network_config.json")
nw_config.load()

mqtt_client = mqtt.setup(nw_config.get("mqtt_config/mqtt_host"), nw_config.get("mqtt_config/mqtt_port"))

def mqtt_publish():
    gc.collect()
    data = {key: temps[key]["value"] for key in temps}
    data["Pump"] = pump_state()
    data["State"] = sm.state
    data["FreeRAM"] = gc.mem_free()
    data["RSSI"] = wlan.status("rssi")
    
    s_data = json.dumps(data)
    try:
        mqtt_client.publish(s_data, nw_config.get("mqtt_config/mqtt_topic"))
        logger.debug(s_data)
    except:
        logger.error("Could not send MQTT Data")
    