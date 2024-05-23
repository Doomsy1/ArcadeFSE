import numpy as np
import timeit

a = 10
b = 5
# Bit operations in Python
def python_bit_operations():
    result = a & b  # Bitwise AND
    result = a | b  # Bitwise OR
    result = a ^ b  # Bitwise XOR
    result = ~a     # Bitwise NOT
    result = a << 2 # Bitwise left shift
    result = a >> 2 # Bitwise right shift

# Bit operations in NumPy
c = np.array([10])
d = np.array([5])
def numpy_bit_operations():
    result = np.bitwise_and(c, d)  # Bitwise AND
    result = np.bitwise_or(c, d)   # Bitwise OR
    result = np.bitwise_xor(c, d)  # Bitwise XOR
    result = np.bitwise_not(c)     # Bitwise NOT
    result = np.left_shift(c, 2)   # Bitwise left shift
    result = np.right_shift(c, 2)  # Bitwise right shift

# Measure the execution time of Python bit operations
python_time = timeit.timeit(python_bit_operations, number=100000)

# Measure the execution time of NumPy bit operations
numpy_time = timeit.timeit(numpy_bit_operations, number=100000)

print(f"Python bit operations: {python_time} seconds")
print(f"NumPy bit operations: {numpy_time} seconds")