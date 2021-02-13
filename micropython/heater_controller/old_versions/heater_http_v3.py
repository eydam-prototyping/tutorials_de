import ep_http
import ep_file_server
import ep_rest_server
import ubinascii
import machine

def setup(wlan, logger, ds):
    def scan_wifi(wlan):
        nets = wlan.scan()
        result = []
        for ssid, bssid, channel, rssi, authmode, hidden in nets:
            net = {
                "ssid": ssid.decode("ascii"),
                "bssid": ubinascii.hexlify(bssid).upper(),
                "channel": channel,
                "rssi": rssi,
                "authmode": authmode,
                "hidden": hidden
            }
            result.append(net)
        return result

    def scan_ds(ds):
        roms = ds.scan()
        return [{"id": ubinascii.hexlify(rom), "value": ds.read_temp(rom)} for rom in roms]


    fs = ep_file_server.file_server(
        html_dir="/html/",
        default_file="index.html",
        logger=logger
    )

    crs_nw = ep_rest_server.config_rest_server(
        config_file="./network_config.json",
        logger=logger
    )

    crs_ds = ep_rest_server.config_rest_server(
        config_file="./ds_config.json",
        logger=logger
    )

    crs_ht = ep_rest_server.config_rest_server(
        config_file="./ht_config.json",
        logger=logger
    )

    srs = ep_rest_server.sensor_rest_server(
        [
            ("^wifinets$", lambda path: scan_wifi(wlan)),
            ("^ds18b20$", lambda path: scan_ds(ds)),
            ("^reset$", lambda path: machine.reset()),
        ],
        logger=logger
    )

    routes = [
        ("^\/?rest/nw\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_nw.serve(sock, req)), 
        ("^\/?rest/ds\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_ds.serve(sock, req)), 
        ("^\/?rest/ht\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: crs_ht.serve(sock, req)), 
        ("^\/?sensor\/?([A-Za-z0-9_\.\/]*)\??([A-Za-z0-9_\.\/]*)$", lambda sock, req: srs.serve(sock, req)),
        ("^(.*)$", lambda sock, req: fs.serve(sock, req)), 
    ]

    return ep_http.http_server(routes=routes, micropython_optimize=True, logger=logger)