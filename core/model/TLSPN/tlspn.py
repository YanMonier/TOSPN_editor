"""
TLSPN (Time Output Synchronised Petri Net) class.
Main class that manages the complete Petri net model.
"""

from .place import Place
from .transition import Transition
from .arc import Arc
from .event import Event
from .output import Output

class TLSPN:
    def __init__(self):
        """Initialize a new TLSPN model."""
        # Model elements
        self.model_type="TLSPN"
        self.places = {}        # Dictionary of places {id: place}
        self.transitions = {}   # Dictionary of transitions {id: transition}
        self.arcs = {}         # Dictionary of arcs {id: arc}
        self.events = {}       # Dictionary of events {id: event}
        self.outputs = {}      # Dictionary of outputs {id: output}
        
        # Name mappings for quick lookup
        self.place_names = {}   # Dictionary of places by name {name: place}
        self.event_names = []   # List of event names
        self.output_names = []  # List of output names
        
        # Marking management
        self.marking_dic = {}    # Current marking {place_id: token_count}
        self.last_marking_dic = {}  # Previous marking {place_id: token_count}
        
        self.place_id = 0
        self.transition_id = 0
        self.arc_id = 0
        self.event_id = 0
        self.output_id = 0

        # Event listener pattern support
        self._listeners = []

        # Create default lambda event
        self.add_event("λ")
        self.add_output(".")

        self.simulation_time=0
        
    
    def add_listener(self, listener):
        """Add a listener to this TLSPN."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove a listener from this TLSPN."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, event_type, data=None):
        """Notify all listeners of a change."""
        for listener in self._listeners:
            listener.on_change(self, event_type, data)
    
    def update_marking(self, place, new_token_count):
        """Update the marking of a place and maintain marking history."""
        self.last_marking_dic[place.id] = self.marking_dic.get(place.id, 0)
        self.marking_dic[place.id] = new_token_count
        self.notify_listeners("marking_changed", {
            "place": place,
            "old_marking": self.last_marking_dic[place.id],
            "new_marking": new_token_count
        })
    
    def get_marking(self, place):
        """Get the current marking of a place."""
        return self.marking_dic.get(place.id, 0)
    
    def get_last_marking(self, place):
        """Get the previous marking of a place."""
        return self.last_marking_dic.get(place.id, 0)
    
    def get_output_expression_with_names(self, output):
        """
        Get the output expression using place names instead of IDs.
        
        Args:
            output: Output object whose expression should be converted
            
        Returns:
            str: Expression with place names instead of IDs
        """
        return output.retrieve_marking_name_expression(self.places)
    
    def add_place(self, name=None, token_number=0, id=None):
        """
        Add a new place to the TLSPN.
        
        Args:
            name (str, optional): Name for the place. If None, auto-generated.
            token_number (int, optional): Initial number of tokens. Defaults to 0.
            
        Returns:
            Place: The newly created place
            
        Raises:
            ValueError: If the place name is invalid or already exists
        """
        print(f"debug: TLSPN_place: {self.place_id} {self.place_names.keys()}")
        if id is None:
            place = Place(self, self.place_id, name, token_number)
            self.place_id += 1
        else:
            place = Place(self, id, name, token_number)
        
        if place.id in self.places:
            raise ValueError(f"Place with ID {place.id} already exists")
        
        self.places[place.id] = place
        self.place_names[place.name] = place
        
        # Initialize marking
        self.marking_dic[place.id] = token_number
        self.last_marking_dic[place.id] = token_number
        place.token_number = token_number
        
        self.notify_listeners("place_added", place)
        return place
    
    def add_transition(self, name=None, event=None, output=None , id=None, timing_interval=None):
        """Add a new transition to the TLSPN."""

        print("DEGBUG timing interval ",timing_interval)
        if event is None:
            event = self.get_event_by_name("λ")

        if output is None:
            output = self.get_output_by_name(".")

        if timing_interval==None:
            timing_interval=[0,0]

        if id is None:
            transition = Transition(self, self.transition_id, name, event, output, timing_interval)
            self.transition_id += 1

        else:
            if id in self.transitions:
                raise ValueError(f"Transition with ID {id} already exists")
            transition = Transition(self, id, name, event, output, timing_interval)
            
        self.transitions[transition.id] = transition
        self.notify_listeners("transition_added", transition)
        return transition
    
    def add_arc(self, source, target, id=None):
        """Add a new arc between source and target elements."""
        if id is None:  
            arc = Arc(source, target, self.arc_id)
            self.arc_id += 1
        else:
            arc = Arc(source, target, id)
        
        if arc.id in self.arcs:
            raise ValueError(f"Arc with ID {arc.id} already exists")
        
        self.arcs[arc.id] = arc
        self.notify_listeners("arc_added", arc)
        return arc
    
    def add_event(self, name, id=None):
        """Add a new event to the TLSPN."""
        if id is None:
            event = Event(name, self.event_id)
            self.event_id += 1
        else:
            event = Event(name, id)
        
        if name in self.event_names:
            raise ValueError(f"Event with name {name} already exists")
        
        self.events[event.id] = event
        self.event_names.append(name)
        self.notify_listeners("event_added", event)
        return event
    
    def add_output(self, name, id=None):
        """Add a new output to the TLSPN."""
        if id is None:
            output = Output(name, self.output_id)
            self.output_id += 1
        else:
            output = Output(name,  id)
        
        if name in self.output_names:
            raise ValueError(f"Output with name {name} already exists")

        self.outputs[output.id] = output
        self.output_names.append(name)
        self.notify_listeners("output_added", output)
        return output
    
    def remove_place(self, place):
        """Remove a place and all its connected arcs."""
        # Remove connected arcs first
        for arc in list(place.input_arcs + place.output_arcs):
            self.remove_arc(arc)
        
        # Remove place and its markings
        del self.places[place.id]
        del self.place_names[place.name]
        if place.id in self.marking_dic:
            del self.marking_dic[place.id]
        if place.id in self.last_marking_dic:
            del self.last_marking_dic[place.id]
            
        self.notify_listeners("place_removed", place)
    
    def remove_transition(self, transition):
        """Remove a transition and all its connected arcs."""
        # Remove connected arcs first
        for arc in list(transition.input_arcs + transition.output_arcs):
            self.remove_arc(arc)
        
        # Remove from associated event
        if transition.event:
            transition.event.remove_from_transition(transition)
        if transition.output:
            transition.output.remove_from_transition(transition)
        
        # Remove transition
        del self.transitions[transition.id]
        self.notify_listeners("transition_removed", transition)
    
    def remove_arc(self, arc):
        """Remove an arc from the TLSPN."""
        arc.remove()  # This removes the arc from its source and target
        del self.arcs[arc.id]
        self.notify_listeners("arc_removed", arc)
    
    def remove_event(self, event):
        """Remove an event and clear its associations."""
        # Remove event from all associated transitions
        for transition in list(event.transitions.values()):
            event.remove_transition(transition)
        
        del self.events[event.id]
        self.event_names.remove(event.name)
        self.notify_listeners("event_removed", event)
    
    def remove_output(self, output):
        """Remove an output from the TLSPN."""

        for transition in list(output.transitions.values()):
            output.remove_transition(transition)

        del self.outputs[output.id]
        self.output_names.remove(output.name)
        self.notify_listeners("output_removed", output)


    
    def to_dict(self):
        """Convert TLSPN to dictionary for serialization."""
        return {
            "general_info":{
                "place_id_num":self.place_id,
                "transition_id_num":self.transition_id,
                "arc_id_num":self.arc_id,
                "event_id_num":self.event_id,
                "output_id_num":self.output_id,
                "model_type": self.model_type
            },
            "places": {place.id:place.to_dict() for place in self.places.values()},
            "transitions": {trans.id:trans.to_dict() for trans in self.transitions.values()},
            "arcs": {arc.id:arc.to_dict() for arc in self.arcs.values()},
            "events": {event.id:event.to_dict() for event in self.events.values()},
            "outputs": {output.id:output.to_dict() for output in self.outputs.values()},
            "marking": self.marking_dic.copy()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a TLSPN from dictionary data."""
        tlspn = cls()
        
        # Clear default lambda event
        tlspn.events.clear()
        tlspn.event_names.clear()
        tlspn.outputs.clear()
        tlspn.output_names.clear()
        
        # Load events first (needed for transitions)
        for event_data_id, event_data in data["events"].items():
            tlspn.add_event(event_data["name"], event_data["id"])

        for output_data_id,output_data in data["outputs"].items():
            tlspn.add_output(output_data["name"], output_data["id"])
        
        # Load places
        for place_data_id,place_data in data["places"].items():
            tlspn.add_place(place_data["name"], place_data["token_number"], place_data["id"])
        
        
        # Load transitions
        for trans_data_i,trans_data in data["transitions"].items():
            tlspn.add_transition(trans_data["name"], tlspn.get_event_by_id(trans_data["event_id"]), tlspn.get_output_by_id(trans_data["output_id"]), trans_data["id"], trans_data["timing_interval"] )
        
        # Load arcs
        for arc_data_id,arc_data in data["arcs"].items():
            if arc_data["source_type"] == "place":
                source = tlspn.get_place_by_id(arc_data["source_id"])
            else:
                source = tlspn.get_transition_by_id(arc_data["source_id"])
            if arc_data["target_type"] == "place":
                target = tlspn.get_place_by_id(arc_data["target_id"])
            else:
                target = tlspn.get_transition_by_id(arc_data["target_id"])
            tlspn.add_arc(source, target, arc_data["id"])

        
        tlspn.place_id = data["general_info"]["place_id_num"]
        tlspn.transition_id = data["general_info"]["transition_id_num"]
        tlspn.arc_id = data["general_info"]["arc_id_num"]
        tlspn.event_id = data["general_info"]["event_id_num"]
        tlspn.output_id = data["general_info"]["output_id_num"]

        print(f"debug: place_id in tlspn {tlspn.place_id}")
        
        return tlspn
    
    def get_place_by_name(self, name):
        """Get a place by its name."""
        return self.place_names.get(name)
    
    def get_event_by_name(self, name):
        """Get an event by its name."""
        for event in self.events.values():
            if event.name == name:
                return event
        return None
    
    def get_event_by_id(self, id):
        """Get an event by its name."""
        return self.events.get(id)

    def get_output_by_id(self, id):
        """Get an event by its name."""
        return self.outputs.get(id)
    
    def get_place_by_id(self, id):
        """Get a place by its ID."""
        return self.places.get(id)
    
    def get_transition_by_id(self, id):
        """Get a transition by its ID."""
        return self.transitions.get(id)

    def get_output_by_name(self, name):
        """Get an output by its name."""
        for output in self.outputs.values():
            if output.name == name:
                return output
        return None
    
    def validate_place_name(self, name):
        """Check if a place name is valid (unique)."""
        return name not in self.place_names
    
    def validate_event_name(self, name):
        """Check if an event name is valid (unique)."""
        return name not in self.event_names
    
    def validate_output_name(self, name):
        """Check if an output name is valid (unique)."""
        return name not in self.output_names
    
    def rename_place(self, place, new_name):
        """Rename a place, updating all necessary mappings."""
        if not self.validate_place_name(new_name):
            raise ValueError(f"Place name '{new_name}' already exists")
            
        old_name = place.name
        del self.place_names[old_name]
        place.change_name(new_name)
        self.place_names[new_name] = place
        
        self.notify_listeners("place_renamed", {
            "place": place,
            "old_name": old_name,
            "new_name": new_name
        })
        print(f"debug: {self.place_names}")
    
    def rename_event(self, event, new_name):
        """Rename an event, updating all necessary mappings."""
        if not self.validate_event_name(new_name):
            raise ValueError(f"Event name '{new_name}' already exists")
            
        old_name = event.name
        self.event_names.remove(old_name)
        event.update_name(new_name)
        self.event_names.append(new_name)
        
        self.notify_listeners("event_renamed", {
            "event": event,
            "old_name": old_name,
            "new_name": new_name
        })
    
    def rename_output(self, output, new_name):
        """Rename an output, updating all necessary mappings."""
        if not self.validate_output_name(new_name):
            raise ValueError(f"Output name '{new_name}' already exists")
            
        old_name = output.name
        self.output_names.remove(old_name)
        output.update_name(new_name)
        self.output_names.append(new_name)
        
        self.notify_listeners("output_renamed", {
            "output": output,
            "old_name": old_name,
            "new_name": new_name
        })
    
    def get_enabled_transitions(self):
        """Get all currently enabled transitions."""
        return [t for t in self.transitions.values() if t.check_enabled()]
    
    def get_transitions_for_event(self, event_name):
        """Get all transitions associated with an event."""
        event = self.get_event_by_name(event_name)
        return list(event.transitions.values()) if event else []
    
    def trigger_event(self, event_name):
        """
        Trigger an event by name, attempting to reserve tokens for enabled transitions.
        Returns list of transitions that successfully reserved tokens.
        """
        event = self.get_event_by_name(event_name)
        if not event:
            raise ValueError(f"Event '{event_name}' not found")
        return event.trigger()
    

    
    def reset_simulation(self):
        """Reset the simulation state."""
        # Release all reservations
        self.set_simulation_time(0)
        for place in self.places.values():
            place.set_token_number(place.init_token_number)

        for transition in self.transitions.values():
            print("reste transition",transition.name)
            transition.simulation_state="disabled"
            transition.check_enabling_state(self.simulation_time)

        #self.notify_listeners("simulation_reset", None)

    def set_simulation_time(self,time):
        self.simulation_time=time
        self.notify_listeners("update_time", self.simulation_time)

    def add_simulation_time(self,time):
        self.simulation_time+=time
        self.notify_listeners("update_time", self.simulation_time)


    def simulation_step(self,next_step=True):

        something_moved=False
        for transition in self.transitions.values():
            transition.check_firing_state(self.simulation_time)

        for transition in self.transitions.values():
            if transition.simulation_state=="firable":
                if transition.max_firing_time==self.simulation_time:
                    transition.fire(self.simulation_time)
                    something_moved=True

        for transition in self.transitions.values():
            transition.check_enabling_state(self.simulation_time)

        for transition in self.transitions.values():
            if transition.simulation_state=="enabled":
                if transition.event.name=="λ":
                    something_moved = True
                    self.activate_event("λ")



        if something_moved:
            self.simulation_step(next_step)
        else:
            if next_step:
                self.add_simulation_time(1)
                self.simulation_step(False)


    def fire_transition(self,transition):
        if transition.simulation_state == "firable":
            transition.fire(self.simulation_time)
            for transition in self.transitions.values():
                transition.check_enabling_state(self.simulation_time)

    def activate_event(self,event_name):
        trans_list=[]
        for transition in self.transitions.values():
            if transition.event.name == event_name:
                if transition.simulation_state=="enabled":
                    trans_list.append(transition)
        while trans_list!=[]:
            prioritary_transition=min(trans_list, key=lambda x: x.priority_level)
            prioritary_transition.activate(self.simulation_time)
            for transition in self.transitions.values():
                transition.check_enabling_state(self.simulation_time)
            trans_list = []
            for transition in self.transitions.values():
                if transition.event.name == event_name:
                    if transition.simulation_state == "enabled":
                        trans_list.append(transition)

    def simulate_over_time(self,new_time):
        for k in range(new_time):
            self.simulation_step()







