# Eydam-Prototyping: ep_statemachine

Python-Modul, um eine einfache Statemachine umzusetzen.

Beispiel:

```python
import ep_statemachine
i = 0
        
def inc():
    nonlocal i
    i = i + 1

workflow = [
    "press coffee button",
    "press coffee button",
    "press espresso button",
    "press espresso button",
    "press off button",
    "press off button",
]

# define states
s_sleep = es.state("sleep", initial=True, entry_action=inc)
s_select_input = es.state("select_input", entry_action=inc)
s_make_coffee = es.state("make coffee")
s_make_espresso = es.state("make espresso")
s_done = es.state("done")
s_off = es.state("off")

# define transitions
t_wake_up = es.transition(s_select_input, identifier="wake up", condition=lambda: re.match("press (coffee|espresso|off) button", workflow[i]) is not None)
s_sleep.add_transition(t_wake_up)

t_coffee = es.transition(s_make_coffee, identifier="coffee", condition=lambda: workflow[i] == "press coffee button")
s_select_input.add_transition(t_coffee)

t_espresso = es.transition(s_make_espresso, identifier="espresso", condition=lambda: workflow[i] == "press espresso button")
s_select_input.add_transition(t_espresso)

t_finished = es.transition(s_done, identifier="finished", condition=lambda: True)
s_make_coffee.add_transition(t_finished)
s_make_espresso.add_transition(t_finished)

t_back_to_sleep = es.transition(s_sleep, identifier="back to sleep", condition=lambda: True)
s_done.add_transition(t_back_to_sleep)

t_turn_off = es.transition(s_off, identifier="turn off", condition=lambda:workflow[i] == "press off button")
s_select_input.add_transition(t_turn_off)

sm = es.statemachine([s_sleep, s_select_input, s_make_coffee, s_make_espresso, s_done, s_off])
sm.init()

# do one step after another
sm.step()
```