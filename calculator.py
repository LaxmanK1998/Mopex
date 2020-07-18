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


#Take operation inputs and call respective function
keyword = input("Enter an operator: ")

# Add calculator memory using lists
memory = []

#while keyword != "exit":
    #