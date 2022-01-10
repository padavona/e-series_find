# This script finds the optimal combination of two
# passive components, e. g. for op amp gain or
# voltage regulator feedback networks.

import math

############################
# -- INPUT VALUES BEGIN -- #
############################

# desired value
x = 1900

# is desired value an upper bound?
# False: Find value that is closest to desired value
# True: Find value that is closest to desired value, but not bigger than desired value
is_upper_bound = False

# R1 range (powers of 10 supported)
r1_start = 100
r1_stop = 1000

# R1 values per decade (12, 24 and 48 supported)
r1_e_row = 24

# R2 range (powers of 10 supported)
r2_start = 100
r2_stop = 1000

# R2 values per decade (12, 24 and 48 supported)
r2_e_row = 24

# Select desired formula by un-commenting lambda or add own lambda
# func = lambda x,y: (2 * x/y) + 1                                    # instrumentation amplifier gain
# func = lambda x,y: (x*y) / (x+y)                                    # parallel resistors
# func = lambda x,y: x + y                                            # series resistors
# func = lambda x,y: x + x + y                                        # series resistors x3
# func = lambda x,y: 1.016 * (x/y + 1)                                # LM43601 DC/DC switching converter output voltage
# func = lambda x,y: (1.2/y) * (x + y)                                # LM43601 DC/DC swichting converter shutdown voltage
# func = lambda x,y: 1.21 * (1 + (y/x)) + (0.000003 * x)              # TPS73801 LDO output voltage
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

# get number of decades between resistor value a and b
def get_decades(a, b):
    decades = 0
    while a * 10 <= b:
        a = a * 10
        decades += 1
    return decades


# create list of resistor values in range a...b that are in E-Row e
def create_values(a, b, e):
    total_values = e * get_decades(a, b)
    values = []
    index = 0
    decade = 1

    if e == 12:
        e_values = e12
    elif e == 24:
        e_values = e24
    else:
        e_values = e48

    while index < total_values:
        values.append(a * e_values[index % e] * decade)
        if (index % e) == (e - 1):
            decade *= 10
        index += 1

    return values


# find and print best values on screen
def print_best_values(r1, r2, f):
    # pre-set best difference to some big value
    best_diff = 99999999

    # buffer for best values
    r1_best = 0
    r2_best = 0
    a_best = 0
    
    # find best values by testing every possible combination
    for i in r1:
        for j in r2:
            A = f(i, j)

            # find best value that is smaller than the desired value
            if is_upper_bound:
                diff = x - A
                if (diff < best_diff) and (diff >= 0):
                    best_diff = diff
                    r1_best = i
                    r2_best = j
                    a_best = A
            # find best value
            else:
                diff = abs(x - A)
                if (diff < best_diff):
                    best_diff = diff
                    r1_best = i
                    r2_best = j
                    a_best = A

    # print best values
    print("best value for R1:       ", round(r1_best, 2), "Ohm (E-" + str(r1_e_row) + ")")
    print("best value for R2:       ", round(r2_best, 2), "Ohm (E-" + str(r2_e_row) + ")")
    print("best result:             ", round(a_best, 3))

# create full set of E-row values
r1 = create_values(r1_start, r1_stop, r1_e_row)
r2 = create_values(r2_start, r2_stop, r2_e_row)

# find and print best values
print_best_values(r1, r2, func)
