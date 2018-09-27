import unittest
from math import sqrt, log10, pi, ceil, floor

h_loss_ideal = 0.08
density = 0.075
viscosity = 0.0432
st_length = 100
roughness = 0.006
# colebrook_correct = 0.00065

def diff_sel(branch_cfm):
    if 0 <= branch_cfm <= 75:
        return 6
    elif 76 <= branch_cfm <= 169:
        return 9
    elif 170 <= branch_cfm <= 300:
        return 12
    elif 301 <= branch_cfm <= 469:
        return 15
    elif 470 <= branch_cfm <= 675:
        return 18
    elif 676 <= branch_cfm <= 909:
        return 21
    elif 910 <= branch_cfm <= 1200:
        return 24
    elif 1201 <= branch_cfm <= 1875:
        return 30
    else:
        print("Diffuser out of range")
        return 0


def diff_lim_sel(diffuser, diffuser_cfm, ceiling):
    if diffuser == 1:
        diffuser = diff_sel(diffuser_cfm)
        if diffuser % 2 == 0:
            width = diffuser + 2
            return width
        else:
            width = diffuser + 3
            return width

    elif diffuser > 1:
        width = diffuser
        return width

    elif diffuser == 0:
        height = ceiling
        return height

    else:
        print("Uh oh. Limit selecting went awry")
        return 0


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


# segment1 = Segment(1, 300, 600, 0, 1)


class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(diff_lim_sel(1, 300, 12), 14)
