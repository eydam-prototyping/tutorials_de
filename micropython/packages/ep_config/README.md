# Eydam-Prototyping: ep_config

A simple module to edit config files in JSON format. I use it in some of my other modules.

```python
import ep_config

c = ep_config.config()
#c.config = c.make_sample_config()
c.load()

c.set("wifi_config/dhcp_hostname", "ESP32")
c.save()
```