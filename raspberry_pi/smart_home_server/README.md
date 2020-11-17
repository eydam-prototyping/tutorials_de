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