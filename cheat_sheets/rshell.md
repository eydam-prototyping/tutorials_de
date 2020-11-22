# RShell Cheat Sheet

## Installation

```shell
> pip3 install rshell
```
## RShell starten
```shell
> rshell -p COM5
```

## Dateien verwalten

Wenn `rshell` gestartet ist:

Dateien anschauen:
```shell
> ls -l /pyboard
   139 Jan  1 2000  boot.py
   216 Nov 21 15:37 credentials.json
  1135 Jan  1 2000  main.py
```

Neues Verzeichnis anlegen:
```shell
> mkdir /pyboard/data
> ls -l /pyboard
        139 Jan  1 2000  boot.py
        216 Nov 21 15:37 credentials.json
 1074286633 Jan  1 2000  data/
       1135 Jan  1 2000  main.py
```

Dateien kopieren:
```shell
> cp ./cheat_sheets/rshell.md /pyboard/data
> ls -l /pyboard
   139 Jan  1 2000  boot.py
   216 Nov 21 15:37 credentials.json
     0 Jan  1 2000  data/
  1135 Jan  1 2000  main.py
> ls -l /pyboard/data
   133 Nov 22 15:49 rshell.md
```

Dateien löschen:
```shell
> rm /pyboard/data/rshell.md
```

## REPL

```shell
> repl
Entering REPL. Use Control-X to exit.
>
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>> 
>>>
```

soft reboot:
```python
>>> [Ctrl+D]
MPY: soft reboot
MicroPython v1.13 on 2020-09-02; ESP32 module with ESP32
Type "help()" for more information.
>>> 
```

repl beenden:
```python
>>> [Ctrl+X]
```

Weitere Infos auf [hier](https://github.com/dhylands/rshell)