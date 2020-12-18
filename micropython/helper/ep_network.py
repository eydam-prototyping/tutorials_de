import network
import ujson
import time
import machine
import ubinascii

def connect_to_wifi():
    """Connects to a wifi-network. There must be a credentials.json-file with SSID and PASS. See 
    https://github.com/eydam-prototyping/tutorials_de/blob/master/snippets/micropython-wifi-login.md
    for details.

    Returns:
        network.WLAN-Object
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # sort available networks by ssid
    nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True) 

    with open("credentials.json", "r") as f:
        credentials = ujson.load(f)

    # only nets, that are available in credentials.json
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

    return wlan


def connect_and_subscribe(sub_callback=None):
    """Connectes to MQTT-Host and subscribes to topics. MQTT-IP, -Port and Topics must be defined in
    credentials.json.

    Args:
        sub_callback (func(topic, msg), optional): Callback-Function when message is recieved.

    Returns:
        MQTT-Client
    """
    with open("credentials.json", "r") as f:
        credentials = ujson.load(f)
    
    try:
        from umqtt.robust import MQTTClient
    except ImportError as e:
        import upip
        upip.install('micropython-umqtt.simple')
        upip.install('micropython-umqtt.robust')
        from umqtt.robust import MQTTClient
        
    # Set Options for MQTT-Broker
    client = MQTTClient(ubinascii.hexlify(machine.unique_id()), credentials["mqtt"]["host"], credentials["mqtt"]["port"])
    # Set callback to handle Messages
    if sub_callback is not None:
        client.set_callback(sub_callback)
    # Connect
    client.connect(clean_session=False)
    for topic in credentials["mqtt"]["topics"]:
        client.subscribe(topic)
    time.sleep(3)
    client.check_msg()
    return client