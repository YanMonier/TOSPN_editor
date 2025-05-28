"""
Event class for TLSPN model.
Represents events that can trigger transitions.
"""

class Event:

    def __init__(self, name, id):
        """
        Initialize a new Event.
        
        Args:
            name (str): Name of the event
        """
        self.id = id
        
        self.name = name
        self.transitions = {}  # Dictionary of transitions using this event {transition_id: transition}
        
        # Event listener pattern support
        self._listeners = []
    
    def add_listener(self, listener):
        """Add a listener to this event."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this event."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def update_name(self, new_name):
        """Update the name of the event."""
        old_name = self.name
        self.name = new_name
        self.notify_listeners("event_name_changed", {"old": old_name, "new": new_name})
    
    def add_to_transition(self, transition):
        """Associate a transition with this event."""
        self.transitions[transition.id] = transition
        self._listeners.append(transition)
        self.notify_listeners("transition_added_to_event", transition)
    
    def remove_from_transition(self, transition):
        """Remove a transition's association with this event."""
        if transition.id in self.transitions:
            del self.transitions[transition.id]
            self._listeners.remove(transition)
            self.notify_listeners("transition_removed_from_event", transition)
    
    def get_enabled_transitions(self):
        """Get all enabled transitions associated with this event."""
        return [t for t in self.transitions.values() if t.check_enabled()]
    
    def trigger(self):
        """
        Trigger this event, attempting to reserve tokens for all enabled transitions.
        Returns list of transitions that successfully reserved tokens.
        """
        enabled_transitions = self.get_enabled_transitions()
        reserved_transitions = []
        
        for transition in enabled_transitions:
            if transition.reserve_input_tokens():
                transition.reservation_time = 0  # Start timing
                reserved_transitions.append(transition)
        
        if reserved_transitions:
            self.notify_listeners("triggered", reserved_transitions)
            
        return reserved_transitions
    
    def to_dict(self):
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "transition_ids": list(self.transitions.keys())
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an event from dictionary data."""
        event = cls(data["name"])
        event.id = data["id"]
        # Note: Transitions must be associated separately after all transitions are loaded
        return event 