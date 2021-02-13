# Heizungssteuerung mit dem ESP32 - Teil 2

Beim letzten mal haben wir den ESP32 soweit bekommen, dass wir ihn über WiFi konfigurieren konnten. Seit dem habe ich die Datei `nw_config.py` etwas aufgehübscht (eigentlich nur CSS) und einen Teil aus der `main.py` in die neu erstellte `heater_http.py` ausgelagert. Einfach nur der Übersichtlichkeit halber.

Dieses Tutorial startet also bei `main_v7.py`, `heater_http_v1.py` und `nw_config_v3.html`. Meine `main.py` sieht jetzt so aus:

```python
# main.py v7
import ep_logging
import ep_wifi
import heater_http

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

http_server = heater_http.setup(wlan, logger_http)
http_server.start()
```

In diesem Teil wollen wir uns der Temperaturmessung widmen.

## Temperaturmessung mit DS18B20-Sensoren

Wer schon einmal vor dem Problem stand, mit einem Microcontroller Temperaturen messen zu müssen, kennt ihn wahrscheinlich: den DS18B20-Temperatursensor von Dallas. Er wird über den 1-Wire-Bus angesprochen. Das bedeutet, wir können mehrere Sensoren mit nur einem Pin am ESP32 auslesen. Auch die Beschaltung ist einfach: wir brauchen lediglich einen 4.7kOhm-PullUp-Widerstand an der Datenleitung. 

Damit ich das alles nicht frei-fliegend verdrahten muss, löte ich die Bauteile auf eine Platine auf. Ich habe dafür eine Lochrasterplatine mit Spannungsversorgung, Relais und einigen Steckern entworfen, die in ein wetterfestes Gehäuse passt. Wenn du also vorhast, dieses Tutorial nachzubauen und mich unterstützen willst könntest du ja eine meiner Platinen kaufen: [SolidCircuit HV3](https://www.eydam-prototyping.com/product/solidcircuit-hv3/).

Auf diese Platine löte ich zuerst den ESP32 auf und schließe ihn an die Spannungsversorgung an. Ich habe die Platine nicht speziell für dieses Projekt entworfen, sondern wollte so variabel wie möglich sein. Deswegen habe ich 3-8-polige JST-XH-Stecker vorgesehen, es spricht aber auch nichts dagegen, nur einen 3-poligen Stecker einzulöten. Für die DS18B20-Sensoren brauche ich ja nicht mehr.
Als nächstes kommen die Lötbrücken und der der PullUp-Widerstand. Ich schließe die Sensoren an GPIO4 an. Zum Testen habe ich mir an einen Sensor einen Stecker gekrimpt.

[Bild]

OK, das wars erst einmal mit dem Löten und Krimpen, jetzt kommt wieder Software. MicroPython wird bereits mit einem Modul zum Nutzen des 1-Wire-Busses ausgeliefert. Wir können es auf die Schnelle mal in der REPL ausprobieren. 

```python
>>> import onewire
>>> import ds18x20
>>> import machine
>>> ow = onewire.OneWire(machine.Pin(4))    # Bus initialisieren auf GPIO4
>>> ds = ds18x20.DS18X20(ow)
>>> roms = ds.scan()                        # nach angeschlossenen Slaves suchen
>>> roms
[bytearray(b'(!a\x85\x13\x19\x01\xb5')]     # Liste mit Slaves, hier nur einer
>>> import ubinascii
>>> ubinascii.hexlify(roms[0])              # die Seriennummer lesbar
b'28216185131901b5'
>>> ds.convert_temp()                       # allen angeschlossenen Slaves den Befehl zum messen geben
>>> ds.read_temp(roms[0])                   # Temperatur auslesen
22.625
```

Das hat ja schon mal ziemlich gut funktioniert. Der Nachteil daran, dass alle Sensoren an einem Pin hängen ist, dass ich anhand der Adresse wissen muss, welcher Sensor welche Temperatur misst. Und da die Adresse auf den Sensoren leider nicht draufsteht, brauchen wir eine Möglichkeit, um die Adressen den Messstellen zuzuordnen. Das schreit doch schon wieder nach einer Konfigurations-Webseite.

Im Prinzip wisst ihr schon, wie das geht. Wir brauchen wieder eine HTML-Datei, eine Konfigurationsdatei und eine neue Funktion, die für uns die angeschlossenen Sensoren ermittelt. Also los geht's. 

Die Konfigurationsdatei ist wieder eine JSON-Datei, diesmal mit dem Namen `ds_config.json`. Darin steht ein Dictionary, in der die Namen der Messstellen den Sensoren zugeordnet sind.

```json
# ds_config.json
{
    "T_Ofen": {
        "id": "28216185131901b5"
    }
}
```

In unserer `heater_http.py` ergänzen wir die Route für die neue Config-Datei und die Funktion zum auslesen der Sensoren. Achtung: setup bekommt `ds` als neuen Parameter:

```python
# heater_http.py v2

...

def setup(wlan, logger, ds):

    ...

    def scan_ds(ds):
        roms = ds.scan()
        return [{"id": ubinascii.hexlify(rom), "value": ds.read_temp(rom)} for rom in roms]

    ...

    

    crs_ds = ep_rest_server.config_rest_server(
        config_file="./ds_config.json",
        logger=logger
    )

    srs = ep_rest_server.sensor_rest_server(
        [
            ("^wifinets$", lambda path: scan_wifi(wlan)),
            ("^ds18b20$", lambda path: scan_ds(ds)),
            ("^reset$", lambda path: machine.reset()),
        ],
        logger=logger
    )

    routes = [
        ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
        ("^\/?rest/ds\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_ds.serve(sock, req)), 
        ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
        ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
    ]

```

In unserer `main.py` erzeugen wir das `ds`-Objekt. Achtung: die Sensoren führen die Messungen nur dann durch, wenn wir es ihnen sagen. Es wäre also sinnvoll, diese Messungen regelmäßig dirchzuführen. Dazu bieten sich Timer an:

```python
# main.py v8

...

import onewire
import ds18x20
import machine

...

ow = onewire.OneWire(machine.Pin(4))
ds = ds18x20.DS18X20(ow)

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: ds.convert_temp())

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()
```

Jetzt noch die HTML-Datei erstellen (siehe `ds_config.py`) und wir sollten unsere Sensoren zuordnen können:

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/ds_config_1.png "ds_config.html")

Ok, so weit, so gut. Widmen wir uns als nächstes der eigentlichen Steuerung.

## Steuerung

Die Steuerung möchte ich als Statemachine umsetzen. Ich denke, ich kann so am besten vorhersagen, was wann passiert und warum.

Hier mal ein Schaubild der Heizung. Eigentlich brauche ich nur drei Temperaturmessstellen (T_Oven, T_TankU, T_TankL), ich möchte mir aber, nur aus Interesse, weitere anzeigen lassen.

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/heater_1.png "heater")


| Messstelle | Langbezeichnung (engl.) | Bedeutung        | wichtig für Steuerung |
|------------|-------------------------|------------------|-----------------------|
| T_Oven     | Oven                    | Ofen             | Ja                    |
| T_TankU    | Tank Upper              | Speicher Oben    | Ja                    |
| T_TankL    | Tank Lower              | Speicher Unten   | Ja                    |
| T_Gas      | Gas                     | Gasheizung       | Nein                  |
| T_Amb      | Ambient                 | Umgebung (außen) | Nein                  |
| T_HeatF    | Heater Flow             | Heizungsvorlauf  | Nein                  |
| T_HeatR    | Heater Return           | Heizungsrücklauf | Nein                  |
| T_Water    | Water                   | Warmwasser       | Nein                  |
| P1         | Pump 1                  | Ladepumpe        | Ja                    |
| P2         | Pump 2                  | Heizungspumpe    | Nein                  |

Gesteuert werden soll die Ladepumpe. Die Heizungspumpe hat eine andere Steuerung, die ich zumindest noch nicht ersetzen will.
Der Ofen wird mit Holz betrieben und ist die Hauptwärmequelle. Wenn gerade keiner da ist, wird auch mal die Gasheizung genutzt, aber eher selten. Die Gasheizung hat ebenfalls eine eigene Pumpe, die ich auch noch nicht steuern will. 

Nun zum Ablauf:

Die Steuerung startet im Zustand "Cold". Sobald mit dem Heizen begonnen wird, (Temperaturschwelle im Ofen überschritten), wird in den Zustand "HeatUp1" gewechselt. Hier springt die Pumpe P1 an (natürlich nur, wenn die Temperatur im Speicher geringer ist als die im Ofen). Die Pumpe läuft solange, bis die Temperatur im Ofen zu klein wird (kleiner als Temperaturschwelle oder kleiner als die Temperatur im Speicher) und wechselt dann in den Zustand "HeatUp2", in dem die Pumpe ausgeschaltet wird. Mit ausgeschalteter Pumpe steigt die Temperatur im Ofen wieder und ab einer gewissen Temperaturdifferenz (Ofen - Speicher) wird wieder in den Zustand "HeatUp1" gewechselt. Diese beiden Zustände wechseln sich so lange ab, bis der Speicher warm (größer als Temperaturschwelle) ist. Dann wird in den Zustand "Hot" gewechselt und die Pumpe geht aus. Das bewirkt, dass die Temperatur im Ofen weiter steigt und die Luftklappe automatisch zu und der Ofen aus geht. Sobald dann die Temperatur im Ofen wieder weit genug gesunken ist, wird wieder in den Zustand "Cold" gewechselt und der Ablauf beginnt von neuem. 

So zumindest die Theorie. Wir sollten aber auch Fehlerzustände berücksichtigen: Was passiert, wenn die Luftklappe hängt? Oder das Einschalten der Pumpe keinen Temperaturabfall im Ofen bewirkt, z.B. weil die Pumpe kaputt ist? 
Wenn die Temperatur im Ofen eine gewisse Temperaturschwelle übersteigt, soll in den Zustand "toHot" gewechselt werden (Warnschwelle 1). Wenn die Temperatur dann noch weiter steigt, soll in den Zustand "muchToHot" gewechselt werden. Was in diesen Zuständen dann genau passiert (Warn-Lampe, Ton, Meldung aufs Handy), können wir uns später überlegen. Ich habe nur ersteinmal die Zustände vorgesehen.

Mein Zustandsautomat sieht dann also so aus (zumindest zum Zeitpunkt, zu dem ich das hier schreibe. Wenn ich daran noch was ändere, schreibe ich noch ein Update). In Klammern habe ich immer einen Vorschlag für die Temperaturschwellen angegeben, die sollen aber einstellbar sein.

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/statemachine.png "statemachine")

Ich habe für solche Anwendungen (Statemachine) auch ein kleines Python-Modul geschrieben. Du kannst es dir mit `upip.install("micropython-eydam-prototyping-statemachine")` installieren.

Bevor wir die Statemachine umsetzen können, müssen wir uns aber erst einmal um die Temperaturschwellen kümmern. Die wollen wir wieder in der Weboberfläche einstellen können. Du kennst die nötigen Schritte dafür ja schon: Config-Datei erstellen, Rest-Server erstellen, HTML-Seite erstellen. Ich schreibe jetzt nicht jeden einzelnen Schritt auf. Du kannst dir die Dateien `heater_http_v3.py`, `ht_config.json` und `ht_config_v1.html` dafür anschauen.

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/ht_config_1.png "ht_config.html")

Jetzt können wir die Statemachine umsetzen. Ich lagere sie gleich in eine neue Datei `statemachine.py` aus. Die Statemachine muss einerseits die aktuellen Temperaturen kennen und andererseits auch die Schwellwerte. Wir übergeben ihr also zwei Funktionen, mit denen diese ermittelt werden können. Als nächstes definieren wir die States, dann die Transitions und zum Schluss ordnen wir die Transitions den States zu:

```python
# statemachine.py v1
import ep_statemachine

def setup(temps, thresh):

    s_cold = ep_statemachine.state("cold", initial=True)    #1
    s_heatUp1 = ep_statemachine.state("heatUp1")            #2
    s_heatUp2 = ep_statemachine.state("heatUp2")            #3
    s_hot = ep_statemachine.state("hot")                    #4
    s_toHot = ep_statemachine.state("toHot")                #5
    s_muchToHot = ep_statemachine.state("muchToHot")        #6

    t_12 = ep_statemachine.transition(s_heatUp1, "t_12",                # (T_Oven > T1) & T_Oven > T_TankU + dT1
        lambda: (temps("T_Oven")>thresh("T1")) & (temps("T_Oven")>temps("T_TankU")+thresh("T1")) 
        )

    t_23 = ep_statemachine.transition(s_heatUp2, "t_23", 
        lambda: (temps("T_Oven")<temps("T_TankL")+thresh("dT1"))        # T_Oven < T_TankL + dT1
        )

    t_32 = ep_statemachine.transition(s_heatUp1, "t_32", 
        lambda: (temps("T_Oven")>temps("T_TankU")+thresh("dT1"))        # T_Oven > T_TankU + dT1
        )

    t_cold = ep_statemachine.transition(s_cold, "t_cold", 
        lambda: (temps("T_Oven")<thresh("T5"))                          # T_Oven < T5
        )

    t_hot = ep_statemachine.transition(s_hot, "t_hot", 
        lambda: (temps("T_TankL")>thresh("T2"))                         # T_TankL > T2
        )

    t_42 = ep_statemachine.transition(s_heatUp1, "t_42",                # T_TankL < T2 - dT1 & T_Oven > T_TankU + dT1
        lambda: (temps("T_TankL")<thresh("T2")-thresh("dT1"))&(temps("T_Oven")>temps("T_TankU")+thresh("dT1"))        
        )

    t_toHot = ep_statemachine.transition(s_toHot, "t_toHot",          
        lambda: (temps("T_Oven")>thresh("T3")+thresh("dT2"))            # T_Oven > T3 + dT2
        )

    t_54 = ep_statemachine.transition(s_hot, "t_54",          
        lambda: (temps("T_Oven")<thresh("T3")-thresh("dT2"))            # T_Oven < T3 - dT2
        )

    t_56 = ep_statemachine.transition(s_muchToHot, "t_56",          
        lambda: (temps("T_Oven")>thresh("T4")+thresh("dT2"))            # T_Oven > T4 + dT2
        )

    t_65 = ep_statemachine.transition(s_toHot, "t_65",          
        lambda: (temps("T_Oven")<thresh("T4")-thresh("dT2"))            # T_Oven < T4 - dT2
        )

    s_cold.add_transition(t_12)
    s_cold.add_transition(t_toHot)

    s_heatUp1.add_transition(t_23)
    s_heatUp1.add_transition(t_cold)
    s_heatUp1.add_transition(t_hot)
    s_heatUp1.add_transition(t_toHot)

    s_heatUp2.add_transition(t_32)
    s_heatUp2.add_transition(t_cold)
    s_heatUp2.add_transition(t_hot)
    s_heatUp2.add_transition(t_toHot)
    
    s_hot.add_transition(t_cold)
    s_hot.add_transition(t_toHot)
    s_hot.add_transition(t_42)

    s_toHot.add_transition(t_54)
    s_toHot.add_transition(t_56)

    s_muchToHot.add_transition(t_65)

    return ep_statemachine.statemachine([s_cold, s_heatUp1, s_heatUp2, s_hot, s_toHot, s_muchToHot])
```

Als nächstes müssen wir einiges in der `main.py` ändern. Brauchen zuerst zwei Funktionen, mit denen die Statemachine die Sensorwerte und die Schwellen ermitteln kann. Dies mache ich mit Lambda-Funktionen, die jeweils einfach nur Werte aus Dictionarys auslesen. Um das Dictionary mit den Temperaturen zu füllen, können wir eine Funktion schreiben, die das im vorhin definierten Timer umsetzt. Hier arbeiten wir etwas ungenau: die Funktion `ds.convert_temp()` startet die Messprozedur in den Sensoren, sie wartet aber nicht, bis sie fertig sind. Das kann bis zu 750ms dauern. Wir wollen in einem Interrupt aber nicht warten sondern lesen die Temperaturen direkt aus und bekommen so die alten Temperaturen. Unsere Steuerung hängt also um einen Takt hinterher, was uns hier aber nicht stören soll. 

Unsere `main.py` sieht jetzt so aus:

```python
# main.py v9

import ep_logging
import ep_wifi
import ep_config
import heater_http
import onewire
import ds18x20
import machine
import ubinascii
import statemachine

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

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

sm = statemachine.setup(
    lambda name: temps[name]["value"] if (name in temps) and ("value" in temps[name]) else 0,
    lambda name: thresh.get(name, 0)
)
sm.init()
sm.step_until_stationary()

def read_temps(timer, ds, temps, sm):
    ds.convert_temp()
    for key in temps:
        temps[key]["value"] = ds.read_temp(ubinascii.unhexlify(temps[key]["id"]))
    sm.step()

tim_ds = machine.Timer(0)
tim_ds.init(mode=machine.Timer.PERIODIC, period=5000, callback=lambda timer: read_temps(timer, ds, temps, sm))

http_server = heater_http.setup(wlan, logger_http, ds)
http_server.start()
```

Es kann sein, dass du in der Weboberfläche den Sensor `T_Ofen` in `T_Oven` umbennen musst, damit das folgende funktioniert.

Wenn du den ESP32 jetzt einmal neu startest, sollte die Steuerung an sich schon funktionieren. Das kannst du in der REPL einmal ausprobieren:

```python
>>> sm.state
cold
>>> temps
{'T_Oven': {'id': '28216185131901b5', 'name': 'T_Oven', 'value': 25.0}}
```

Wenn du den Sensor jetzt mal mit einem Feuerzeug heiß machst (Achtung, nicht übertreiben, der ist nur bis 125°C ausgelegt), sollte sich der Zustand der Statemachine ändern:

```python
>>> temps
{'T_Oven': {'id': '28216185131901b5', 'name': 'T_Oven', 'value': 63.375}}
>>> sm.state
heatUp1
>>> temps
{'T_Oven': {'id': '28216185131901b5', 'name': 'T_Oven', 'value': 97.9375}}
>>> sm.state
toHot
>>> temps
{'T_Oven': {'id': '28216185131901b5', 'name': 'T_Oven', 'value': 112.0625}}
>>> sm.state
muchToHot
```

Super. Ob wirklich alles richtig funktioniert, testen wir, wenn wir auch die anderen Sensoren angeschlossen haben.

Jetzt müssen wir nur noch die Pumpe anschalten und Warnmeldungen ausgeben, wenn wir in die entsprechenden States wechseln.
Auf dem [SolidCircuit-HV3](https://www.eydam-prototyping.com/product/solidcircuit-hv3/) sind bereits zwei Relais verbaut, du brauchst sie nur noch anzuschließen. 

Eine Überlegung zum Anschluss der Pumpe: Das Relais hat zwei Klemmen, die du Nutzen kannst: N.O. (Normal Open) und N.C. (Normal Closed). Wenn du das Relais einschaltest, ist also der N.O.-Ausgang bestromt, ansonsten der N.C.-Ausgang. Du solltest hier überlegen, welche Fehlerfälle auftreten können und was wann am sichersten ist. Mal angenommen, der ESP32 hat eine Fehlfunktion und bleibt in einem State hängen. Hier kannst du nicht wissen, in welchem State er hängen bleibt, es ist also egal, ob du die Pumpe an N.O. oder N.C. anklemmst. Was passiert aber, wenn das Netzteil versagt? Dann startet der ESP32 nicht und das Relais wird nicht bestromt. Und du kannst es in diesem Zustand auch nicht so einfach einschalten, weil du ja irgendwo Strom für das Relais herbekommen müsstest. In diesem Zustand sollte die Pumpe lieber an als aus sein, damit der Ofen in keinem Fall überhitzt.

Für den Fall, dass der ESP32 eine Fehlfunktion hat, will ich mit einem Schalter dafür sorgen können, dass das Relais aus und die Pumpe eingeschaltet wird. Zusätzlich will ich über eine LED sehen, ob die Pumpe gerade an oder aus ist. Dafür habe ich mir folgende Schaltung überlegt: 

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/relay_circuit.png "relay-circuit")

Ich habe mir fertige LED-Module gekauft, in denen ein Vorwiderstand bereits eingebaut ist. Deswegen dimensioniere ich den Widerstand hier nicht. 

Dann brauche ich noch eine LED für die Warnungsanzeige.

![alt text](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/heater_controller/img/warning_led.png "warning_led")

Okay, jetzt schreibe ich mir noch ein paar Funktionen die ausgelöst werden sollen, wenn ein State betreten wird:

```python
# statmachine.py v2
import machine

def setup(temps, thresh):
    pump_pin = machine.Pin(14, machine.Pin.OUT)
    warn_led = machine.Pin(17, machine.Pin.OUT)

    pump_on = lambda: pump_pin.off()
    pump_off = lambda: pump_pin.on()

    warn_on = lambda: warn_led.off()
    warn_off = lambda: warn_led.on()

    def s_cold_enter():
        pump_off()
        warn_off()

    def s_heatUp1_enter():
        pump_on()
        warn_off()

    def s_heatUp2_enter():
        pump_off()
        warn_off()

    def s_hot_enter():
        pump_off()
        warn_off()

    def s_toHot_enter():
        pump_on()
        warn_on()

    def s_muchToHot_enter():
        pump_on()
        warn_on()

    s_cold = ep_statemachine.state("cold", initial=True, entry_action=s_cold_enter)    #1
    s_heatUp1 = ep_statemachine.state("heatUp1", entry_action=s_heatUp1_enter)         #2
    s_heatUp2 = ep_statemachine.state("heatUp2", entry_action=s_heatUp2_enter)         #3
    s_hot = ep_statemachine.state("hot", entry_action=s_hot_enter)                     #4
    s_toHot = ep_statemachine.state("toHot", entry_action=s_toHot_enter)               #5
    s_muchToHot = ep_statemachine.state("muchToHot", entry_action=s_muchToHot_enter)   #6
```

Okay, jetzt nochmal der Feuerzeug-Test und dann funktioniert die Steuerung an sich schon mal. Im nächsten Kapitel werden wir die Messwerte per MQTT ausgeben und ein Display anschließen.