import unittest
from math import sqrt, log10, pi, ceil, floor

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006
#colebrook_correct = 0.00065


def secant_solver(guess, guess2, func_eval):
    x0 = guess
    x1 = guess2

    for j in range(1, 100):
        if abs(x1 - x0) < 0.00001:
            print(str(guess))
            print(str(guess2))
            print("f = " + str(x1))
            return x1

        elif j == 99:
            print("Solver Malfunction")
            return 0

        else:
            x2 = x1 - func_eval(x1) * (x1 - x0) / (func_eval(x1) - func_eval(x0))
            x0 = abs(x1)
            x1 = abs(x2)
            # print("x1 is: " + str(x1))
            # print("x0 is: " + str(x0))


def h_loss_func(cfm, dim1, dim2):
    eq_dia = 1.3 * pow((dim1 * dim2), 0.625) / pow((dim1 + dim2), 0.25)

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

    h_loss = (secant_solver(0.02, 0.03, colebrook_eq) + 0.00065) * (st_length / (eq_dia / 12)) * (
            density / 32.174) * (
                     pow(fps, 2) / 2) / 144 * 27.679904842545
    return round(h_loss, 4)


def dim2_func(cfm_seg, limit_inch):
    def dim2_eq(var):
        return h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

    dim_work = secant_solver(2, 6, dim2_eq)
    return dim_work


"""class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(secant_solver(0, 1, 0, f), 8)"""

print("Head Loss = " + str(h_loss_func(250, 10, 6)))

if abs(s-b) >= (abs(b-c) / 2):

if mflag = 1:
