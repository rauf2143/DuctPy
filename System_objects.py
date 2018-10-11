class Duct:
    """Duct class represents all segments including mainlines and branches"""

    def __init__(self, number, running_cfm, inst_cfm, parent=0, diffuser=0):
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

    def __str__(self):
        return str(self.type) + "[" + str(self.number) + "]"


obj = Duct(1, 100, 50)
print(obj)
