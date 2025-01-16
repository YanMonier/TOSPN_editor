from pyparsing import Word, alphas, alphanums, oneOf, Group, Forward, Literal, Optional, infixNotation, opAssoc

# Define elements
word = Word(alphas, alphanums + "_")  # Matches identifiers like p1, x, FM, FD
operand = Forward()  # Forward declaration
function_call = Forward()  # Forward declaration

lparen = Literal("(").suppress()
rparen = Literal(")").suppress()

func=oneOf(["FM", "FD"])
# Logical operators
operator = oneOf(["AND", "OR"])

# Function call structure: FM(p1) or FD(p2)


# Define operand (could be a word or group or function call)
operand <<= word | function_call | Group(lparen + operand + rparen)  # operand can be word, function call, or group

function_call <<= (func + lparen + operand + rparen)

arg = Group(function_call | word | operand | func )


# Now we need to define how to handle the logical operators and precedence
expr = infixNotation(arg,
    [
        (operator, 2, opAssoc.LEFT)  # AND, OR with left associativity
    ]
)

# Now you can define your parser and test it
input_string = "FM(p1 OR p2) ANDFD AND (p2) OR FM(p3 AND p4)"
result = expr.parseString(input_string)

# Display the result
print(result.asList())

