# This script finds the optimal combination of two
# passive components, e. g. for op amp gain or
# voltage regulator feedback networks.

import math
import numpy as np

############################
# -- INPUT VALUES BEGIN -- #
############################

# desired value
desired = 1900

# is desired value an upper bound?
# False: Find value that is closest to desired value
# True: Find value that is closest to desired value, but not bigger than desired value
is_upper_bound = False

# X range (powers of 10 supported)
x_start = 100
x_stop = 1000

# X values per decade (12, 24 and 48 supported)
x_e_row_ = {'e12', 'e24', 'e48'}

# Y range (powers of 10 supported)
y_start = 100
y_stop = 1000

# Y values per decade (12, 24 and 48 supported)
y_e_row_ = {'e12', 'e24', 'e48'}

# Select desired formula by un-commenting lambda or add own lambda
# func = lambda x,y: (2 * x/y) + 1                                    # instrumentation amplifier gain
# func = lambda x,y: (x*y) / (x+y)                                    # parallel resistors
# func = lambda x,y: x + y                                            # series resistors
# func = lambda x,y: x + x + y                                        # series resistors x3
# func = lambda x,y: 1.016 * (x/y + 1)                                # LM43601 DC/DC switching converter output voltage
# func = lambda x,y: (1.2/y) * (x + y)                                # LM43601 DC/DC swichting converter shutdown voltage
# func = lambda x,y: 1.21 * (1 + (y/x)) + (3e-6 * x)                  # TPS73801 LDO output voltage
# func = lambda x,y: y/(x+y)                                          # voltage divider (desired value is "amplification" e.g. 0.5 for a divider that divides in half)
# func = lambda x,y: 1.23 * (1 + x/y) + (-20e-9 * x)                  # LP2954 output voltage
# func = lambda x,y: 1/(2*math.pi * (350 + 2*x) * y/1e9)              # differential analog filter on GMS (with "R2" in "nF")
func = lambda x,y: 1/(2*math.pi * (350 + 2*x) * (y/1e9 + 0.5/1e9))  # combined DM+CM analog filter on GMS (with "R2" in "nF" and 1 nF from each line to ground as CM part)

##########################
# -- INPUT VALUES END -- #
##########################

# E-12 base values
e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

# E-24 base values
e24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

# E-48 base values
e48 = [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
       1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
       3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
       5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53]

# TODO: E-96 base values
#e96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10,

# get number of decades between two values
def get_decades(start, stop):
    decades = 0
    while start * 10 <= stop:
        start *= 10
        decades += 1
    return decades

def get_start_decade(start: float):
    num = start
    if num >= 1:
        index = 0
        while num > 10:
            num /= 10
            index += 1
        return 10**index 
    elif num > 0:
        index = 1
        while num < 10:
            num *= 10
            index -= 1
        return 10**index 
    else:
        return None


def get_base_values(erows: set[str]) -> set[float]:
    # base value sets per e-row
    e12 = {1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2}
    e24 = {1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1}
    e48 = {1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
        1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
        3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
        5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53}

    base_values = set()
    for erow in erows:
        if erow == 'e12':
            base_values.update(e12)
        elif erow == 'e24':
            base_values.update(e24)
        elif erow == 'e48':
            base_values.update(e48)
        else:
            print('invalid e-row')

    return base_values

def get_values(start: float, stop: float, base_values: set[float]):
    first_decade = get_start_decade(start)
    no_of_decades = get_decades(first_decade, stop) + 1
 
    decades = [first_decade]
    for i in range(no_of_decades):
        decades.append(decades[i] * 10)

    for decade in decades:
        for base_value in base_values:
            value = decade * base_value
            # print(value)
            if start <= value <= stop:
                yield value

# find and print best values on screen
def print_best_values(f):
    # pre-set best difference to some big value
    best_diff = 99999999

    # buffer for best values
    x_best = 0
    y_best = 0
    desired_best = 0
    
    # find best values by testing every possible combination
    for i in get_values(x_start, x_stop, get_base_values(x_e_row_)):
        for j in get_values(y_start, y_stop, get_base_values(y_e_row_)):
            result = f(i, j)

            # find best value that is smaller than the desired value
            if is_upper_bound:
                diff = desired - result
                if (diff < best_diff) and (diff >= 0):
                    best_diff = diff
                    x_best = i
                    y_best = j
                    desired_best = result
            # find best value
            else:
                diff = abs(desired - result)
                if (diff < best_diff):
                    best_diff = diff
                    x_best = i
                    y_best = j
                    desired_best = result

    # print best values
    print(f"best value for R1:       {round(x_best, 2)}")
    print(f"best value for R2:       {round(y_best, 2)}")
    print(f"best result:             {round(desired_best, 3)}")

# find and print best values
print_best_values(func)

# print(get_base_values({'e12', 'e24', 'e48'}))

# print(get_start_decade(0.5))

# for val in get_values(10, 100, get_base_values({'e12'})):
#     print(val)
#     pass
