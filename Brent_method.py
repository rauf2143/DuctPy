from math import sqrt, log10, pi, ceil, floor

tolerance = 0.0001

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006
colebrook_correct = 0.00065


def brents(f, x0, x1, max_iter=50, tolerance=1e-5):
    fx0 = f(x0)
    fx1 = f(x1)

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

        if (3 * a + b) / 4 < s < b:
            s = (a + b) / 2
        elif mflag == True and abs(s - b) >= (abs(b - c) / 2):
            s = (a + b) / 2
        elif mflag == False and abs(s - b) >= (abs(c - d) / 2):
            s = (a + b) / 2
        elif mflag == True and abs(b - c) < abs(tolerance):
            s = (a + b) / 2
        elif mflag == False and abs(c - d) < abs(tolerance):
            s = (a + b) / 2
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
    print("Steps taken: " + str(steps))
    print("Friction Factor: " + str(b + .00065))
    return b


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

    h_loss = (brent_solver(0.01, 0.04, colebrook_eq) + 0.00065) * (st_length / (eq_dia / 12)) * (
            density / 32.174) * (
                     pow(fps, 2) / 2) / 144 * 27.679904842545
    return round(h_loss, 4)

def dim2_func(cfm_seg, limit_inch):
    def dim2_eq(var):
        return h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

    dim_work = brent_solver(2, 98, dim2_eq)
    return dim_work

# def func(x):
# return x-4


f = lambda x: x ** 2 - 4

root = dim2_func(1200, 20)

# root, steps = brents(func, -10, 10)
# print(str(brents(f, -10, 10)))
print("Root is: " + str(root))
# print("Steps taken: " + str(steps))
