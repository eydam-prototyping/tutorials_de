# Eydam-Prototyping: ep_config

Eine einfache Bibliothek, um Konfigurationsdateien im JSON-Format zu bearbeiten. Sie wird in einigen meiner anderen Bibliothekten verwendet.

```python
import ep_config

c = ep_config.config()
#c.config = c.make_sample_config()
c.load()

c.set("wifi_config/dhcp_hostname", "ESP32")
c.save()
```