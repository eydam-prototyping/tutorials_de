# Pip auf dem ESP32/ESP8266

Mit Micropython kann nicht nur Python auf einem Mikrocontroller verwendet werden, es können sogar Bibliotheken installiert werden. Hier ein kleiner Code-Schnipsel, der versucht, eine Bibliothek zu importieren. Falls es fehlschägt, wird sie nachinstalliert. Das funktioniert natürlich nur mit Internetverbindung.

```python
try:
    from umqtt.robust import MQTTClient
except ImportError as e:
    import upip
    upip.install('micropython-umqtt.simple')
    upip.install('micropython-umqtt.robust')
    from umqtt.robust import MQTTClient
```