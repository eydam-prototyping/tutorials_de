# Heizungssteuerung mit dem ESP32 - Teil 3

Beim letzten Mal haben wir die Steuerung soweit hinbekommen, dass sie an sich funktioniert. In diesem Teil wollen wir in unsere Steuerung ein Display einbauen und die Daten per MQTT an einen Broker senden, sodass wir sie später z.B. in Grafana oder IO-Broker darstellen können.

## 2-Zeilen-LCD-Display

Okay, wir brauchen zusätzlich zum Display noch eine Möglichkeit, Eingaben zu machen. Wir wollen ja nicht immer nur einen Wert angezeigt bekommen, sondern uns aussuchen, was wir angezeigt bekommen wollen. Ich habe mich hier für einen Rotary Encoder entschieden. Damit kann man mit durchs Menü navigieren und der, den ich ausgesucht habe, hat sogar noch einen Schalter mit eingebaut. Das Display, was ich nutze, hat gleich noch eine I2C-Adapterplatine mit angelötet. So können wir sogar noch einige Pins sparen (obwohl wir das in diesem Projekt nicht müssten). 

Hier mein Schaltplan:

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/display.png "display")

Für das Display und den Rotary Encoder braucht ihr noch weitere Bibliotheken, die ich aus Urheberrechtsgründen nicht bei mir hochladen möchte. Ihr könnt sie hier downloaden:

* [https://github.com/MikeTeachman/micropython-rotary](https://github.com/MikeTeachman/micropython-rotary): hier braucht ihr die Dateien `rotary_irq_esp.py` und `rotary.py`
* [https://github.com/dhylands/python_lcd/tree/master/lcd](https://github.com/dhylands/python_lcd/tree/master/lcd): hier braucht ihr die Dateien `esp8266_i2c_lcd.py`, `lcd_api.py`

Kopiert sie bei euch auf den ESP32 in das Verzeichnis `/pyboard/lib`. Anschließend könnt ihr mit `upip.install("micropython-eydam-prototyping-lcd-menu")` mein Modul installieren.

Anschließend könnt ihr einmal kurz probieren, ob alles funktioniert hat:

```python
>>> import machine
>>> from esp8266_i2c_lcd import I2cLcd
>>> from rotary_irq_esp import RotaryIRQ
>>> i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
>>> lcd = I2cLcd(i2c, 39, 2, 16)
>>> lcd.clear()
>>> lcd.putstr("Hello World")   # "Hello World" should be displayed
>>> r = RotaryIRQ(18,19,0,10,False)
>>> r.value() # turn rotary
0
>>> r.value()
16
```

Okay. Um jetzt ein Menü auf dem Display darzustellen, müssen wir uns erst einmal eine Struktur überlegen. Ich habe mir folgendes ausgedacht (ich mache es mal auf Englisch, damit es später in den Dateien genau so aussieht. Ihr könnt es aber direkt auf Deutsch machen, wenn ihr wollt. Achtet aber darauf, dass, je nach Display, Umlaute eventuell nicht funktionieren). In der ersten Zeile steht immer der Menüeintrag, in der zweiten steht das, was in Klammern steht:

* Heater
  * Oven (Temperatur Ofen anzeigen)
  * Tank upper (Temperatur Speicher oben anzeigen)
  * Tank lower (Temperatur Speicher unten anzeigen)
  * State (Zustand der Statemachine anzeigen)
* WiFi
  * SSID (SSID anzeigen)
  * IP (IP anzeigen)
  * Signal (Signalstärke anzeigen)
* ESP32
  * CPU-Temperature (CPU-Temperatur anzeigen)
  * RAM-Usage (Ramnutzung anzeigen)

Um das darzustellen, erstellen wir uns die Datei `menu.json` und kopieren sie auf den ESP32. Dann brauchen wir noch ein bisschen Code, um das Menü auch anzuzeigen. Legt euch dafür die Datei `menu.py` mit folgendem Inhalt an:

```python
# menu.py v1

import machine
import ep_lcd_menu
from rotary_irq_esp import RotaryIRQ
from esp8266_i2c_lcd import I2cLcd

def setup(temps, sm):
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

    lcd = I2cLcd(i2c, 39, 2, 16)
    lcd.clear()

    r = RotaryIRQ(18, 19, 0, 10, False)

    menu = ep_lcd_menu.menu_rot_enc(
        menu_config_file="menu.json", display_type="1602", display=lcd, rotary=r, button_pin=5)

    menu.load()
    menu.render()
    return menu
```

In der `main.py` müsst ihr folgendes ergänzen:

```python
# main.py v10

...

import menu

...

m = menu.setup()

```

Wenn ihr den ESP32 jetzt neu startet, sollte auf dem Display das Menü angezeigt werden. Mit dem Rotaty Encoder könnt ihr durch das Menü navigieren und mit einem Klick auf den Drehknopf könnt ihr den Menüpunkt betreten. Es werden aber noch keine Werte angezeigt. In der `menu.json` haben wir definiert, welche Funktionen aufgerufen werden sollen, um in der zweiten Zeile etwas anzuzeigen:

```json
{
    "title": "Oven",
    "second_line": {
        "reading": "print_T_Oven"
    }
}
```

Wir müssen die Funktion `print_T_Oven` (und alle anderen Funktionen) noch registrieren. Ergänzt dazu folgendes:

```python
# main.py v11
m = menu.setup(get_temp, sm)
m.display_funcs["print_ssid"] = lambda: "{}".format(ssid)
m.display_funcs["print_ip"] = lambda: "{}".format(ip)
m.display_funcs["print_rssi"] = lambda: "{} db".format(wlan.status("rssi")) if wlan.isconnected() else "---"
```

Bzw.:

```python
# menu.py v2

menu.display_funcs = {
    "print_T_Oven": lambda: "{:.2f} C".format(temps("T_Oven")),
    "print_T_TankU": lambda: "{:.2f} C".format(temps("T_TankU")),
    "print_T_TankL": lambda: "{:.2f} C".format(temps("T_TankL")),
    "print_state": lambda: "{}".format(sm.state),
    "print_cpu_temp": lambda: "{:.2f} C".format((esp32.raw_temperature()-32)*5/9),
    "print_ram": lambda: "{:.1f}/{:.1f}kB".format(gc.mem_free()/1024, (gc.mem_alloc()+gc.mem_free())/1024),
}
```

Wir könnten auch alles in die `main.py` schreiben, ich packe aber so viel wie möglich in die `menu.py`, damit die `main.py` möglichst übersichtlich bleibt.

Damit ist unser Menü erstmal fertig. Du kannst es gern noch erweitern, wenn du willst.

## Daten senden über MQTT

Zum Schluss wollen wir die Daten noch an einen MQTT-Broker senden, um sie in Grafana oder IO-Broker darzustellen. Du brauchst einen funktionierenden MQTT-Broker, damit die folgenden Schritte funktionieren. Wie du einen MQTT-Broker mit einem Raspberry Pi aufsetzt, habe ich in [diesem Tutorial](https://www.eydam-prototyping.com/2021/01/09/smart-home-zentrale-mit-dem-raspberry-pi/) beschrieben.

Wir brauchen zunächst einmal zwei weitere Module, um MQTT nutzen zu können. Du kannst sie mit `upip.install("micropython-umqtt.simple2")` und `upip.install("micropython-umqtt.robust2")` installieren. Das Herunterladen und Entpacken nimmt recht viel RAM in Anspruch. Falls du also Probleme mit der Installation hast, kannst du alles andere anhalten (ggf. indem du die `main.py` mit `rm /pyboard/main.py` löscht und später wieder neu kopierst) und die Installation dann durchführen.

Für MQTT brauchen wir noch ein paar Parameter (Host, Port und Topic). Ich habe dafür die `nw_config.html` erweitert (siehe `nw_config_v4.html`)

Anschließend erstellen wir uns eine `mqtt.py`, die uns mit dem MQTT-Broker verbindet:

```python
# mqtt.py v1

import ubinascii
import machine
from umqtt.robust import MQTTClient

def setup(host, port):
    client_id = ubinascii.hexlify(machine.unique_id())
    client = MQTTClient(client_id, host, port)
    client.connect()
    return client
```

In der `main.py` rufen wir diese Funktion dann auf und senden in unserem Timer die MQTT-Botschaften:

```python
# main.py v12

def read_temps(timer, ds, temps, sm):
    ds.convert_temp()
    for key in temps:
        temps[key]["value"] = ds.read_temp(ubinascii.unhexlify(temps[key]["id"]))
    sm.step()
    mqtt_publish()
    gc.collect()

...

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
```

Zusätzlich braucht die `statemachine.py` noch ein kleines Update. Sie muss noch eine Funktion zurückgeben, mit der wir den Zustand der Pumpe ermitteln können:

```python 
# statemachine.py v3

...

return ep_statemachine.statemachine([s_cold, s_heatUp1, s_heatUp2, s_hot, s_toHot, s_muchToHot]), lambda: 1-pump_pin.value()
```

So, das wars. Unsere Steuerung ist fertig für die Endmontage. Im nächsten und letzten Kapitel bauen wir das Gehäuse und nehmen die Steuerung in Betrieb. 