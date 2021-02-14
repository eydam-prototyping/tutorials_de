import ubinascii
import machine
from umqtt.robust import MQTTClient

def setup(host, port):
    client_id = ubinascii.hexlify(machine.unique_id())
    client = MQTTClient(client_id, host, port)
    client.connect()
    return client