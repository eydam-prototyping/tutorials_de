# Eydam-Prototyping: ep_logger

Bibliothek, um mit einem Iot-Gerät, auf dem Micropython läuft, Log-Nachrichten an einen Syslog-Server zu senden. Wie man einen Syslog-Server in Verbindung mit Telegraf und Grafana aufsetzt, habe ich [hier](https://www.eydam-prototyping.com/2021/01/17/log-eintraege-besser-nutzen-mit-rsyslog-den-esp32-ueberwachen/) beschrieben.

Die Nachrichten werden im ietf-syslog-protocol-23-Format gesendet.

## Beispiel:

```python
# Syslog-Server (192.168.178.100) is listening on 514 (UDP)
import ep_logging
logger = ep_logging.logger("192.168.178.100", port=514)
logger.notice("Test")
```
Dieser Code würde folgende Nachricht produzieren:

```
<85>1 2021-01-20T20:33:17.0Z esp32 logger - - Test
 -- - ---------------------- ----- ------ - - ----
  | |           |              |      |   | |   +--- message
  | |           |              |      |   | +------- MSGID (=None)
  | |           |              |      |   +--------- PROCID (=None)
  | |           |              |      +------------- appname
  | |           |              +-------------------- hostname
  | |           +----------------------------------- timestamp
  | +----------------------------------------------- version (always 1)
  +------------------------------------------------- facility + servity
```