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

Wir wollen aber nicht nur einen Docker-Container starten, sondern mehrere gemeinsam. Dazu bietet sich Docker-Compose an. Hier braucht nur ein Konfigurations-Script erstellt werden, mit dem alle Container gestartet werden:

```shell
pi@raspberrypi:~ $ sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
pi@raspberrypi:~ $ sudo chmod +x /usr/local/bin/docker-compose
pi@raspberrypi:~ $ sudo pip install docker-compose
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
      - 8083:8083
      - 8086:8086
      - 8090:8090
    volumes:
      # Daten werden im oben erstellten docker-Ordner gespeichert
      - /home/pi/docker/influxdb:/var/lib/influxdb
    environment:
      # Umgebungsvariablen festlegen
      - INFLUXDB_DB=telegraf
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin

  telegraf:
    image: telegraf:latest
    volumes:
      # Telegraf muss noch konfiguriert werden, mehr dazu weiter unten
      - /home/pi/docker/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin
    depends_on:
      # telegraf darf erst gestartet werden, wenn influxdb läuft
      - influxdb
    
  grafana:
    image: grafana/grafana:latest
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