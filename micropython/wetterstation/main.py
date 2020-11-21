import network
import ujson
import time
import ubinascii
import machine

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True) 

with open("credentials.json", "r") as f:
    credentials = ujson.load(f)

nets = [x for x in nets if x[0].decode("ascii") in credentials["wifi"]]  

i = -1
ssid = ""
while not wlan.isconnected():
    i = i + 1 if i < len(nets)-1 else 0
    ssid = nets[i][0].decode("ascii")
    pwd = credentials["wifi"][ssid]
    bssid = nets[i][1]
    print("connecting to " + ssid)
    wlan.connect(ssid, pwd, bssid=bssid)
    retry = 0
    while (not wlan.isconnected()) and (retry < 5): 
        time.sleep(2)
        retry += 1

print("connected to wifi " + ssid)

try:
    from umqtt.robust import MQTTClient
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    from umqtt.robust import MQTTClient

client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, "192.168.178.128", 1883)
client.connect()



