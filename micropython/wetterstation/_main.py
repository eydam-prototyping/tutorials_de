import network
import ujson
import time
import ubinascii
import machine
import BH1750
import math

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

with open("credentials.json", "r") as f:
    credentials = ujson.load(f)

# sort available wifis by rssi
nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True)  

# wifis, that are available and listed in credentials
nets = [x for x in nets if x[0].decode("ascii") in credentials["wifi"]]  

i = 0
ssid = ""
while not wlan.isconnected():
    i = i + 1 if i < len(nets)-1 else 0
    ssid = nets[i][0].decode("ascii")
    pwd = credentials["wifi"][ssid]
    bssid = nets[i][1]
    wlan.connect(ssid, pwd, bssid=bssid)
    retry = 0
    while (not wlan.isconnected()) and (retry < 5):
        time.sleep(2)
        retry += 1

print("connected to wifi " + ssid)

try:
    from umqtt.robust import MQTTClient
    import bme280
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    upip.install('micropython-bme280')
    from umqtt.robust import MQTTClient
    import bme280

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
bme = bme280.BME280(i2c=i2c)
bh = BH1750.BH1750(i2c)
adc = machine.ADC(0)

client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, "192.168.178.128", 1884)
client.connect()
time.sleep(5)
adc_mean = 0
try:
    while True:
        adc_min = 1024
        adc_max = 0
        adc_dev = 0
        for _ in range(10000):
            adc_val = adc.read()
            adc_mean = 0.9999 * adc_mean + 0.0001 * adc_val
            adc_dev = adc_dev + math.fabs(adc_mean-adc_val)
            adc_min = min([adc_val, adc_min])
            adc_max = max([adc_val, adc_max])
            time.sleep_ms(1)
        adc_dev /= 10000

        bme_data = bme.read_compensated_data()
        print(adc_min)
        print(adc_max)
        print(adc_mean)
        data = {
            "temperature": bme_data[0]/100,
            "humidity": bme_data[2]/1000,
            "pressure": bme_data[1]/256,
            "luminance": bh.luminance(BH1750.BH1750.ONCE_HIRES_1),
            "volume_mean": adc_dev,
            "volume_max": max([adc_mean-adc_min, adc_max-adc_mean]),
            "rssi": wlan.status("rssi")
        }
        print(ujson.dumps(data))
        client.publish('iot/wetterstation/werkstatt', ujson.dumps(data))
except:
    machine.reset()
