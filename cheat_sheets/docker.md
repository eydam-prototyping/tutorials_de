# Docker Cheat Sheet

## Installation

Einfach das fertige Installationsscript ausführen:
```
>>> sudo curl -fsSL https://get.docker.com | sh
```
Docker-Compose:
```
>>> sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
>>> sudo chmod +x /usr/local/bin/docker-compose
>>> sudo pip install docker-compose
```

## Images

Ein Image von Dockerhub herunterladen:

```
>>> sudo docker pull eclipse-mosquitto
```

Ein Image ausführen (und herunterladen, falls noch nicht geschehen):
```
>>> sudo docker run eclipse-mosquitto
```
Oder direkt im Hintergrund:
```
>>> sudo docker run -d eclipse-mosquitto
ed5fcc06a7ddb5413c8646fa33a442ff24091be8bef44b07c774123c1a874696
```
Und später wieder zum Terminal des Containers verbinden:
```
>>> sudo docker attach ed5f
```
Port Mapping (Port 1000 der Maschine auf 1883 des Containers):
```
>>> sudo docker run -d -p 1000:1883 eclipse-mosquitto
```
Volume Mapping:


Laufende Container auflisten:
```
>>> sudo docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
488c2b58091a        eclipse-mosquitto   "/docker-entrypoint.…"   20 seconds ago      Up 18 seconds       1883/tcp            eloquent_sutherland
```

Laufenden Containder beenden:
```
>>> sudo docker stop 488c2b58091a
```
oder
```
>>> sudo docker stop eloquent_sutherland
```

Container löschen:
```
>>> sudo docker rm eclipse-mosquitto
```

Images auflisten:
```
>>> sudo docker images
```

Image löschen (Container mit diesem Image darf nicht laufen):
```
>>> sudo docker rmi eclipse-mosquitto
```