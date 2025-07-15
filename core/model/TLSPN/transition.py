"""
Transition class for TLSPN model.
Represents a transition with timing constraints and event association.
"""

class Transition:
    
    def __init__(self, TLSPN, id=None, name=None, event=None, output=None, timing_interval=[1, 2]):
        """
        Initialize a new Transition.
        
        Args:
            name (str, optional): Name of the transition. If None, auto-generated.
        """
        self.TLSPN=TLSPN
        self.id = id
        self.type = "transition"  # Type identification for arc connections

        if name is None:
            base_name = f"T.{self.id}"
            counter = 0
            while not self._validate_name(base_name):
                counter += 1
                base_name = f"T.{self.id}.{counter}"
            name = base_name
        else:
            # Validate provided name
            if not self._validate_name(name):
                raise ValueError(f"Transition name '{name}' is invalid or already exists")
            
        self.name = name
        self.priority_level=id
        self.timing_interval = timing_interval  # [min_time, max_time]
        self.event = event
        self.event.add_to_transition(self)
        self.output = output
        self.output.add_to_transition(self)
        
        # Arc connections
        self.input_arcs = []   # Arcs where this transition is the target
        self.output_arcs = []  # Arcs where this transition is the source
        
        # Simulation state
        self.is_enabled = False
        self.activated_time=None
        self.min_firing_time=None
        self.max_firing_time=None

        self.simulation_state="disabled"
        
        # Event listener pattern support
        self._listeners = []
    
    def _validate_name(self, name):
        """
        Validate a place name.
        
        Args:
            name (str): Name to validate
            
        Returns:
            bool: True if name is valid, False otherwise
        """
        # Check if empty
        if not name:
            return False
        
        # Check for invalid characters and reserved words
        invalid_terms = ["OR", "AND", "(", ")", "FM", "FD", "or", "and"]
        if any(term in name.upper() for term in invalid_terms) or " " in name:
            return False
        
        # Check uniqueness
        for transition in self.TLSPN.transitions.values():
            if transition.name.upper() == name.upper():
                return False
        
        return True
    
    def add_listener(self, listener):
        """Add a listener to this transition."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this transition."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def on_change(self, subject, event_type, data):
        """Handle changes in the transition model."""
        if event_type == "event_name_changed":
            self.notify_listeners("event_name_changed", {"old":  data["old"], "new": data["new"]})


    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def change_name(self, new_name):
        """Change the name of the transition."""
        old_name = self.name
        self.name = new_name
        self.notify_listeners("name_changed", {"old": old_name, "new": new_name})
    
    def change_id(self, new_id):
        """Change the ID of the transition."""
        old_id = self.id
        self.id = new_id
        self.notify_listeners("id_changed", {"old": old_id, "new": new_id})
    
    def set_timing(self, min_time, max_time):
        """Set the timing interval for the transition."""
        if min_time <= max_time:
            self.timing_interval = [min_time, max_time]
            self.notify_listeners("timing_changed", self.timing_interval)
            return True
        return False
    
    def set_event(self, event):
        """Associate an event with this transition."""
        old_event = self.event
        if old_event is not None:
            old_event.remove_from_transition(self)
        self.event = event
        self.event.add_to_transition(self)
        self.notify_listeners("event_changed", {"old": old_event, "new": event})

    def set_output(self, output):
        """Associate an event with this transition."""
        old_output = self.output
        if old_output is not None:
            old_output.remove_from_transition(self)
        self.output = output
        self.output.add_to_transition(self)
        self.notify_listeners("output_changed", {"old":old_output, "new":output})
    
    def check_enabled(self):
        """
        Check if the transition is enabled (enough tokens in input places).
        Does not consider reservations.
        """
        for arc in self.input_arcs:
            if arc.source.token_number < arc.weight:
                return False
        return True

    def check_enabling_state(self,time):
        if self.simulation_state=="disabled":
            if self.check_enabled():
                self.simulation_state="enabled"
                self.is_enabled=True
                self.TLSPN.notify_listeners("transition_enabled",[self.id,self.name,time])
                self.notify_listeners("simulation_enabled")

        elif self.simulation_state=="enabled":
            if not self.check_enabled():
                self.simulation_state = "disabled"
                self.is_enabled = False
                self.TLSPN.notify_listeners("transition_disabled", [self.id,self.name, time])
                self.notify_listeners("simulation_not_enabled")
        elif self.simulation_state=="has_fired":
            if self.check_enabled():
                self.simulation_state = "enabled"
                self.is_enabled = True
                self.TLSPN.notify_listeners("transition_enabled", [self.id,self.name, time])
                self.notify_listeners("simulation_enabled")
            else:
                self.simulation_state = "disabled"
                self.is_enabled = False
                self.TLSPN.notify_listeners("transition_disabled", [self.id, self.name, time])
                self.notify_listeners("simulation_not_enabled")


    def activate(self,time):
        if self.simulation_state == "enabled":
            self.activated_time = time
            self.min_firing_time = time + int(self.timing_interval[0] * 1000)
            self.max_firing_time = time + int(self.timing_interval[1] * 1000)
            for arc in self.input_arcs:
                arc.source.remove_tokens(arc.weight)
            self.simulation_state = "activated"
            self.TLSPN.notify_listeners("transition_activated", [self.id, self.name, time])
            self.notify_listeners("simulation_activated_cant_fire")


    def check_firing_state(self,time):
        if self.simulation_state == "activated":
            if time >= self.min_firing_time and time <= self.max_firing_time:
                self.simulation_state = "firable"
                self.TLSPN.notify_listeners("transition_firable", [self.id, self.name, time])
                self.notify_listeners("simulation_activated_can_fire")

    def fire(self,time):
        if self.simulation_state == "firable" and time <= self.max_firing_time:
            for arc in self.output_arcs:
                arc.target.add_tokens(arc.weight)
            self.TLSPN.notify_listeners("transition_fired", [self.id, self.name, time])
            self.simulation_state="has_fired"
        elif self.simulation_state == "firable":
            raise Exception(f"timing error of firing for transition {self.name} at time {time} ")


    
    def to_dict(self):
        """Convert transition to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "timing_interval": self.timing_interval,
            "event_id": self.event.id if self.event else None,
            "output_id": self.output.id if self.output else None,
            "priority_level":self.priority_level
        }
    
    @classmethod
    def from_dict(cls, TLSPN, data):
        """Create a transition from dictionary data."""
        transition = cls(TLSPN, name=data["name"],timing_interval=data["timing_interval"])
        transition.id = data["id"]
        transition.timing_interval = data["timing_interval"]
        transition.priority_level = data["priority_level"]
        # Note: Event must be set separately after all events are loaded
        return transition 