from z3 import *

# Create solver
solver = Solver()
solver.set("unsat_core", True)


# Define more variables
x1, x2, x3, x4, x5 = Bools('x1 x2 x3 x4 x5')

# Add conflicting constraints
solver.add(x1 + x2 + x3 == x4)  # Exactly two should be True
solver.add(x1 + x2 == x3)


# Check for satisfiability
if solver.check() == unsat:
	print("No solution found!")

	# Get the unsat core (the conflicting constraints)
	unsat_core = solver.unsat_core()
	print("Unsat Core:", unsat_core)
	print("Reason:", solver.reason_unknown())
else:
	print("Solution found:", solver.model())

