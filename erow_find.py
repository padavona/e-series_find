# This script finds the optimal combination of two values
# that are within an e-series of preferred numbers

from typing import Generator, Callable
import math

############################
# -- INPUT VALUES BEGIN -- #
############################

# desired value
DESIRED = 200

# is desired value an upper bound?
# False: Find value that is closest to desired value
# True: Find value that is closest to desired value, but not bigger than desired value
IS_UPPER_BOUND = False

# X range
X_START = 2000
X_STOP = 20000

# set of e-series (e12, e24, e48 and e96 supported),
# e. g. X_E_SERIES = {"e12, "e24"}
X_E_SERIES = {"e12", "e24"}

# Y range
Y_START = 100
Y_STOP = 400

# set of e-series (e12, e24, e48 and e96 supported),
# e. g. Y_E_SERIES = {"e12, "e24"}
Y_E_SERIES = {"e12", "e24"}

# Select desired formula by un-commenting lambda or add own lambda
func = lambda x, y: (2 * x / y) + 1  # instrumentation amplifier gain
# func = lambda x, y: (x * y) / (x + y)  # parallel resistors
# func = lambda x, y: x + y  # series resistors
# func = lambda x, y: x + x + y  # series resistors x3
# func = lambda x, y: 1.016 * (x / y + 1)  # LM43601 DC/DC switching converter output voltage
# func = lambda x, y: (1.2 / y) * (x + y)  # LM43601 DC/DC swichting converter shutdown voltage
# func = lambda x, y: 1.21 * (1 + (y / x)) + (3e-6 * x)  # TPS73801 LDO output voltage
# func = lambda x, y: y / (x + y)  # voltage divider (desired value is "output" to "input" voltage)
# func = lambda x, y: 1.23 * (1 + x / y) + (-20e-9 * x)  # LP2954 output voltage
# func = lambda x, y: 1 / (2 * math.pi * (350 + 2 * x) * y)  # differential analog filter on GMS
# func = lambda x, y: 1 / (
#     2 * math.pi * (350 + 2 * x) * (y / 1e9 + 0.5 / 1e9)
# )  # combined DM+CM analog filter on GMS (with "R2" in "nF" and 1 nF from each line to ground as CM part)

##########################
# -- INPUT VALUES END -- #
##########################

# base values
E12_BASE = {1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2}
E24_BASE = {
    1.0,
    1.1,
    1.2,
    1.3,
    1.5,
    1.6,
    1.8,
    2.0,
    2.2,
    2.4,
    2.7,
    3.0,
    3.3,
    3.6,
    3.9,
    4.3,
    4.7,
    5.1,
    5.6,
    6.2,
    6.8,
    7.5,
    8.2,
    9.1,
}
E48_BASE = {
    1.00,
    1.05,
    1.10,
    1.15,
    1.21,
    1.27,
    1.33,
    1.40,
    1.47,
    1.54,
    1.62,
    1.69,
    1.78,
    1.87,
    1.96,
    2.05,
    2.15,
    2.26,
    2.37,
    2.49,
    2.61,
    2.74,
    2.87,
    3.01,
    3.16,
    3.32,
    3.48,
    3.65,
    3.83,
    4.02,
    4.22,
    4.42,
    4.64,
    4.87,
    5.11,
    5.36,
    5.62,
    5.90,
    6.19,
    6.49,
    6.81,
    7.15,
    7.50,
    7.87,
    8.25,
    8.66,
    9.09,
    9.53,
}
E96_BASE = {
    1.00,
    1.02,
    1.05,
    1.07,
    1.10,
    1.13,
    1.15,
    1.18,
    1.21,
    1.24,
    1.27,
    1.30,
    1.33,
    1.37,
    1.40,
    1.43,
    1.47,
    1.50,
    1.54,
    1.58,
    1.62,
    1.65,
    1.69,
    1.74,
    1.78,
    1.82,
    1.87,
    1.91,
    1.96,
    2.00,
    2.05,
    2.10,
    2.15,
    2.21,
    2.26,
    2.32,
    2.37,
    2.43,
    2.49,
    2.55,
    2.61,
    2.67,
    2.74,
    2.80,
    2.87,
    2.94,
    3.01,
    3.09,
    3.16,
    3.24,
    3.32,
    3.40,
    3.48,
    3.57,
    3.65,
    3.74,
    3.83,
    3.92,
    4.02,
    4.12,
    4.22,
    4.32,
    4.42,
    4.53,
    4.64,
    4.75,
    4.87,
    4.99,
    5.11,
    5.23,
    5.36,
    5.49,
    5.62,
    5.76,
    5.90,
    6.04,
    6.19,
    6.34,
    6.49,
    6.65,
    6.81,
    6.98,
    7.15,
    7.32,
    7.50,
    7.68,
    7.87,
    8.06,
    8.25,
    8.45,
    8.66,
    8.87,
    9.09,
    9.31,
    9.53,
    9.76,
}


def get_decades(start: float, stop: float) -> int:
    decades = 1
    while start * 10 <= stop:
        start *= 10
        decades += 1
    return decades


def get_start_decade(start: float) -> float:
    num = start
    if num >= 1:
        index = 0
        while num > 10:
            num /= 10
            index += 1
        return 10 ** index
    elif num > 0:
        index = 1
        while num < 10:
            num *= 10
            index -= 1
        return 10 ** index
    else:
        return None


def get_e_series(value: float) -> Generator[str, None, None]:
    assert value > 0, "value has to be greater than 0"

    if value >= 10:
        while value >= 10:
            value /= 10
    elif value < 1.0:
        while value < 1.0:
            value *= 10

    value = round(value, 2)

    if value in E12_BASE:
        yield "E-12"
    if value in E24_BASE:
        yield "E-24"
    if value in E48_BASE:
        yield "E-48"
    if value in E96_BASE:
        yield "E-96"


def get_base_values(e_series: set[str]) -> set[float]:
    base_values = set()
    for series in e_series:
        if series == "e12":
            base_values.update(E12_BASE)
        elif series == "e24":
            base_values.update(E24_BASE)
        elif series == "e48":
            base_values.update(E48_BASE)
        elif series == "e96":
            base_values.update(E96_BASE)
        else:
            print("invalid e-series")

    return base_values


def get_values(start: float, stop: float, base_values: set[float]) -> Generator[float, None, None]:
    first_decade = get_start_decade(start)
    no_of_decades = get_decades(first_decade, stop)

    decades = []
    decades.append(first_decade)
    for i in range(no_of_decades):
        decades.append(decades[i] * 10)

    for decade in decades:
        for base_value in base_values:
            value = decade * base_value
            if start <= value <= stop:
                yield value


def print_best_values(f: Callable) -> None:
    assert X_START <= X_STOP, "Stop value (X) has to be greater than or equal start value"
    assert Y_START <= Y_STOP, "Stop value (Y) has to be greater than or equal start value"
    assert X_START != 0, "Start value (X) cannot be 0"
    assert Y_START != 0, "Start value (Y) cannot be 0"

    # pre-set best difference to some big value
    best_diff = 99999999

    # buffer for best values
    x_best = 0
    y_best = 0
    desired_best = 0

    # find best values by testing every possible combination
    no_x_values = True
    no_y_values = True
    for x in get_values(X_START, X_STOP, get_base_values(X_E_SERIES)):
        no_x_values = False
        for y in get_values(Y_START, Y_STOP, get_base_values(Y_E_SERIES)):
            no_y_values = False
            result = f(x, y)

            # find best value that is smaller than the desired value
            if IS_UPPER_BOUND:
                diff = DESIRED - result
                if (diff < best_diff) and (diff >= 0):
                    best_diff = diff
                    x_best = x
                    y_best = y
                    desired_best = result
            # find best value
            else:
                diff = abs(DESIRED - result)
                if diff < best_diff:
                    best_diff = diff
                    x_best = x
                    y_best = y
                    desired_best = result

    # print best values
    if no_x_values == True or no_y_values == True:
        print("At least one given range does not contain any e-values")
    else:
        print("best value for X:   {} ({})".format(round(x_best, 2), ", ".join(get_e_series(x_best))))
        print("best value for Y:   {} ({})".format(round(y_best, 2), ", ".join(get_e_series(y_best))))
        print("best result:        {}".format(round(desired_best, 4)))
        print("error to desired:   {} %".format(round((desired_best - DESIRED) / DESIRED * 100, 3)))


def main():
    try:
        print_best_values(func)
    except AssertionError as e:
        print(f"Assertion failed: {e}")


if __name__ == "__main__":
    main()
