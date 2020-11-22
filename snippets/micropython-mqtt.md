# MQTT mit Micropython

Auch für MQTT gibt es fertige Bibliotheken von Micropython. 

Hier ein kurzes Beispiel dazu:

```python
import ujson
import ubinascii
import machine
from umqtt.robust import MQTTClient

with open("credentials.json", "r") as f:
    credentials = ujson.load(f)

# Connect to WiFi ...
...

client_id = ubinascii.hexlify(machine.unique_id())

def sub_callback(topic, msg):
    pass

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
    time.sleep(1)
    client.check_msg()
    return client

client = connect_and_subscribe(client_id, credentials["mqtt"]["ip"], 
  credentials["mqtt"]["port"], sub_callback)

while True:
    try:
        client.check_msg()

        ...

    except OSError:
        client = connect_and_subscribe(client_id, credentials["mqtt"]["ip"], 
          credentials["mqtt"]["port"], sub_callback)
```
