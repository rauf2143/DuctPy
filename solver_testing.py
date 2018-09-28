from math import sqrt, log10, pi, ceil, floor

tolerance = 0.0001

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006
colebrook_correct = 0.00065


def secant_solver(guess, guess2, func_eval):
    x0 = guess
    x1 = guess2
    steps = 0

    for j in range(1, 100):
        if abs(x1 - x0) < tolerance:
            x1 = x1
            print("Secant Steps taken: " + str(steps))
            print("Secant Friction Factor: " + str(x1 + .00065))
            return x1, steps

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


def brents(x0, x1, f):
    fx0 = f(x0)
    fx1 = f(x1)
    max_iter = 50

    assert (fx0 * fx1) <= 0, "Root not bracketed"

    if abs(fx0) < abs(fx1):
        x0, x1 = x1, x0
        fx0, fx1 = fx1, fx0

    x2, fx2 = x0, fx0

    mflag = True
    steps_taken = 0

    while steps_taken < max_iter and abs(x1 - x0) > tolerance:
        fx0 = f(x0)
        fx1 = f(x1)
        fx2 = f(x2)

        if fx0 != fx2 and fx1 != fx2:
            L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
            L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
            L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
            new = L0 + L1 + L2

        else:
            new = x1 - ((fx1 * (x1 - x0)) / (fx1 - fx0))

        if ((new < ((3 * x0 + x1) / 4) or new > x1) or
                (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2)) or
                (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2)) or
                (mflag == True and (abs(x1 - x2)) < tolerance) or
                (mflag == False and (abs(x2 - d)) < tolerance)):
            new = (x0 + x1) / 2
            mflag = True

        else:
            mflag = False

        fnew = f(new)
        d, x2 = x2, x1

        if (fx0 * fnew) < 0:
            x1 = new
        else:
            x0 = new

        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0

        steps_taken += 1
    print("Brent other Steps taken: " + str(steps_taken))
    print("Brent other Friction Factor: " + str(x1 + .00065))
    return x1, steps_taken


def brent_solver(a, b, func):
    # if func(a) * func(b) >= 0:
    # return 0, 0

    if abs(func(a)) < abs(func(b)):
        a, b = b, a
    c = a
    mflag = True
    steps = 0

    while steps < 100 and abs(b - a) > tolerance:
        if func(a) != func(c) and func(b) != func(c):
            s1 = (a * func(b) * func(c)) / ((func(a) - func(b)) * (func(a) - func(c)))
            s2 = (b * func(a) * func(c)) / ((func(b) - func(a)) * (func(b) - func(c)))
            s3 = (c * func(a) * func(b)) / ((func(c) - func(a)) * (func(c) - func(b)))
            s = s1 + s2 + s3

        else:
            s = b - func(b) * (b - a) / (func(b) - func(a))

        if s < (3 * a + b) / 4 or s > b:
            s = (a + b) / 2
            mflag = True
        elif mflag is True and abs(s - b) >= (abs(b - c) / 2):
            s = (a + b) / 2
            mflag = True
        elif mflag is False and abs(s - b) >= (abs(c - d) / 2):
            s = (a + b) / 2
            mflag = True
        elif mflag is True and abs(b - c) < abs(tolerance):
            s = (a + b) / 2
            mflag = True
        elif mflag is False and abs(c - d) < abs(tolerance):
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False

        d = c
        c = b
        if func(a) * func(s) < 0:
            b = s
        else:
            a = s

        if abs(func(a)) < abs(func(b)):
            a, b = b, a

        steps += 1
    print("Brent mine Steps taken: " + str(steps))
    print("Brent mine Friction Factor: " + str(b + .00065))
    return b, steps


def h_loss_func(cfm, dim1, dim2, f):
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

    h_loss = (f(0.01, 0.04, colebrook_eq)[0] + 0.00065) * (st_length / (eq_dia / 12)) * (
            density / 32.174) * (
                     pow(fps, 2) / 2) / 144 * 27.679904842545
    return round(h_loss, 4)


def dim2_func(cfm_seg, limit_inch):
    def dim2_eq(var):
        return h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

    dim_work, steps = brent_solver(2, 98, dim2_eq)
    print(str(dim_work))
    print(str(steps))
    return dim_work


# def func(x):
# return x-4


f = lambda x: x ** 2 - 4
cfm = int(input("CFM: "))
width = int(input("Width: "))
height = int(input("Height: "))


# root_brent_other = []
# root_brent_mine = []
# root_secant = []


def range_create(n):
    return list(range(100, n + 100))


def numbers(n):
    return [i for i in range(100, n, 100)]


# print(numbers(10000))

# cfm = list(range(100, 10000, 100))

"""for i in range(1, len(cfm)):
    width = 18
    height = 12

    root_brent_other.append(h_loss_func(cfm[i], width, height, brents))

    root_brent_mine.append(h_loss_func(cfm[i], width, height, brent_solver))

    root_secant.append(h_loss_func(cfm[i], width, height, secant_solver))
    # root, steps = brents(func, -10, 10)
    # print(str(brents(f, -10, 10)))

print("Brent other Root is: " + str(root_brent_other))
print("Brent mine Root is: " + str(root_brent_mine))
print("Secant Root is: " + str(root_secant))
# print("Steps taken: " + str(steps))"""

root_brent_other = h_loss_func(cfm, width, height, brents)

root_brent_mine = h_loss_func(cfm, width, height, brent_solver)

root_secant = h_loss_func(cfm, width, height, secant_solver)

print("Brent other Root is: " + str(root_brent_other))
print("Brent mine Root is: " + str(root_brent_mine))
print("Secant Root is: " + str(root_secant))
