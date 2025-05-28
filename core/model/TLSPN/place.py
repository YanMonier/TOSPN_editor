"""
Place class for TLSPN model.
Represents a place in the Petri net with token management and reservation capabilities.
"""

class Place:
    def __init__(self, TLSPN, id, name=None, token_number=0):
        """
        Initialize a new Place.
        
        Args:
            TLSPN: Reference to the TLSPN model
            name (str, optional): Name of the place. If None, auto-generated.
            
        Raises:
            ValueError: If the name is invalid or already exists
        """
        self.TLSPN = TLSPN
        self.id = id
        self.type = "place"  # Type identification for arc connections
        
        # Generate unique name if none provided
        if name is None:
            base_name = f"P.{self.id}"
            counter = 0
            while not self._validate_name(base_name):
                counter += 1
                base_name = f"P.{self.id}.{counter}"
            name = base_name
        else:
            # Validate provided name
            if not self._validate_name(name):
                raise ValueError(f"Place name '{name}' is invalid or already exists")
        
        self.name = name
        
        self.token_number = token_number
        self.reserved_tokens = {}  # Dictionary to track token reservations {transition_id: number_of_tokens}
        
        # Arc connections
        self.input_arcs = []   # Arcs where this place is the target
        self.output_arcs = []  # Arcs where this place is the source
        
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
        for place in self.TLSPN.places.values():
            if place.name.upper() == name.upper():
                return False
        
        return True
    
    def add_listener(self, listener):
        """Add a listener to this place."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this place."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def change_name(self, new_name):
        """Change the name of the place."""
        old_name = self.name
        self.name = new_name
        self.notify_listeners("name_changed", {"old": old_name, "new": new_name})
    
    def change_id(self, new_id):
        """Change the ID of the place."""
        old_id = self.id
        self.id = new_id
        self.notify_listeners("id_changed", {"old": old_id, "new": new_id})
    
    def add_tokens(self, count):
        """Add tokens to the place."""
        self.token_number += count
        self.notify_listeners("token_changed", self.token_number)
    
    def remove_tokens(self, count):
        """Remove tokens from the place."""
        if self.token_number >= count:
            self.token_number -= count
            self.notify_listeners("token_changed", self.token_number)
            return True
        return False
    
    def reserve_tokens(self, transition_id, count):
        """
        Reserve tokens for a specific transition.
        
        Args:
            transition_id: ID of the transition reserving tokens
            count: Number of tokens to reserve
            
        Returns:
            bool: True if reservation was successful, False otherwise
        """
        available_tokens = self.token_number - sum(self.reserved_tokens.values())
        if available_tokens >= count:
            self.reserved_tokens[transition_id] = count
            self.notify_listeners("token_reserved", 
                                {"transition": transition_id, "count": count})
            return True
        return False
    
    def release_reservation(self, transition_id):
        """Release tokens reserved for a specific transition."""
        if transition_id in self.reserved_tokens:
            del self.reserved_tokens[transition_id]
            self.notify_listeners("reservation_released", transition_id)
            return True
        return False
    
    def get_available_tokens(self):
        """Get the number of tokens available for reservation."""
        return self.token_number - sum(self.reserved_tokens.values())
    
    def to_dict(self):
        """Convert place to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "token_number": self.token_number,
            "type": self.type
        }
    
