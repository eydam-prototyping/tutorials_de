# main.py v7
import time
import ep_logging
import ep_wifi
import heater_http

wifi = ep_wifi.wifi("./network_config.json", max_time_wait_for_connect=10)
wlan, ssid, bssid = wifi.connect()

logger = ep_logging.colored_logger(appname="main")
logger.notice("WiFi connected")

logger_http = ep_logging.colored_logger(appname="http")

http_server = heater_http.setup(wlan, logger_http)
http_server.start()