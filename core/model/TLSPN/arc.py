"""
Arc class for TLSPN model.
Represents a directed connection between places and transitions.
"""

class Arc:
    arc_id = 0  # Class-level counter for unique IDs
    
    def __init__(self, source, target, id):
        """
        Initialize a new Arc.
        
        Args:
            source: Source element (Place or Transition)
            target: Target element (Place or Transition)
        """
        self.id = id
        
        self.source = source
        self.target = target
        self.weight = 1
        
        # Add this arc to the source and target elements
        if hasattr(source, 'output_arcs'):
            source.output_arcs.append(self)
        else:
            raise ValueError("Source element does not have output_arcs attribute")
        if hasattr(target, 'input_arcs'):
            target.input_arcs.append(self)
        else:
            raise ValueError("Target element does not have input_arcs attribute")
            
        # Event listener pattern support
        self._listeners = []
    
    def add_listener(self, listener):
        """Add a listener to this arc."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this arc."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def set_weight(self, weight):
        """Set the weight of the arc."""
        if weight > 0:
            self.weight = weight
            self.notify_listeners("weight_changed", weight)
            return True
        return False
    
    def remove(self):
        """Remove this arc from its source and target elements."""
        if hasattr(self.source, 'output_arcs'):
            self.source.output_arcs.remove(self)
        if hasattr(self.target, 'input_arcs'):
            self.target.input_arcs.remove(self)
    
    def to_dict(self):
        """Convert arc to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source.id,
            "source_type": self.source.type,  # "place" or "transition"
            "target_id": self.target.id,
            "target_type": self.target.type,  # "place" or "transition"
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data, places, transitions):
        """
        Create an arc from dictionary data.
        
        Args:
            data: Dictionary containing arc data
            places: Dictionary of places {id: place}
            transitions: Dictionary of transitions {id: transition}
        """
        # Get source and target elements
        source = places[data["source_id"]] if data["source_type"] == "place" else transitions[data["source_id"]]
        target = places[data["target_id"]] if data["target_type"] == "place" else transitions[data["target_id"]]
        
        # Create arc
        arc = cls(source, target)
        arc.id = data["id"]
        arc.weight = data["weight"]
        return arc 