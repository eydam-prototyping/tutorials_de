import ep_network
import os

wlan = ep_network.connect_to_wifi()

if "next" in os.listdir():
    for file in os.listdir("next"):
        os.rename("next/"+file, file)
    os.rmdir("next")