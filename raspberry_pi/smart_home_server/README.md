# Smart Home Server mit dem Raspberry Pi

Die meisten meiner anderen Tutorials drehen sich um IoT-Geräte, die eine Steuerzentrale brauchen. Eine Wetterstation, die ihre Daten ins Nichts sendet oder ein Toröffner, den man nicht bedienen kann, ist wenig sinnvoll. Daher hier ein Tutorial, mit dem eine Steuerzentrale eingerichtet werden kann.

# Hardware

Ich verwende für dieses Tutorial ein Raspberry Pi 4. Ein Raspberry Pi 3 würde wahrscheinlich auch reichen, ich habe aber gerade einen 4er verfügbar. Zusätzlich wird natürlich noch ein Netzteil benötigt.

# Software

Ich gehe davon aus, das bereits Raspberry Pi OS auf dem Pi installiert ist. In diesem Tutorial beschreibe ich, wie man die Steuerung mit Docker aufsetzt. Docker hat den großen Vorteil, dass alle Programme gekapselt sind. Ich weiß genau, welche Daten gesichert werden müssen und ein eventueller Umzug auf andere Hardware wird so einfacher.

Docker wird einfach mit dem vom Hersteller bereitgestellten Installations-Script installiert. Achtung: Dieser Weg sollte nur bei wirklich vertrauenswürdigen Quellen gewählt werden. Es werden direkt Befehle mit Root-Rechten ausgeführt:

```shell
pi@raspberrypi:~ $ sudo curl -fsSL https://get.docker.com | sh
```

Damit wir docker auch mit dem User `pi` starten können, müssen wir ihm noch die Rechte dafür geben. Dieser Schritt ist optional. Alternativ müssen einige der folgenden Befehle mit `sudo` ausgeführt werden. Danach den Raspberry Pi neu starten:
```shell
pi@raspberrypi:~ $ sudo usermod -aG docker pi
pi@raspberrypi:~ $ sudo reboot
```

Danach kann einmal geprüft werden, ob die Installation funktioniert hat:
```shell
pi@raspberrypi:~ $ docker version
Client: Docker Engine - Community
 Version:           19.03.13
 API version:       1.40
 Go version:        go1.13.15
 Git commit:        4484c46
 Built:             Wed Sep 16 17:07:02 2020
 OS/Arch:           linux/arm
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          19.03.13
  API version:      1.40 (minimum version 1.12)
  Go version:       go1.13.15
  Git commit:       4484c46
  Built:            Wed Sep 16 17:00:52 2020
  OS/Arch:          linux/arm
  Experimental:     false
 containerd:
  Version:          1.3.7
  GitCommit:        8fba4e9a7d01810a393d5d25a3621dc101981175
 runc:
  Version:          1.0.0-rc10
  GitCommit:        dc9208a3303feef5b3839f4323d9beb36df0a9dd
 docker-init:
  Version:          0.18.0
  GitCommit:        fec3683
```

Wir wollen aber nicht nur einen Docker-Container starten, sondern mehrere gemeinsam. Dazu bietet sich Docker-Compose an. Hier braucht nur ein Konfigurations-Script erstellt werden, mit dem alle Container gestartet werden. Dazu wird zunächst Python und Pip benötigt. Python ist standardmäßig installiert, Pip jedoch nicht unbedingt. Deswegen: 

```shell
pi@raspberrypi:~ $ sudo apt-get install -y python3-pip
```
Danach kann docker-compose installiert werden. Im Anschluss kann gleich geprüft werden, ob die Installation funktioniert hat:

```shell
pi@raspberrypi:~ $ sudo pip3 install docker-compose
pi@raspberrypi:~ $ docker-compose version
docker-compose version 1.27.4, build unknown
docker-py version: 4.3.1
CPython version: 3.7.3
OpenSSL version: OpenSSL 1.1.1d  10 Sep 2019
```

Ich will alle Daten, die gesichert werden müssen, an einem Ort sammeln. Dazu erstelle ich mir einen Ordner:

```shell
pi@raspberrypi:~ $ mkdir docker
pi@raspberrypi:~ $ cd docker
```

## Docker-Compose

In diesem Ordner erstelle ich mir die Datei `docker-compose.yml`, die das Zusammenspiel der Docker-Container beschreibt:
```shell
pi@raspberrypi:~/docker $ nano docker-compose.yml
```

Folgende Container werden benötigt:

| Container | Image | Was macht er? |
|-----------|-------|---------------|
| MQTT-Broker | `eclipse-mosquitto:latest` | nimmt die MQTT-Nachrichten entgegen und verteilt sie |
| Datenbank | `influxdb:latest` | hier werden die Daten gespeichert |
| Telegraf | `telegraf:latest` | ist die Schnittstelle zwischen MQTT-Broker und Datenbank |
| Grafana | `grafana/grafana:latest` | Web-Dashboard - Hier werden die Daten visualisiert |

Das Docker-Compose-File sieht dann so aus:

```yml
version: "3"
services:
  mosquitto:
    image: eclipse-mosquitto:latest
    ports:
      - 1883:1883

  influxdb:
    image: influxdb:latest
    ports:
      - 8086:8086
    volumes:
      - /home/pi/docker/influxdb:/var/lib/influxdb
    environment:
      - INFLUXDB_DB=telegraf
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin

  telegraf:
    image: telegraf:latest
    user: "1000"
    volumes:
      - /home/pi/docker/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin
    depends_on:
      - influxdb

  grafana:
    image: grafana/grafana:latest
    user: "1000"
    ports:
      - 3000:3000
    volumes:
      - /home/pi/docker/grafana:/var/lib/grafana
      - /home/pi/docker/grafana-provisioning:/etc/grafana/provisioning
    depends_on:
      - influxdb
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

Alle Passwörter werden später natürlich geändert.

Wir wollen die Daten alle im vorhin erstellten Ordner docker speichern. Dafür brauchen wir noch ein paar Unterordner. Theoretisch erstellen die Container diese Unterordner selbst, ich hatte aber Probleme mit den Rechten, deswegen erstelle ich sie selbst:

```shell
pi@raspberrypi:~/docker $ mkdir grafana
pi@raspberrypi:~/docker $ mkdir grafana-provisioning
pi@raspberrypi:~/docker $ mkdir influxdb
pi@raspberrypi:~/docker $ mkdir telegraf
```

Wir brauchen auch noch eine Konfigurationsdatei für telegraf. Diese könne wir uns wie folgt erstellen:

```shell
pi@raspberrypi:~/docker $ docker run --rm telegraf telegraf config > ./telegraf/telegraf.conf
```

Anschließend können die Container mit docker-compose gestartet werden. Beim ersten start werden die Container noch heruntergeladen. Das dauert ein paar Minuten, muss aber nur beim ersten mal gemacht werden.

```shell
pi@raspberrypi:~/docker $ docker-compose up -d
```

Wenn alles funktioniert hat, dann sollten die Container jetzt laufen:
```shell
pi@raspberrypi:~/docker $ docker ps
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS                          NAMES
9cae4d47213c        grafana/grafana:latest     "/run.sh"                10 seconds ago      Up 7 seconds        0.0.0.0:3000->3000/tcp         docker_grafana_1
7b428df1106d        telegraf:latest            "/entrypoint.sh tele…"   10 seconds ago      Up 7 seconds        8092/udp, 8125/udp, 8094/tcp   docker_telegraf_1
d0048b5cd3b3        eclipse-mosquitto:latest   "/docker-entrypoint.…"   12 seconds ago      Up 9 seconds        0.0.0.0:1883->1883/tcp         docker_mosquitto_1
e248822bf387        influxdb:latest            "/entrypoint.sh infl…"   12 seconds ago      Up 9 seconds        0.0.0.0:8086->8086/tcp         docker_influxdb_1
```

## Grafana

Grafana sollte nun vom Browser aus erreichbar sein. Dazu die IP vom Raspberry Pi gefolgt von :3000 in die Adresszeile des Browsers eingeben:

![Grafana Login Screen](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2019_43_37-Grafana.png)

Beim ersten Login wird man aufgefordert, das Passwort zu ändern. Danach ist man eingeloggt :)

Um zu testen, ob wir von Grafana aus auf die Datenbank zugreifen können, klicken wir Rechts auf das Zahnrad (Configuration) und dann auf "Data Sources":

![Grafana Menu](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_03_08-Grafana.png)

Hier können wir eine neue Datenquelle erstellen. Wir klicken auf "Add Data Source" und dann auf "InfluxDB".
Hier tragen wir unter dem Punkt HTTP bei URL den Wert "http://influxdb:8086" ein (influxdb, weil wir docker nutzen) und unter dem Punkt InfluxDB Details bei Database den Wert "telegraf". Ganz unten klicken wir dann auf "Save & Test". Wenn alles funktioniert hat, erscheit die Meldung "Data Source is working".

![Grafana Data Source](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_10_09-InfluxDB_Settings-Grafana.png)

![Grafana Data Source](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_12_08-InfluxDB_Settings-Grafana.png)

## Telegraf

Damit wir jetzt ein paar Daten zum Darstellen haben, können wir den Zustand des Raspberry Pi monitoren. Ich habe mir dazu ein fertiges Dashboard rausgesucht: [https://grafana.com/grafana/dashboards/10578](https://grafana.com/grafana/dashboards/10578). Dazu muss die vorhin erzeugte `telegraf.conf` bearbeitet werden. Also wieder zurück zum Raspberry Pi:

```shell
pi@raspberrypi:~/docker/telegraf $ nano telegraf.conf
```

Hier müssen die `#`-Zeichen (Kommentar) vor folgenden Zeilen entfernt werden, bzw. die entsprechenden Zeilen angepasst werden:

```shell
[[outputs.influxdb]]
  urls = ["http://influxdb:8086"]

[[inputs.net]]
  interfaces = ["eth0", "wlan0"]

[[inputs.netstat]]

[[inputs.file]]
  files = ["/sys/class/thermal/thermal_zone0/temp"]
  name_override = "cpu_temperature"
  data_format = "value"
  data_type = "integer"

[[inputs.exec]]
  commands = ["/opt/vc/bin/vcgencmd measure_temp"]
  name_override = "gpu_temperature"
  data_format = "grok"
  grok_patterns = ["%{NUMBER:value:float}"]
```

Um Informationen über die GPU auslesen zu können, müssen wir noch die Rechte anpassen:

```shell
pi@raspberrypi:~/docker $ sudo usermod -G video pi
```

Dann die Container neustarten mit:
```shell
pi@raspberrypi:~/docker $ docker-compose restart
Restarting docker_telegraf_1  ... done
Restarting docker_grafana_1   ... done
Restarting docker_influxdb_1  ... done
Restarting docker_mosquitto_1 ... done
```

Um sicherzustellen, dass man sich nicht irgendwo vertippt hat und das Config-File nicht geparst werden kann, kann man direkt danach prüfen, ob alle Container wirklich laufen:

```shell
pi@raspberrypi:~/docker $ docker ps
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS                          NAMES
f852de155e04        telegraf:latest            "/entrypoint.sh tele…"   42 minutes ago      Up About a minute   8092/udp, 8125/udp, 8094/tcp   docker_telegraf_1
1998c84c5cb7        grafana/grafana:latest     "/run.sh"                42 minutes ago      Up About a minute   0.0.0.0:3000->3000/tcp         docker_grafana_1
8745dbf9bed1        influxdb:latest            "/entrypoint.sh infl…"   42 minutes ago      Up About a minute   0.0.0.0:8086->8086/tcp         docker_influxdb_1
747b453ef975        eclipse-mosquitto:latest   "/docker-entrypoint.…"   42 minutes ago      Up About a minute   0.0.0.0:1883->1883/tcp         docker_mosquitto_1
```

Sollte das nicht der Fall sein, helfen einem die Log-Files oft weiter:

```shell
pi@raspberrypi:~/docker $ docker-compose logs telegraf
```

Jetzt sollten Status-Daten vom Raspberry Pi in die Datenbank gespeichert werden. Diese können wir in Grafana abrufen. Dazu können wir uns entweder selbst ein Dashboard erstellen, oder das oben erwähnte, fertige Dashboard importieren. Dazu in Grafana rechts auf das Plus (Create) und dann auf Import klicken:

![Grafana Menu](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_44_03-Grafana.png)

Dann in das Feld "Import via grafana.com" die ID des Dashboards 10578 eintragen und dann auf "Load" klicken:

![Grafana Menu](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_48_46-Import_Import-Grafana.png)

Auf der nächsten Seite noch die vorhin erzeugte Datenquelle (InfluxDB) angeben und auf Import klicken:

![Grafana Menu](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_50_19-Import_Import-Grafana.png)

Dann sollte das Dashboard zu sehen sein:

![Grafana Menu](https://github.com/eydam-prototyping/tutorials_de/blob/master/raspberry_pi/smart_home_server/img/2020-11-18%2020_52_12-Raspberry%20Pi%20Monitoring-Grafana.png)


Herzlichen Glückwunsch, du hast dir eine erste kleine Smart-Home-Zentrale erstellt :)

MQTT konnten wir hier noch nicht testen, dafür brauchen wir ein paar IoT-Geräte.