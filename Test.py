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

    def dim2_func(cfm_seg, limit_inch):

        def dim2_eq(var):
            return h_loss_func(cfm_seg, limit_inch, var) - h_loss_ideal

        dim_work = secant_solver(2, 6, 0, dim2_eq)
        # print(str(dim_work))
        return dim_work

    def rounding_func(dim_round):
        dim_bound1 = floor(dim_round)
        dim_bound2 = ceil(dim_round)
        if dim_bound1 % 2 != 0:
            dim_bound1 -= 1
        if dim_bound2 % 2 != 0:
            dim_bound2 += 1
        # bound1 = h_loss_func(cfm,user_limit,dim_bound1)-h_loss_ideal
        # bound2 = h_loss_func(cfm,user_limit,dim_bound2)-h_loss_ideal
        if abs(h_loss_func(cfm, limit, dim_bound1) - h_loss_ideal) < abs(
                h_loss_func(cfm, limit, dim_bound2) - h_loss_ideal):
            dim_inch = dim_bound1
        else:
            dim_inch = dim_bound2

        """if dim_round % 2 <= 0.5:
            dim_inch = floor(dim_round)

        elif 0.5 < dim_round % 2 <= 1:
            dim_inch = ceil(dim_round) + 1

        else:
            dim_inch = ceil(dim_round)"""

        if user_limit >= 100:
            return dim_inch * 25

        else:
            return dim_inch

    d2_to_round = dim2_func(cfm, limit)
    # print(str(d2_to_round))

    d2_final = rounding_func(d2_to_round)
    # print(str(d2_final))

    return d2_final


def diff_lim_sel(cfm, segment, ceiling):
    if segment.diffuser == 1:
        if 0 <= cfm <= 75:
            segment.diffuser = 6
        elif 76 <= cfm <= 169:
            segment.diffuser = 9
        elif 170 <= cfm <= 300:
            segment.diffuser = 12
        elif 301 <= cfm <= 469:
            segment.diffuser = 15
        elif 470 <= cfm <= 675:
            segment.diffuser = 18
        elif 676 <= cfm <= 909:
            segment.diffuser = 21
        elif 910 <= cfm <= 1200:
            segment.diffuser = 24
        elif 1201 <= cfm <= 1875:
            segment.diffuser = 30
        else:
            print("Diffuser out of range")

        if segment.diffuser % 2 == 0:
            segment.width = segment.diffuser + 2
        else:
            segment.width = segment.diffuser + 3

    elif segment.diffuser > 1:
        segment.width = segment.diffuser

    else:
        segment.height = ceiling


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

    def print_data(self):
        print(
            '{0:<20}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}'.format(self.name, self.cfm, self.width, self.height,
                                                                       self.length, self.h_loss, self.diffuser))
    def select_diffuser(self):
        if 0 <= self.diffuser_cfm <= 75:
            self.diffuser = 6
        elif 76 <= self.diffuser_cfm <= 169:
            self.diffuser = 9
        elif 170 <= self.diffuser_cfm <= 300:
            self.diffuser = 12
        elif 301 <= self.diffuser_cfm <= 469:
            self.diffuser = 15
        elif 470 <= self.diffuser_cfm <= 675:
            self.diffuser = 18
        elif 676 <= self.diffuser_cfm <= 909:
            self.diffuser = 21
        elif 910 <= self.diffuser_cfm <= 1200:
            self.diffuser = 24
        elif 1201 <= self.diffuser_cfm <= 1875:
            self.diffuser = 30
        else:
            print("Diffuser out of range")

    # def input_data(self)

    # def lim_in(self, limit):
    # self.local_limit = limit


def main():
    print("Python Duct Sizer v0.1.9.25")
    print("Author: Ahsan Rauf")
    print("asn.rauf@gmail.com")
    print("Enter CFM List. Enter -1 to stop. Numerical values only.")

    # alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    # "U", "V", "W", "X", "Y", "Z"]

    ceiling = int(input("Enter overall ceiling limit: "))
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
        diff_lim_sel(branch[i].diffuser_cfm, branch[i], ceiling)
        branch[i].solve_branch()
        if branch[i].number == mainline[i].number:
            mainline[i].height = branch[i].height + 2
            # mainline[i].local_limit = max(mainline[i].local_limit, branch[i].height + 2)
            # else:
            # mainline[i].local_limit

    for i in range(1, len(mainline)):

        if mainline[i].height == 0 and mainline[i].width == 0:
            diff_lim_sel(mainline[i].diffuser_cfm, mainline[i], ceiling)
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
    return 0

if __name__ == "__main__":
    main()
