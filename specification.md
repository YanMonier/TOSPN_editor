# Time Output Synchronised Petri Net (TOSPN) Specification

## Overview
A Time Output Synchronised Petri Net (TOSPN) is a variant of Petri nets that incorporates timed transitions with event synchronization and output generation. This document specifies the key properties and behaviors of TOSPN.

## Core Components

### Places
- Hold tokens representing resources or states
- Connected to transitions via directed arcs
- Maintain a current marking (number of tokens)

### Transitions
- Connect input and output places
- Associated with:
  - An event
  - A time interval [time1, time2]
  - Input arcs (with weights)
  - Output arcs (with weights)

### Events
- External or internal signals that trigger transitions
- Include a special "λ" event for autonomous transitions

### Outputs
- Mathematical expressions based on place markings
- Can detect rising and falling edges of conditions
- Used for system synchronization and monitoring

## Behavioral Semantics

### Transition Enabling
1. A transition becomes enabled when all its input places have sufficient tokens according to the input arc weights
2. The transition remains in a waiting state until its associated event occurs

### Event Observation and Token Reservation
1. When the associated event is observed for an enabled transition:
   - Required tokens in the input places are immediately reserved for this transition
   - Reserved tokens are no longer available to other transitions
   - A clock/timer starts at the moment of event observation

### Firing Window
1. After event observation and token reservation:
   - The transition must fire within its specified time interval [time1, time2]
   - The timing clock starts from the moment of event observation
   - Reserved tokens remain unavailable to other transitions during this window
   - The actual firing can occur at any point within this interval

### Transition Firing
1. When the transition fires:
   - Reserved tokens are consumed from input places
   - New tokens are produced in output places according to output arc weights
   - The firing must occur within the specified time interval

## Key Characteristics

1. **Event-Driven Behavior**
   - Transitions are triggered by events rather than just token availability
   - Events initiate the token reservation and timing process

2. **Token Reservation**
   - Tokens are reserved immediately upon event observation
   - Reservation ensures resource availability for the triggered transition
   - Prevents resource conflicts during the firing window

3. **Timed Response Window**
   - Time intervals represent bounded response times after event observation
   - Timing starts at event observation, not at enabling
   - Allows modeling of systems with flexible but bounded processing times

4. **Output Synchronization**
   - System state can be monitored through output expressions
   - Supports detection of state changes through rising/falling edge detection
   - Enables synchronization with external systems

## Applications

TOSPN is particularly suitable for modeling systems where:
- Resources need to be reserved upon event detection
- Processing times are bounded but flexible
- Event observation and actual processing/completion are separated in time
- Resource conflicts need to be resolved at event observation
- System state changes need to be monitored and synchronized with external systems 