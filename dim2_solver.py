from math import sqrt, log10, pi, ceil, floor
import unittest
import time

# tolerance = 0.0001

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006


# colebrook_correct = 0.00065

def secant_solver(guess, guess2, func_eval, tolerance):
    x0 = guess
    x1 = guess2
    steps = 0

    for j in range(1, 100):
        if abs(x1 - x0) < tolerance:
            x1 = x1
            # print("Secant Steps taken: " + str(steps))
            # print("Secant Friction Factor: " + str(x1 + .00065))
            return x1

        elif j == 99:
            print("Solver Malfunction")
            return 0

        else:
            x2 = x1 - func_eval(x1) * (x1 - x0) / (func_eval(x1) - func_eval(x0))
            x0 = abs(x1)
            x1 = abs(x2)
            steps += 1
            # print("x1 is: " + str(x1))
            # print("x0 is: " + str(x0))


def d2_solver(cfm, user_limit):
    if user_limit >= 100:
        limit = user_limit / 25
    else:
        limit = user_limit

    def dim2_func(cfm_seg, limit_inch):

        def dim2_eq(var):
            return h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

        dim_work = secant_solver(2, 6, dim2_eq, 0.05)
        # print(str(dim_work))
        return dim_work

    def rounding_func(dim_round):
        dim_bound1 = floor(dim_round)
        dim_bound2 = ceil(dim_round)
        if dim_bound1 % 2 != 0:
            dim_bound1 -= 1
        if dim_bound2 % 2 != 0:
            dim_bound2 += 1

        if abs(h_loss_func(cfm, limit, dim_bound1) - h_loss_ideal) < abs(
                h_loss_func(cfm, limit, dim_bound2) - h_loss_ideal):
            dim_inch = dim_bound1
        else:
            dim_inch = dim_bound2

        if user_limit >= 100:
            return dim_inch * 25

        else:
            return dim_inch

    d2_to_round = dim2_func(cfm, limit)
    # print(str(d2_to_round))

    d2_final = rounding_func(d2_to_round)
    # print(str(d2_final))

    return d2_final


def h_loss_func(cfm, dim1, dim2):
    eq_dia = 1.3 * pow((dim1 * dim2), 0.625) / pow((dim1 + dim2), 0.25)
    assert eq_dia > 0, "Equivalent dia is zero"

    eq_area = pi * pow(eq_dia, 2) / 4 / 144
    # print(str(eq_area))
    fpm = cfm / eq_area
    fps = fpm / 60

    re = density * fpm * 60 * eq_dia / 12 / viscosity

    def colebrook_eq(var):
        lhs = 1 / sqrt(var)
        rhs = -2 * log10((roughness / (3.7 * eq_dia)) + (2.51 / (re * sqrt(var))))
        # print(str(eq_dia))
        return lhs - rhs

    h_loss = (secant_solver(0.01, 0.02, colebrook_eq, 0.0001) + 0.00065) * (st_length / (eq_dia / 12)) * (
            density / 32.174) * (
                     pow(fps, 2) / 2) / 144 * 27.679904842545
    return round(h_loss, 4)


def main():
    # cfm = int(input("CFM = "))
    # limit = int(input("Limit = "))
    # height = int(input("Height = "))
    limit = 12
    for i in range(100, 5000, 100):
        print("CFM = " + str(i))
        print("Limit = " + str(limit))
        print("Width = " + str(d2_solver(i, limit)))
        if i % 500 == 0:
            limit += 2


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(time.time() - start_time)


class MyTest(unittest.TestCase):
    def test(self):
        for i in range(100, 2000, 100):
            self.assertEqual(d2_solver(300, 6), 12)
