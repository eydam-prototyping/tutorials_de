import ujson
import network
import time
import ubinascii
import ep_logging

class wifi:
    def __init__(self, config_file="config.json", max_time_wait_for_connect=5, logger=None):
        self.config_file = config_file
        self.max_time_wait_for_connect = max_time_wait_for_connect
        self.logger = logger if logger is not None else ep_logging.default_logger(appname="wifi")

    def connect(self):
        config = {}
        try:
            with open(self.config_file, "r") as f:
                config = ujson.load(f)
        except:
            self.logger.warning("No or invaild config file. Creating new file.")
            config = self.make_sample_config()
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        wlan.active(True)

        if "wifi_config" in config:
            if "dhcp_hostname" in config["wifi_config"]:
                wlan.config(dhcp_hostname=config["wifi_config"]["dhcp_hostname"])
                self.logger.info("Set hostname to " + config["wifi_config"]["dhcp_hostname"])

        if "wifi_nets" in config:
            available_nets = sorted(wlan.scan(), key=lambda x: x[3], reverse=True) 
            configured_ssids = [net["ssid"] for net in config["wifi_nets"]]
            nets = [x for x in available_nets if x[0].decode("ascii") in configured_ssids]  
            i = -1
            ssid = ""
            bssid = ""

            for net in nets:
                ssid = net[0].decode("ascii")
                configured_nets = [net for net in config["wifi_nets"] if net["ssid"] == ssid]
                for configured_net in configured_nets:
                    pwd = configured_net["pass"]
                    if "bssid" in configured_net:
                        if configured_net["bssid"].upper() != ubinascii.hexlify(net[1]).decode("ascii").upper():
                            continue
                    
                    bssid = ubinascii.hexlify(net[1]).decode("ascii").upper()
                    wlan.connect(ssid, pwd, bssid=net[1])
                    retry = 0
                    while (not wlan.isconnected()) and (retry < self.max_time_wait_for_connect): 
                        time.sleep(1)
                        retry += 1
                        self.logger.debug("Waiting: " + str(retry) + "/" + str(self.max_time_wait_for_connect))
                    
                if wlan.isconnected():
                    break

            if wlan.isconnected():
                self.logger.info("Connected to " + ssid)
                return wlan, ssid, bssid

        self.logger.warning("Could not connect to configured wifi. Starting AP")
        wlan.active(False)

        wlan = network.WLAN(network.AP_IF)
        wlan.active(True)
        wlan.config(essid=config["wifi_config"]["ap_ssid"])
        wlan.config(password=config["wifi_config"]["ap_pass"])
        
        self.logger.warning("Please connect to " + config["wifi_config"]["ap_ssid"] + " and configure network")
        
        return wlan, config["wifi_config"]["ap_ssid"], None

    def make_sample_config(self):
        config = {
            "wifi_config":{
                "dhcp_hostname": "ESP32",
                "ap_ssid": "ESP32",
                "ap_pass": "eydam-protoyping"
            },
            "wifi_nets": [
                {
                    "ssid": "ssid1", 
                    "pass": "pass1",
                    "bssid": "123456"
                },{   
                    "ssid": "ssid2",
                    "pass": "pass2"
                }
            ],
            "mqtt_config": {
                "host": "192.168.178.128",
                "port": "1883",
            }
        }

        with open(self.config_file, "w") as f:
            ujson.dump(config, f)

        return config