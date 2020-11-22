# Installation von MicroPython auf einem ESP32

[MicroPython](https://www.micropython.org/) ist Python für Mikrocontroller. Es ist weitestgehend kompatibel mit Python 3.5 und enthält einen vollständigen Python-Compiler und eine Laufzeitumgebung. Ich ärgere mich ein wenig, dass ich mich erst jetzt damit beschäftige. Es beschleunigt den Entwicklungsprozess enorm.

## Firmware installieren

Um MicroPyhton auf einem ESP32 zu installieren, lade ich zunächst die Firmware herunter. Für den [ESP32](https://micropython.org/download/esp32/) gibt es hier die Optionen mit ESP-IDF v3.x oder v4.x. Da v4.x noch nicht alle Features unterstützt, entscheide ich mich für ESP-IDF v3.x Als nächstes muss man sich zwischen der Version mit und ohne SPIRAM entscheiden. Mein Board hat kein SPIRAM, daher nehme ich die Version ohne. Und zum Schluss noch die Frage welche Version: Hier nehme ich die neueste Version, die nicht das Wort "unstable" enthält. Das ist zum Zeitpunkt der Erstellung des Tutorials die Version [esp32-idf3-20200902-v1.13.bin](https://micropython.org/resources/firmware/esp32-idf3-20200902-v1.13.bin).

Um die Firmware auf den ESP32 zu bekommen, nutze ich das esptool vom Chiphersteller Espressiv. Ich mache das ganze in einer eigenen virtuellen Pythonumgebung. Diese erstelle ich mit:

```shell
> python3 -m venv venv
```
Diese aktiviere ich mit:
```shell
# Windows
> ./venv/Scripts/Activate.ps1
```
In dieser Umgebung können wir dann das esptool installieren:
```shell
> pip install esptool
```
Das könnte ein paar Minuten dauern.
Im Anschluss lösche ich den Speicher des ESP32 zuerst und dann übertrage ich die Firmware:
```shell
> esptool.py --port COM5 erase_flash
esptool.py v3.0
Serial port COM5
Connecting.....
Detecting chip type... ESP32
Chip is ESP32-D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: 3c:71:bf:96:f1:e8
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 7.2s
Hard resetting via RTS pin...

> esptool.py --chip esp32 --port COM5 write_flash -z 0x1000 esp32-idf3-20200902-v1.13.bin
esptool.py v3.0
Serial port COM5
Connecting....
Chip is ESP32-D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: 3c:71:bf:96:f1:e8
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Compressed 1448768 bytes to 926007...
Wrote 1448768 bytes (926007 compressed) at 0x00001000 in 82.5 seconds (effective 140.5 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```
Möglicherweise ist euer ESP32 nicht unter COM5 verfügbar. Welchen COM-Port ihr nutzt, könnt ihr in der Windows-Hardwareumgebung herausfinden. Dazu einfach in die Windows-Suchzeile "Geräte-Manager" eintippen. Dann solltet ihr unter "Anschlüsse (COM&LPT)" den COM-Port finden. Falls dort mehrere auftauchen, einfach den ESP32 trennen und wieder verbinden und beobachten, welcher COM-Port neu hinzukommt. 

![Gerätemanager](https://github.com/eydam-prototyping/tutorials_de/blob/master/micropython/ESP32_installation/img/2020-11-21%2013_54_08-Geraetemanager.png)

## Python-Code ausführen

Ab jetzt kann Python-Code auf dem ESP32 ausgeführt werden. Entweder Zeile für Zeile eingetippt in einer REPL (Read-Eval-Print Loop, dt: Einlesen-Ausführen-Ausgeben Schleife) oder als komplette Datei ausgeführt. Dazu brauche ich ein Tool, mit dem ich meinen Code an den ESP32 senden kann. Hier ist rshell eine Option:
```shell
> pip3 install rshell
```

Mit rshell kann ich mir anschauen, welche Dateien auf dem ESP32 zu finden sind. Dazu muss ich nur rshell starten und den Befehl `ls -l /pyboard` ausführen:

```shell
> rshell -p COM5
Using buffer-size of 32
Connecting to COM5 (buffer-size 32)...
Trying to connect to REPL  connected
Testing if ubinascii.unhexlify exists ... Y
Retrieving root directories ... /boot.py/
Setting time ... Nov 21, 2020 15:02:56
Evaluating board_name ... pyboard
Retrieving time epoch ... Jan 01, 2000
Welcome to rshell. Use the exit command to exit rshell.

> ls -l /pyboard
   139 Jan  1 2000  boot.py
```

Mit dem Befehl `repl` starte ich die REPL und kann Befehle eingeben, die direkt ausgeführt werden, z.B.:

```shell
> repl
Entering REPL. Use Control-X to exit.

MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>> help('modules')
__main__          gc                uasyncio/stream   upip_utarfile
_boot             inisetup          ubinascii         upysh
_onewire          machine           ubluetooth        urandom
_thread           math              ucollections      ure
_uasyncio         micropython       ucryptolib        urequests
_webrepl          neopixel          uctypes           uselect
apa106            network           uerrno            usocket
btree             ntptime           uhashlib          ussl
builtins          onewire           uhashlib          ustruct
cmath             sys               uheapq            utime
dht               uarray            uio               utimeq
ds18x20           uasyncio/__init__ ujson             uwebsocket
esp               uasyncio/core     umqtt/robust      uzlib
esp32             uasyncio/event    umqtt/simple      webrepl
flashbdev         uasyncio/funcs    uos               webrepl_setup
framebuf          uasyncio/lock     upip              websocket_helper
Plus any modules on the filesystem

```

Damit ist MicroPython auf dem ESP32 installiert. Jetzt können die Projekte umgesetzt werden.

Ein kleines Cheat Sheet zu rshell habe ich [hier](https://github.com/eydam-prototyping/tutorials_de/blob/master/cheat_sheets/rshell.md) vorbereitet.