import network
import ujson
import time
import ubinascii
import machine
import BH1750
import math

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
    import bme280
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    upip.install('micropython-bme280')
    from umqtt.robust import MQTTClient
    import bme280

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

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
bme = bme280.BME280(i2c=i2c)
bh = BH1750.BH1750(i2c)
adc_sol = machine.ADC(machine.Pin(34))
adc_vol = machine.ADC(machine.Pin(33))
adc_vol_mean = 2048 
adc_wind = machine.ADC(machine.Pin(39))

def get_wind_dir(adc):
    wind_dir_dict = {
        3143: 0,
        1624: 22.5,
        1845: 45,
        335:  67.5,
        372:  90,
        264:  112.5,
        739:  135,
        506:  157.5,
        1149: 180,
        979:  202.5,
        2521: 225,
        2398: 247.5,
        3781: 270,
        3310: 292.5,
        3549: 315,
        2811: 337.5,
    }
    for key in wind_dir_dict:
        if key-18 < adc < key+18:
            return wind_dir_dict[key]
            
wind_speed = 0
rain = 0
def increment_counter(pin):
    print(pin)
    if str(pin) == "Pin(18)":
        global wind_speed
        wind_speed += 1
    elif str(pin) == "Pin(19)":
        global rain
        rain += 1
        
wind_speed_pin = machine.Pin(18, machine.Pin.IN)
wind_speed_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=increment_counter)

rain_pin = machine.Pin(19, machine.Pin.IN)
rain_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=increment_counter)

adc_sol = machine.ADC(machine.Pin(34))
adc_sol.atten(machine.ADC.ATTN_11DB)
####################################
#                                  #
#             Main Loop            #
#                                  #
####################################

while True:
    try:
        client.check_msg()

        bme_data = bme.read_compensated_data()

        v_sol = adc_sol.read()/4096.0*3.3
        i_sol = v_sol/22.0
        p_sol = v_sol*i_sol

        adc_vol_min = 4096  # Minimalwert der Spannung
        adc_vol_max = 0     # Maximalwert der Spannung
        adc_vol_dev = 0     # Mittlere Abweichung der Spannung vom Mittelwert
        for _ in range(10000):
            adc_vol_val = adc_vol.read()
            adc_vol_mean = 0.9999 * adc_vol_mean + 0.0001 * adc_vol_val
            adc_vol_dev = adc_vol_dev + math.fabs(adc_vol_mean-adc_vol_val)
            adc_vol_min = min([adc_vol_val, adc_vol_min])
            adc_vol_max = max([adc_vol_val, adc_vol_max])
            time.sleep_ms(1)
        adc_vol_dev /= 10000

        data = {
            "temperature": bme_data[0]/100,
            "humidity": bme_data[2]/1000,
            "pressure": bme_data[1]/256,
            "luminance": bh.luminance(BH1750.BH1750.ONCE_HIRES_1),
            "volume_mean": adc_vol_dev,
            "volume_max": max([adc_vol_mean-adc_vol_min, adc_vol_max-adc_vol_mean]),
            "wind_dir" : get_wind_dir(adc_wind.read()),
            "wind_speed": wind_speed,
            "solar": p_sol,
            "rain": rain,
            "rssi": wlan.status("rssi")
        }

        wind_speed = 0
        rain = 0

        client.publish("iot/werkstatt/wetter", ujson.dumps(data))
        print(ujson.dumps(data))

    except OSError:
        client = connect_and_subscribe(client_id, credentials["mqtt"]["host"], 
          credentials["mqtt"]["port"])



