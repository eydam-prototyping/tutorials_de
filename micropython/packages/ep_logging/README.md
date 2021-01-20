# Eydam-Prototyping: ep_logger

Library, to send log messages from an IoT-Device running MicroPython to a syslog-server. How to setup a syslog-server in combination with Telegraf and Grafana is described here: [hier](https://www.eydam-prototyping.com/en/2021/01/17/log-eintraege-besser-nutzen-mit-rsyslog-den-esp32-ueberwachen/)

The messages will be send in ietf-syslog-protocol-23-format.

## Example:

```python
# Syslog-Server (192.168.178.100) is listening on 514 (UDP)
import ep_logging
logger = ep_logging.logger("192.168.178.100", port=514)
logger.notice("Test")
```

This Code would produce the following message:

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