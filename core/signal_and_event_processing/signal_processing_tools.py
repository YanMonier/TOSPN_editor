from enum import Enum
from dataclasses import dataclass
import typing as t

class EdgeType(Enum):
    RISING = "rising"
    FALLING = "falling"
    BOTH = "both"

@dataclass
class SignalConfig:
    signal_id: str
    name: str
    units: str = ""
    description: str = ""

@dataclass
class EventRule:
    name: str
    formula: str  # e.g. "sig1 + sig2 > 10"
    edge: EdgeType
    output_event_name: str


def detect_edge(prev_value: bool, current_value: bool, edge: EdgeType) -> bool:
    if edge == EdgeType.RISING:
        return not prev_value and current_value
    elif edge == EdgeType.FALLING:
        return prev_value and not current_value
    elif edge == EdgeType.BOTH:
        return prev_value != current_value
    return False

def save_config(signals, rules, filename):
    data = {
        "signals": [vars(s) for s in signals],
        "rules": [vars(r) for r in rules]
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_config(filename):
    with open(filename) as f:
        data = json.load(f)
    signals = [SignalConfig(**s) for s in data["signals"]]
    rules = [EventRule(**r) for r in data["rules"]]
    return signals, rules

class EventProcessor:
    def __init__(self, rules):
        self.rules = rules
        self.prev_results = {r.name: False for r in rules}
        self.signals = {}

    def update_signal(self, signal_id, value):
        self.signals[signal_id] = value

    def check_rules(self, timestamp):
        events = []
        for rule in self.rules:
            # Prepare variables for eval
            context = {sid: self.signals.get(sid, 0) for sid in self.signals}
            current_result = bool(eval(rule.formula, {}, context))
            if detect_edge(self.prev_results[rule.name], current_result, rule.edge):
                events.append((timestamp, rule.output_event_name))
            self.prev_results[rule.name] = current_result
        return events