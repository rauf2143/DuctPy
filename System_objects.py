from math import sqrt, log10, pi, ceil, floor
from time import time

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006


def secant_solver(guess, guess2, func_eval, tolerance):
    x0 = guess
    x1 = guess2
    steps = 0

    for j in range(1, 101):
        fx0 = func_eval(x0)
        fx1 = func_eval(x1)

        if abs(x1 - x0) < tolerance:
            x1 = x1
            return x1

        elif j == 100:
            print("Solver Malfunction")
            return 0

        else:
            x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
            x0 = abs(x1)
            x1 = abs(x2)
            steps += 1


class Duct:
    """Duct class represents all segments including mainlines and branches"""

    # registry = []

    def __init__(self, number, running_cfm, inst_cfm, parent=0, diffuser=1):
        self.registry.append(self)
        self.number = number
        self.cfm = running_cfm
        self.inst_cfm = inst_cfm

        self.diffuser = diffuser
        self.parent = parent

        if self.parent == 0 or isinstance(self.parent, str) is True:
            self.type = "Mainline"

        elif isinstance(self.parent, int) is True and self.parent != 0:
            self.type = "Branch"

        else:
            self.type = "Error"

        self.name = self.type + "[" + str(self.number) + "]"
        self.length = 0
        self.fitting_len = 0

        self.width = 0
        self.height = 0
        self.h_loss = 0
        self.solved = False

        if self.diffuser == 1:
            self.select_diffuser()

    def __str__(self):
        return '{0:<15}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}'.format(self.name, self.cfm, self.width, self.height,
                                                                          self.length, self.h_loss, self.diffuser)

    def d2_solver(self, cfm, dim1_user_dim):
        if dim1_user_dim >= 100:
            limit = dim1_user_dim / 25
        else:
            limit = dim1_user_dim

        def dim2_func(cfm_seg, limit_inch):

            def dim2_eq(var):
                return self.h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

            dim_work = secant_solver(2, 6, dim2_eq, 0.05)
            return dim_work

        def rounding_func(dim_round):
            dim_bound1 = floor(dim_round)
            dim_bound2 = ceil(dim_round)
            if dim_bound1 % 2 != 0:
                dim_bound1 -= 1
            if dim_bound2 % 2 != 0:
                dim_bound2 += 1

            if abs(self.h_loss_func(cfm, limit, dim_bound1) - h_loss_ideal) < abs(
                    self.h_loss_func(cfm, limit, dim_bound2) - h_loss_ideal):
                dim_inch = dim_bound1
            else:
                dim_inch = dim_bound2

            if dim1_user_dim >= 100:
                return dim_inch * 25

            else:
                return dim_inch

        d2_to_round = dim2_func(cfm, limit)

        d2_final = rounding_func(d2_to_round)

        return d2_final

    def h_loss_func(self, cfm, dim1, dim2):
        self.eq_dia = 1.3 * pow((dim1 * dim2), 0.625) / pow((dim1 + dim2), 0.25)
        assert self.eq_dia > 0, "Equivalent dia is zero"
        self.eq_area = pi * pow(self.eq_dia, 2) / 4 / 144
        self.fpm = cfm / self.eq_area
        self.fps = self.fpm / 60
        self.re = density * self.fpm * 60 * self.eq_dia / 12 / viscosity

        def colebrook_eq(var):
            lhs = 1 / sqrt(var)
            rhs = -2 * log10((roughness / (3.7 * self.eq_dia)) + (2.51 / (self.re * sqrt(var))))
            return lhs - rhs

        h_loss = (secant_solver(0.01, 0.02, colebrook_eq, 0.0001) + 0.00065) * (st_length / (self.eq_dia / 12)) * (
                density / 32.174) * (pow(self.fps, 2) / 2) / 144 * 27.679904842545
        return round(h_loss, 4)

    def solve_branch(self):
        if self.width != 0 and self.height != 0:
            print("Duct is overdimensioned")
        elif self.height != 0:
            self.width = self.d2_solver(self.cfm, self.height)
            self.solved = True
        elif self.width != 0:
            self.height = self.d2_solver(self.cfm, self.width)
            self.solved = True
        else:
            print("No limit to solve")
            return

        self.h_loss = self.h_loss_func(self.cfm, self.width, self.height)
        return

    def select_diffuser(self):
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

        if self.diffuser % 2 == 0:
            self.width = self.diffuser + 2
        else:
            self.width = self.diffuser + 3
        return


class Mainline(Duct):
    registry = []

    def limit_sel(self, branch):
        self.height = branch.height + 2
        return


class Branch(Duct):
    registry = []


def main():
    print("Python Duct Sizer v0.1.10.12")
    print("Author: Ahsan Rauf")
    print("asn.rauf@gmail.com")
    print("Enter CFM List. Enter -1 to stop. Numerical values only.")

    ceiling = int(input("Enter overall ceiling limit: "))
    cfm_running = 0

    for i in range(1, 20):
        # print("Enter CFM [" + str(i) + "]: ")
        cfm_inst = int(input("Enter CFM[" + str(i) + "]: "))

        if cfm_inst == -1:
            break

        else:
            print("Enter if branch")
            branch_if = int(input())

        cfm_running += cfm_inst

        if branch_if == 1:
            Branch(i, cfm_inst, cfm_inst, i)
            Mainline(i, cfm_running, cfm_inst, 0, 0)

        elif branch_if == 0:
            Mainline(i, cfm_running, cfm_inst, 0)

    print('{0:<15}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}'.format('Segment', 'CFM', 'Width', 'Height', 'Length',
                                                                     'Head Loss', 'Diffuser'))
    start_time = time()
    for m in Mainline.registry:
        for b in Branch.registry:
            if b.parent == m.number:
                b.solve_branch()
                m.limit_sel(b)

        m.solve_branch()
        print(m)

    print("Number of mainline segments = " + str(len(Mainline.registry)))

    for b in Branch.registry:
        print(b)

    print("Number of branches = " + str(len(Branch.registry)))
    print("Time to compute: " + str(round(time() - start_time, 4)) + " s")


if __name__ == '__main__':
    main()
