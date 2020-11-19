# Docker Cheat Sheet

## Installation

Einfach das fertige Installationsscript ausführen:
```
>>> sudo curl -fsSL https://get.docker.com | sh
```
## Begriffe

* **Image**: Paket aus einer Software in einer bestimmten Version und der zur Laufzeit benötigeten Diensten und Dateien.
* **Container**: Instanz eines Images.


## Neuen Container starten

Ein Image ausführen (und herunterladen, falls noch nicht geschehen):
```
>>> sudo docker run <IMAGE>
>>> sudo docker run eclipse-mosquitto
```

| Parameter                     | Bedeutung      | Erklärung                                         |
|-------------------------------|----------------|---------------------------------------------------|
| `-d`                          | Detached       | Container läuft im Hintergrund                    |
| `-p Host_Port:Container_Port` | Port-Mapping   | einen Port an einen Container weiterleiten        |
| `-P`                          | Port-Mapping   | alle Ports weiterleiten                           |
| `-v Host_Dir:Container_Dir`   | Volume-Mapping | Container speichert seine Daten in einem Ordner im Dateisystem |
| `-it`                         | Interactive    | Interactive Mode mit Terminal                     |


Port Mapping (Port 1884 der Maschine auf 1883 des Containers):
```
>>> sudo docker run -d -p 1884:1883 eclipse-mosquitto
```

## Container steuern

Laufende Container auflisten:
```
>>> sudo docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
488c2b58091a        eclipse-mosquitto   "/docker-entrypoint.…"   20 seconds ago      Up 18 seconds       1883/tcp            eloquent_sutherland
```

| Parameter | Erklärung                                                    |
|-----------|--------------------------------------------------------------|
| `-a`      | Alle Container auflisten (auch die, die gerade nicht laufen) |

Laufenden Container anhalten:
```
>>> sudo docker stop 488c2b58091a
>>> sudo docker stop eloquent_sutherland
```
Angehaltenen Container starten:
```
>>> sudo docker start 488c2b58091a
>>> sudo docker start eloquent_sutherland
```
Eine Shell in einem laufenden Container starten
```
>>> sudo docker exec -it 488c2b58091a bash
>>> sudo docker exec -it eloquent_sutherland bash
```

## Images

Ein Image von Dockerhub herunterladen:
```
>>> sudo docker pull <IMAGE>
>>> sudo docker pull eclipse-mosquitto
```

Images auflisten:
```
>>> sudo docker images
```

Image löschen (Container mit diesem Image darf nicht laufen):
```
>>> sudo docker rmi eclipse-mosquitto
```

# Docker Compose

## Installation

Docker-Compose:
```
>>> sudo pip install docker-compose
```

## docker-compose.yml

```yml
version: "3"
  services:
    # Name des Containers 
    mosquitto:  
      # Verwendetes Image (optional: Version)
      image: eclipse-mosquitto:latest 
      # Portmapping
      ports:
        - 1884:1883 

    influxdb:
      image: influxdb:latest
      ports:
        - 8083:8083
        - 8086:8086
        - 8090:8090
      # Volume-Mapping
      volumes:
        - /home/pi/docker/influxdb:/var/lib/influxdb
      # Umgebungsvariablen
      environment:
        - INFLUXDB_DB=telegraf
        - INFLUXDB_ADMIN_USER=admin
        - INFLUXDB_ADMIN_PASSWORD=admin
```

## Docker Compose steuern

Docker Compose starten:
```
>>> sudo docker-compose up -d
```

Docker Compose anhalten:
```
>>> sudo docker-compose down
```

Logs anzeigen:
```
>>> sudo docker-compose logs [Container]
```