from math import sqrt, log10, pi, ceil, floor


class Fluid:
    def __init__(self):
        self.density = 0.075
        self.viscosity = 0.0432


class Duct:
    def __init__(self):
        self.density = 0.075
        self.viscosity = 0.0432
        self.roughness = 0.006
        self.h_loss_ideal = 0.08
        self.st_length = 100
        self.width = 0
        self.height = 0
        self.cfm = 0
        self.eq_dia = 0
        self.eq_area = 0
        self.fpm = 0
        self.fps = 0
        self.reynolds = 0
        self.h_loss = 0

    def brent_solver(self, a, b, func, tolerance):
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
        # print("Brent mine Steps taken: " + str(steps))
        # print("Brent mine Friction Factor: " + str(b + .00065))
        return b

    def h_loss_func(self):
        self.eq_dia = 1.3 * pow((self.width * self.height), 0.625) / pow((self.width + self.height), 0.25)
        self.eq_area = pi * pow(self.eq_dia, 2) / 4 / 144
        self.fpm = self.cfm / self.eq_area
        self.fps = self.fpm / 60
        self.reynolds = self.density * self.fpm * 60 * self.eq_dia / 12 / self.viscosity

        self.h_loss = (self.brent_solver(0.01, 0.04, self.colebrook_eq, 0.0001) + 0.00065) * (
                    self.st_length / (self.eq_dia / 12)) * (self.density / 32.174) * (
                                  pow(self.fps, 2) / 2) / 144 * 27.679904842545
        return round(self.h_loss, 4)

    def colebrook_eq(self, var):
        lhs = 1 / sqrt(var)
        rhs = -2 * log10((self.roughness / (3.7 * self.eq_dia)) + (2.51 / (self.reynolds * sqrt(var))))
        # print(str(eq_dia))
        return lhs - rhs


class Line(Fluid, Duct):
    def __init__(self, number, total_cfm, inst_cfm, parent=0, diffuser=0):
        super().__init__()
        self.number = number
        self.total_cfm = total_cfm
        self.inst_cfm = inst_cfm
        self.parent = parent
        self.diffuser = diffuser

    def select_diffuser(self):
        assert 1 <= self.inst_cfm <= 1875, "Diffuser selection out of range"

        if 0 <= self.inst_cfm <= 75:
            self.diffuser = 6
        elif 76 <= self.inst_cfm <= 169:
            self.diffuser = 9
        elif 170 <= self.inst_cfm <= 300:
            self.diffuser = 12
        elif 301 <= self.inst_cfm <= 469:
            self.diffuser = 15
        elif 470 <= self.inst_cfm <= 675:
            self.diffuser = 18
        elif 676 <= self.inst_cfm <= 909:
            self.diffuser = 21
        elif 910 <= self.inst_cfm <= 1200:
            self.diffuser = 24
        elif 1201 <= self.inst_cfm <= 1875:
            self.diffuser = 30
        else:
            print("Diffuser out of range")

    def initialize(self):
        if self.diffuser == 1:
            self.select_diffuser()

    def print_data(self):
        print(
            '{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}'.format(self.cfm, self.width, self.height, self.h_loss, self.diffuser))


class Segment:
    def __init__(self, number, diffuser_cfm, cfm, parent=0, diffuser=0):
        self.number = number
        self.cfm = cfm
        self.diffuser_cfm = diffuser_cfm

        self.diffuser = diffuser
        self.parent = parent

        if self.diffuser == 1:
            self.select_diffuser()

        if self.parent != 0:
            self.type = "Branch"
            self.diffuser = 1

        elif self.parent == 0:
            self.type = "Mainline"

        self.name = self.type + "[" + str(self.number) + "]"
        self.length = 0
        self.fitting_len = 0

        # self.local_limit = 0
        self.width = 0
        self.height = 0
        # self.dumdim = 0
        self.h_loss = 0

    def solve_branch(self):
        if self.width != 0 and self.height != 0:
            print("Duct is overdimensioned")
            # self.dumdim = d2_solver(self.cfm, self.width)
        elif self.height != 0:
            self.width = d2_solver(self.cfm, self.height)
        elif self.width != 0:
            self.height = d2_solver(self.cfm, self.width)
        else:
            print("No limit to solve")

        # self.width = max(self.dumdim, self.local_limit)
        # self.height = min(self.dumdim, self.local_limit)
        self.h_loss = h_loss_func(self.cfm, self.width, self.height)
