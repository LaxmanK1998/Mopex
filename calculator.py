# This is the calculator file required for Mopex
# Importing required libraries
import math

# Defining required constants
pi = math.pi
e = math.e

# -----Basic functions---------------------------------------------------------------------------

# Add 2 Numbers
def addition(a, b):
    return a + b

# Subtract 2 Numbers
def subtraction(y, z):
    return y - z

# Calculate absolute value of 2 Numbers
def absolute(c, d):
    if c > d:
        return c - d
    else:
        return d - c

# Multiply 2 Numbers
def multiplication(k, f):
    return k * f

# Divide 2 numbers
def division(g, h):
    return g / h

# Calculate modulo of 2 numbers
def modulo(j, k):
    return j % k

# Calculate sine of number
def sin(i):
    return math.sin(i)

# Calculate cosine of number
def cos(i):
    return math.cos(i)

# Calculate tangent of number
def tan(i):
    return math.tan(i)

# Calculate square of a number
def square(a):
    return a * a

# Calculate cube of a number
def cube(a):
    return a * a * a

# Raise a number to a power
def power(num, pow):
    result = 1
    for i in range(pow):
        result = result * num
    return result

#Calculate square root
def root(a):
    return math.sqrt(a)

# Calculate cube root
def cuberoot(a):
    return a**(1/3)

# Calculate nth root
def nthroot(num, power):
    return num**(1/power)

# ----Advanced functions---------------------------------------------------------------------

# Calculate natural log
def naturallog(n):
    return math.log(n)
# Calculate common log
def commonlog(n):
    return math.log10(n)

# Invert number
def invert(x):
    return (1/x)

# Calculate factorial

def factorial(n):
   
    if n == 1:
        return 1
    elif n <= 0:
        print("Invalid Input")
    else:
        return n * factorial(n - 1)

# Calculate Combination
def combination(k, r):
    return factorial(k) * invert((factorial(k-r))*factorial(r))

# Calculate permutation
def permutation(k, r):
    return factorial(k) * invert((factorial(k-r)))


# Add calculator memory using lists
memory = []
total = 0
running = True

# While loop running to take input
while running:
    operation = input("Enter your operator. Enter 'help' for list of operations or enter 'quit' to exit: ")
    if operation == "quit" or operation == "QUIT" or operation == "Quit":
        print("Goodbye")
        running = False
    elif operation == "help" or operation == "HELP" or operation == "Help":
        print("Here are the operations you can give to this calculator program.\n Left side shows operand name and right side shows the keyword")
        print("Addition : +")
        print("Subtraction: -")
        print("Absolute value: ||")
        print("Multiplication: *")
        print("Division: /")
        print("Modulo: %")
        print("Sine: sin")
        print("Cosine: cos")
        print("Tangent: tan")
        print("Square: ^2")
        print("Cube: ^3")
        print("Power: ^n")
        print("Square root: ^(1/2)")
        print("Cube root: ^(1/3)")
        print("n'th root: ^(1/n)")
        print("Natural log: loge")
        print("Common log: log10")
        print("Invert number: 1/x")
        print("Factorial: !")
        print("Permutation: nPr")
        print("Combination: nCr")
    else:
        print("Invalid input. Please try again. Enter 'help' for a list of operation")

