############################################################
##                  basic logic gates                     ##
##  these gates allow you to build more complex circuits  ##
##           circuits.py contains some examples           ##
##   user_circuits contains those defined by the user     ##
############################################################

from comod import _INPUT
from comod import _OUTPUT
from simulator import *


# NOT gate
class NotGate(Circuit):
    def __init__(self, name=None):
        Circuit.__init__(self, name)
        self.A = Input('I', self, False)
        self.add_output('O', False)

    def evalfun(self):
        self.outputList[0].set(not self.A.value)


# AND gate
class AndGate(Circuit):
    def __init__(self, name=None, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        out = True
        for inp in self.inputList:
            if inp.value is False:
                out = False
                break
        self.outputList[0].set(out)


# OR gate
class OrGate(Circuit):
    def __init__(self, name=None, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is True:
                out = True
                break
        self.outputList[0].set(out)


# XOR gate
class XorGate(Circuit):
    def __init__(self, name, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        c = 0
        for inp in self.inputList:
            if inp.value is True:
                c += 1
        self.outputList[0].set(c % 2)


# NAND gate
class NandGate(Circuit):
    def __init__(self, name, inputs=2):
        Circuit.__init__(self, name)
        for inp in range(inputs):
            self.add_input('I' + str(inp), False)
        self.add_output('O', False)

    def evalfun(self):
        out = False
        for inp in self.inputList:
            if inp.value is False:
                out = True
                break
        self.outputList[0].set(out)
