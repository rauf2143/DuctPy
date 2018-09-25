from math import sqrt, log10, pi, floor, ceil

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006
colebrook_correct = 0.00065


def secant_solver(guess, guess2, correct, func_eval):
    x0 = guess
    x1 = guess2

    for j in range(1, 100):
        if abs(x1 - x0) < 0.00001:
            x1 = x1 + correct
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

    h_loss = secant_solver(0.02, 0.03, colebrook_correct, colebrook_eq) * (st_length / (eq_dia / 12)) * (
            density / 32.174) * (
                     pow(fps, 2) / 2) / 144 * 27.679904842545
    # print("h_loss = " + str(round(h_loss, 5)) + " in. WC / 100 ft")
    return round(h_loss, 4)


def d2_solver(cfm, user_limit):
    if user_limit >= 100:
        limit = user_limit / 25
    else:
        limit = user_limit

    def dim2_func(cfm, limit):

        def dim2_eq(var):
            return h_loss_func(cfm, limit, var) - h_loss_ideal

        dim_work = secant_solver(2, 6, 0, dim2_eq)

        """if dim_work % 2 < 0.5:
            return dim_work

        elif ceil(dim_work) % 2 < 1:
            return dim_work + 1

        else:
            return dim_work + 1"""
        # print(str(dim_work))
        return dim_work

    def rounding_func(dim_round):
        if dim_round % 2 <= 0.5:
            dim_inch = floor(dim_round)

        elif 0.5 < dim_round % 2 <= 1:
            dim_inch = ceil(dim_round) + 1

        else:
            dim_inch = ceil(dim_round)

        if user_limit >= 100:
            return dim_inch * 25

        else:
            return dim_inch

    d2_to_round = dim2_func(cfm, limit)
    # print(str(d2_to_round))

    d2_final = rounding_func(d2_to_round)
    # print(str(d2_final))

    return d2_final


def diff_lim_sel(cfm, list):
    if list.diffuser == 1:
        if 0 <= cfm <= 75:
            list.diffuser = 6
        elif 76 <= cfm <= 169:
            list.diffuser = 9
        elif 170 <= cfm <= 300:
            list.diffuser = 12
        elif 301 <= cfm <= 469:
            list.diffuser = 15
        elif 470 <= cfm <= 675:
            list.diffuser = 18
        elif 676 <= cfm <= 909:
            list.diffuser = 21
        elif 910 <= cfm <= 1200:
            list.diffuser = 24
        elif 1201 <= cfm <= 1875:
            list.diffuser = 30
        else:
            print("Diffuser out of range")

        if list.diffuser % 2 == 0:
            list.local_limit = list.diffuser + 2
        else:
            list.local_limit = list.diffuser + 3

    elif list.diffuser > 1:
        list.local_limit = list.diffuser

    else:
        list.local_limit = ceiling_limit


class Segment:
    def __init__(self, number, diffuser_cfm, cfm, parent=0, diffuser=0):
        self.number = number
        self.cfm = cfm
        self.diffuser_cfm = diffuser_cfm
        self.diffuser = diffuser
        self.parent = parent

        if self.parent != 0:
            self.type = "Branch"
            self.diffuser = 1

        elif self.parent == 0:
            self.type = "Mainline"

        self.name = self.type + "[" + str(self.number) + "]"
        self.length = 0
        self.fitting_len = 0

        self.local_limit = 0
        self.width = 0
        self.height = 0
        self.dumdim = 0
        self.h_loss = 0

    def solve_branch(self):

        # if self.parent != 0:

        """if self.diffuser == 1:
            self.diffuser = diff_sel(self.diffuser_cfm)
            if diff_sel(self.diffuser_cfm) % 2 == 0:
                self.local_limit = self.diffuser + 2
            else:
                self.local_limit = self.diffuser + 3
        elif self.diffuser > 1:
            self.local_limit = self.diffuser
        else:
            self.local_limit = ceiling_limit"""

        self.dumdim = d2_solver(self.cfm, self.local_limit)

        self.width = max(self.dumdim, self.local_limit)
        self.height = min(self.dumdim, self.local_limit)
        self.h_loss = h_loss_func(self.cfm, self.width, self.height)

    def print_data(self):
        print(
            '{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}'.format(self.name, self.cfm, self.width, self.height,
                                                                       self.length, self.h_loss, self.diffuser))

    # def input_data(self)

    # def lim_in(self, limit):
    # self.local_limit = limit


print("Python Duct Sizer v0.1.9.25")
print("Author: Ahsan Rauf")
print("asn.rauf@gmail.com")
print("Enter CFM List. Enter -1 to stop. Numerical values only.")

alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
            "V", "W", "X", "Y", "Z"]

ceiling_limit = int(input("Enter overall ceiling limit: "))
cfm_running = 0
mainline = [Segment("dummy", 0, -1)]
branch = [Segment("dummy", 0, -1)]

for i in range(1, 20):
    print("Enter CFM " + str(i) + ": ")
    cfm_inst = int(input())

    if cfm_inst == -1:
        break
    else:
        print("Enter if branch")
        branch_if = int(input())

    cfm_running += cfm_inst

    if branch_if == 1:
        branch.append(Segment(i, cfm_inst, cfm_inst, i))
        mainline.append(Segment(i, cfm_inst, cfm_running))

    elif branch_if == 0:
        mainline.append(Segment(i, cfm_inst, cfm_running, 0, 1))

print('{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}'.format('Segment', 'CFM', 'Width', 'Height', 'Length',
                                                                 'Head Loss', 'Diffuser'))

for i in range(1, len(branch)):
    diff_lim_sel(branch[i].diffuser_cfm, branch[i])

for i in range(1, len(branch)):
    branch[i].solve_branch()
    if branch[i].number == mainline[i].number:
        mainline[i].local_limit = max(mainline[i].local_limit, branch[i].height + 2)
        #else:
            #mainline[i].local_limit

for i in range(1, len(mainline)):

    if mainline[i].local_limit == 0:
        diff_lim_sel(mainline[i].diffuser_cfm, mainline[i])
        mainline[i].solve_branch()

    else:
        mainline[i].solve_branch()

    mainline[i].print_data()

for i in range(1, len(branch)):
    # branch[i].solve_branch()
    branch[i].print_data()

# lim_sel(branch, mainline)

# for i in range(0, len(branch)):
# branch[i].solve_branch()
# branch[i].print_data()
