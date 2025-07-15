"""
Output class for TLSPN model.
Represents outputs that are computed based on place markings.
"""

class Output:
    
    def __init__(self, name, id):
        """
        Initialize a new Output.
        
        Args:
            name (str): Name of the output
            math_expression (str): Mathematical expression for evaluation
            txt_expression (str): Human-readable expression
        """
        self.id = id
        self.name = name
        self.transitions = {}  # Dictionary of transitions using this event {transition_id: transition}

        # Event listener pattern support
        self._listeners = []
        self.observable=True
    
    def add_listener(self, listener):
        """Add a listener to this output."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this output."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def update_name(self, new_name):
        """Update the name of the output."""
        old_name = self.name
        self.name = new_name
        self.notify_listeners("name_changed", {"old": old_name, "new": new_name})

    def add_to_transition(self, transition):
        """Associate a transition with this event."""
        self.transitions[transition.id] = transition
        self._listeners.append(transition)
        self.notify_listeners("transition_added_to_output", transition)

    def remove_from_transition(self, transition):
        """Remove a transition's association with this event."""
        if transition.id in self.transitions:
            del self.transitions[transition.id]
            self._listeners.remove(transition)
            self.notify_listeners("transition_removed_from_output", transition)


    def to_dict(self):
        """Convert event to dictionary for serialization."""
        return {
            "id":self.id,
            "name":self.name,
            "transition_ids":list(self.transitions.keys())
        }

    @classmethod
    def from_dict(cls, data):
        """Create an event from dictionary data."""
        output = cls(data["name"])
        output.id = data["id"]
        # Note: Transitions must be associated separately after all transitions are loaded
        return output