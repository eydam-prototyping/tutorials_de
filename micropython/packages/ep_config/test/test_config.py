import unittest
import ep_config

class Test(unittest.TestCase):
    def test_has(self):
        c = ep_config.config()
        c.config = c.make_sample_config()
        self.assertTrue(c.has("wifi_config"))
        self.assertTrue(c.has("wifi_config/dhcp_hostname"))
        self.assertFalse(c.has("wifi_confi"))
        self.assertTrue(c.has("wifi_nets/0"))
        self.assertFalse(c.has("wifi_nets/2"))
    
    def test_get(self):
        c = ep_config.config()
        c.config = c.make_sample_config()
        self.assertEqual(c.get("wifi_config/dhcp_hostname"), "ESP32")
        self.assertEqual(c.get("wifi_nets/0"), {"ssid": "ssid1", "pass": "pass1", "bssid": "123456"})
        self.assertIsNone(c.get("wifi_nets/2"))

    def test_set(self):
        c = ep_config.config()
        c.config = c.make_sample_config()
        
        c.set("wifi_config/dhcp_hostname", "ESP")
        self.assertEqual(c.get("wifi_config/dhcp_hostname"), "ESP")
        
        c.set("test", "test")
        self.assertEqual(c.get("test"), "test")
        
        c.set("foo/bar", "test")
        self.assertEqual(c.get("foo"), {"bar": "test"})

        c.set("wifi_nets/0", "test")
        self.assertEqual(c.get("wifi_nets/0"), "test")

        self.assertRaises(KeyError, c.set, "wifi_nets/2", "test")
        
        self.assertRaises(KeyError, c.set, "wifi_nets/a", "test")