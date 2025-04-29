"""
Command pattern implementation for TOSPN editor operations.
Provides undo/redo functionality.
"""

class Command:
    """Base class for all commands."""
    
    def execute(self):
        """Execute the command."""
        raise NotImplementedError
    
    def undo(self):
        """Undo the command."""
        raise NotImplementedError

class CommandManager:
    """Manages command execution and undo/redo stacks."""
    
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
    
    def execute(self, command):
        """Execute a command and add it to the undo stack."""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Clear redo stack when new command is executed
    
    def undo(self):
        """Undo the last command."""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
    
    def redo(self):
        """Redo the last undone command."""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
    
    def can_undo(self):
        """Check if undo is available."""
        return bool(self.undo_stack)
    
    def can_redo(self):
        """Check if redo is available."""
        return bool(self.redo_stack)

# Example commands for TOSPN operations
class AddPlaceCommand(Command):
    def __init__(self, tospn, name=None, position=None):
        self.tospn = tospn
        self.name = name
        self.position = position
        self.place = None
    
    def execute(self):
        self.place = self.tospn.add_place(self.name)
        if self.position and hasattr(self.place, 'set_position'):
            self.place.set_position(self.position)
    
    def undo(self):
        self.tospn.remove_place(self.place)

class AddTransitionCommand(Command):
    def __init__(self, tospn, name=None, position=None):
        self.tospn = tospn
        self.name = name
        self.position = position
        self.transition = None
    
    def execute(self):
        self.transition = self.tospn.add_transition(self.name)
        if self.position and hasattr(self.transition, 'set_position'):
            self.transition.set_position(self.position)
    
    def undo(self):
        self.tospn.remove_transition(self.transition)

class AddArcCommand(Command):
    def __init__(self, tospn, source, target):
        self.tospn = tospn
        self.source = source
        self.target = target
        self.arc = None
    
    def execute(self):
        self.arc = self.tospn.add_arc(self.source, self.target)
    
    def undo(self):
        self.tospn.remove_arc(self.arc)

class SetTokensCommand(Command):
    def __init__(self, place, new_tokens):
        self.place = place
        self.new_tokens = new_tokens
        self.old_tokens = place.token_number
    
    def execute(self):
        self.place.token_number = self.new_tokens
        self.place.notify_observers("token_changed", self.new_tokens)
    
    def undo(self):
        self.place.token_number = self.old_tokens
        self.place.notify_observers("token_changed", self.old_tokens)

class SetArcWeightCommand(Command):
    def __init__(self, arc, new_weight):
        self.arc = arc
        self.new_weight = new_weight
        self.old_weight = arc.weight
    
    def execute(self):
        self.arc.set_weight(self.new_weight)
    
    def undo(self):
        self.arc.set_weight(self.old_weight)

class SetTransitionTimingCommand(Command):
    def __init__(self, transition, min_time, max_time):
        self.transition = transition
        self.new_min = min_time
        self.new_max = max_time
        self.old_min = transition.timing_interval[0]
        self.old_max = transition.timing_interval[1]
    
    def execute(self):
        self.transition.set_timing(self.new_min, self.new_max)
    
    def undo(self):
        self.transition.set_timing(self.old_min, self.old_max) 