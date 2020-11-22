import network
import ujson
import time
import ubinascii
import machine

####################################
#                                  #
#         Connect to Wifi          #
#                                  #
####################################

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

####################################
#                                  #
#         Initialize MQTT          #
#                                  #
####################################

try:
    from umqtt.robust import MQTTClient
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    from umqtt.robust import MQTTClient

def connect_and_subscribe(client_id, broker_ip, broker_port, sub_callback=None, 
  sub_topics=[]):
    # Set Options for MQTT-Broker
    client = MQTTClient(client_id, broker_ip, broker_port)
    # Set callback to handel Messages
    if sub_callback is not None:
        client.set_callback(sub_callback)
    # Connect
    client.connect(clean_session=False)
    for topic in sub_topics:
        client.subscribe(topic)
    time.sleep(3)
    client.check_msg()
    return client

client_id = ubinascii.hexlify(machine.unique_id())

client = connect_and_subscribe(client_id, credentials["mqtt"]["host"], 
  credentials["mqtt"]["port"])

####################################
#                                  #
#        Initialize Sensors        #
#                                  #
####################################

#i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
#bme = bme280.BME280(i2c=i2c)
#bh = BH1750.BH1750(i2c)
#adc = machine.ADC(0)
mq = machine.ADC(machine.Pin(34))

####################################
#                                  #
#             Main Loop            #
#                                  #
####################################

while True:
    try:
        client.check_msg()

        data = {
            "mq": mq.read()
        }

        client.publish("iot/test/mq", ujson.dumps(data))
        time.sleep(5)

    except OSError:
        client = connect_and_subscribe(client_id, credentials["mqtt"]["host"], 
          credentials["mqtt"]["port"])



