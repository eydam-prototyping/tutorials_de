import json

class config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {}

    def load(self):
        self.config = {}
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except:
            print("no or invaild config file")
            self.config = self.make_sample_config()

    def save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    def _isint(self, num):
        try:
            int(num)
            return True
        except:
            return False  

    def set(self, path, value):
        if path == "":
            self.config = value
            return 
        p = self.config
        tmp = None
        key = path
        for key in path.split("/"):
            if type(p) is dict:
                if key not in p:
                    p[key] = {}
            elif type(p) is list:
                if not self._isint(key):
                    raise KeyError("Index of list must be of type int")
                else:
                    key = int(key)
                    if key >= len(p):
                        raise KeyError("List index out of range")
            tmp, p = p, p[key]
        tmp[key] = value  

    def get(self, path):
        if path == "":
            return self.config
        if not self.has(path):
            return None
        p = self.config
        for key in path.split("/"):
            if type(p) is list:
                key = int(key)    
            p = p[key]
        return p

    def has(self, path):
        if path == "":
            return True
        p = self.config
        for key in path.split("/"):
            if type(p) is list:
                if not self._isint(key):
                    return False
                key = int(key)
                if len(p) <= key:
                    return False
            elif type(p) is dict:
                if key not in p:
                    return False
            else:
                return False         
            p = p[key]
        return True

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
            json.dump(config, f)

        return config