from pyparsing import Forward, Word, alphas, alphanums, nums, Literal, Group, Optional, Suppress, ZeroOrMore, oneOf,infixNotation, opAssoc

# Define basic components
lparen = Literal("(").suppress()
rparen = Literal(")").suppress()
operator = oneOf(["AND", "OR"])

operand = Forward()
expr=Forward()

identifier = Word(alphas, alphanums + "_")  # Function name or variable
integer = Word(nums)  # Integer argument

# Forward declaration for recursive expressions
expression = Forward()

# Argument can be an identifier, integer, or another nested expression
arg = Group(expression | identifier | integer | operand)

# Define the expression rule to allow for a functor followed by arguments
expression << (identifier + lparen + expr + rparen)


expr <<= infixNotation(arg,
    [
        (operator, 2, opAssoc.LEFT)  # AND, OR with left associativity
    ]
)



# Test the parser



print(expr.parseString("f(x AND (y OR z)) AND g(x)"))

