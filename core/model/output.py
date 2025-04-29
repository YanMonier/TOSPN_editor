"""
Output class for TOSPN model.
Represents outputs that are computed based on place markings.
"""

class Output:
    
    def __init__(self, name, math_expression, txt_expression, id):
        """
        Initialize a new Output.
        
        Args:
            name (str): Name of the output
            math_expression (str): Mathematical expression for evaluation
            txt_expression (str): Human-readable expression
        """
        self.id = id
        
        self.name = name
        self.math_marking_expression = math_expression
        self.txt_marking_expression = txt_expression
        
        self.last_value = None
        
        # Event listener pattern support
        self._listeners = []
    
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
    
    def update_expression(self, new_math_expression, new_txt_expression):
        """Update both mathematical and text expressions."""
        old_math = self.math_marking_expression
        old_txt = self.txt_marking_expression
        
        self.math_marking_expression = new_math_expression
        self.txt_marking_expression = new_txt_expression
        
        self.notify_listeners("expression_changed", {
            "old_math": old_math,
            "new_math": new_math_expression,
            "old_txt": old_txt,
            "new_txt": new_txt_expression
        })
    
    def retrieve_marking_name_expression(self, place_dict):
        """
        Get the text expression with place names instead of IDs.
        
        Args:
            place_dict: Dictionary of places {id: place} from TOSPN
            
        Returns:
            str: Expression with place names instead of IDs
        """
        converted_expression = self.txt_marking_expression
        for place_id, place in place_dict.items():
            converted_expression = converted_expression.replace(f"P.{place_id}", place.name)
        
        print(f"debug: expression output converted: {converted_expression}")
        return converted_expression
    
    def evaluate_marking_expression(self, marking_dic):
        """
        Evaluate the output expression with the given marking.
        
        Args:
            marking_dic: Dictionary of place markings {place_id: token_count}
        
        Returns:
            bool: Result of the expression evaluation
        """
        converted_expression = self.math_marking_expression
        for place_id, token_count in marking_dic.items():
            converted_expression = converted_expression.replace(f"P.{place_id}", str(token_count))
        
        try:
            result = eval(converted_expression)
            return bool(result)
        except Exception as e:
            print(f"Error evaluating output {self.name}: {e}")
            return False
    
    def update_value(self, marking_dic):
        """
        Update the output value based on new marking.
        Returns tuple (falling_edge, rising_edge).
        """
        new_value = self.evaluate_marking_expression(marking_dic)
        
        falling_edge = False
        rising_edge = False
        
        if self.last_value is not None:
            falling_edge = self.last_value and not new_value
            rising_edge = not self.last_value and new_value
        
        self.last_value = new_value
        
        if falling_edge or rising_edge:
            self.notify_listeners("value_changed", {
                "value": new_value,
                "falling_edge": falling_edge,
                "rising_edge": rising_edge
            })
        
        return falling_edge, rising_edge
    
    def to_dict(self):
        """Convert output to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "math_expression": self.math_marking_expression,
            "txt_expression": self.txt_marking_expression
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an output from dictionary data."""
        output = cls(
            data["name"],
            data["math_expression"],
            data["txt_expression"]
        )
        output.id = data["id"]
        return output 