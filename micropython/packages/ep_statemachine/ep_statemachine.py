import time

class state:
    def __init__(self, identifier, initial=False, entry_action=None, during_action=None, exit_action=None, data={}):
        self.identifier = identifier
        self.initial = initial
        self.transitions = {}
        self.entry_action = entry_action
        self.during_action = during_action
        self.exit_action = exit_action
        self.data = data

    def add_transition(self, transition):
        self.transitions[transition.identifier] = transition

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return self.identifier

class event:
    def __init__(self, identifier="event"):
        self.identifier = identifier
        

class transition:
    def __init__(self, dst, identifier="transition", condition=False, events=[]):
        self.dst = dst
        self.identifier = identifier
        self.condition = condition
        self.events = {event.identifier: event for event in events}
            

class statemachine:
    def __init__(self, states):
        self.states = states
        self.state = None

    def init(self):
        for state in self.states:
            if state.initial:
                self.state = state
                if self.state.entry_action is not None:
                    self.state.entry_action()
                break
        else:
            raise RuntimeError("No initial state defined")

    def _terminated(self):
        return self.state.transitions == {}

    def step(self):
        if self.state is None:
            print("Current state is not defined")
            return

        if self._terminated():
            raise RuntimeError("Terminal state reached")

        for transition in self.state.transitions:
            if self.state.transitions[transition].condition():
                if self.state.exit_action is not None:
                    self.state.exit_action()
                self.state = self.state.transitions[transition].dst
                if self.state.entry_action is not None:
                    self.state.entry_action()
                return
        if self.state.during_action is not None:
            self.state.during_action()

    def action(self, event):
        if self.state is None:
            print("Current state is not defined")
            return

        if self._terminated():
            raise RuntimeError("Terminal state reached")

        for transition in self.state.transitions:
            if event.identifier in self.state.transitions[transition].events:
                if self.state.exit_action is not None:
                    self.state.exit_action()
                self.state = self.state.transitions[transition].dst
                if self.state.entry_action is not None:
                    self.state.entry_action()
                return 


    def cycle(self, delay=0):
        while not self._terminated():
            if delay > 0:
                time.sleep(delay)
            self.step()
