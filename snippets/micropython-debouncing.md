# Schalter Entprellen

Wer schon einmal mit Schaltern gearbeitet hat, kennt das Problem wahrscheinlich: Wenn ein Schalter geschlossen wird, dann "kleben" die Kontakte nicht zusammen, sondern prallen aufeinander und erzeugen oft mehrere Impulse. Bei einem Lichtschalter fällt das nicht auf, weil diese Prellzeiten sehr kurz sind. Ein Mikrocontroller sieht aber mehrere Impulse.

Ich bin beim Bau der Wetterstation auf dieses Problem gestoßen. Die Reed-Kontakte im Windgeschwindigkeitssensor und im Regensensor haben bis zu 20 Impulse erzeugt!

Es gibt mehrere Ideen, wie man dieses Problem lösen kann:
* Nach einem Impuls wird der Schalter für eine gewisse Zeit "blind" geschaltet. Dies funktioniert für handbetätigte Schalter ganz gut, weil hier üblicherweise relativ langsam gedrückt wird. Mehr als 5 Impulse pro Sekunde sind wohl nicht zu erwarten und falls doch, wird der Bediener es einem nicht übel nehmen, wenn mal ein Impuls verloren geht. Für das Messen einer Drehzahl ist diese Methode aber nicht geeignet, weil man hier die maximale Drehzahl begrenzt.
* Tiefpassfilter: Hier kann mit einem oder mehrerer Kondensatoren und Widerstände eine kleine Filter-Schaltung gebaut werden, mit der das Signal aufbereitet wird. Wenn man die Prellzeiten und maximale Betätigungsrate kennt, kann das ganz gut funktionieren. Nachteil: man muss Hardware nachrüsten und ggf. eine Weile probieren.
* "Intelligentes" erkennen der Prellzeiten: Prell-Kontakte sind meist deutlich schneller, als die wirklich gewollten Impulse. Hier habe ich mir eine kleine Klasse gebaut, die diese Eigenschat nutzt.

## Erkennen der Prellkontakte

Die Zeit zwischen zwei Prellkontakten ist meist deutlich kleiner, als die Zeit zwischen zwei wirklich gewollten Impulsen. Diese Eigenschaft kann man ausnutzen. Für meine Reed-Kontakte bin ich folgendermaßen Vorgegangen:

* Die Zeit zwischen zwei Impulsen wird gemessen. Wenn diese Zeit kleiner ist, als ein Schwellwert, werden sie als Prellkontakt gezählt. Mit einem EWMA-Filter nähert sich dieser Schwellwert dem Durchschnitt der Prellzeiten an.
* Ist die Zeit zwischen den Impulsen größer als Faktor*Schwellwert, wird er als gewollter Impuls gezählt. Der Schwellwert wird hier nicht angepasst.
* Schwellwert und Faktor müssen sinnvoll initialisiert werden, damit diese Methode funktioniert.

Hier der Code:

```python
import machine
import utime

class debounced_switch:
    def __init__(self, pin, initial_bounce_time=200, max_bounce_threshold=5000,
                 ewma_factor=0.9999):

        self.raw_counter = 0                # Zähler über alle Impulse
        self.debounced_counter = 0          # Zähler über entprellte Impulse
        self.last_click = utime.ticks_us()  # Zeit in us des letzten Impulses
        self.mean_bounce_time = initial_bounce_time 
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=self._callback)
        self.initial_bounce_time = initial_bounce_time
        self.max_bounce_threshold = max_bounce_threshold
        self.ewma_factor = ewma_factor

    def _callback(self, pin):
        self.raw_counter += 1
        dt = utime.ticks_us() - self.last_click     # Zeitspanne zwischen zwei Impulsen
        if dt < 0:                                  # wenn dt<0, dann hat überlauf stattgefunden
            self.last_click = utime.ticks_us()      # und Impuls wird verworfen
            return
        if dt > 5*self.mean_bounce_time:            
            self.debounced_counter += 1             # Echter Impuls 
        else:
            self.mean_bounce_time = self.mean_bounce_time * \   
                self.ewma_factor + dt*(1-self.ewma_factor)      # Anpassen EWMA-Filter
        if self.mean_bounce_time > self.max_bounce_threshold:   # Filter hat sich verlernt,
            self.mean_bounce_time = self.initial_bounce_time    # daher reset
        self.last_click += dt

    def reset(self):                        # Zähler zurücksetzen
        self.raw_counter = 0
        self.debounced_counter = 0
```

