#!/usr/bin/env python3
# coding: utf-8

#############################################################
## quelques test de construction et simulation de circuits ##
##                sera remplacé par la GUI                 ##
#############################################################

from engine.simulator import log  # le log
from engine.gates import *        # portes logiques de base
from engine.clock import *        # horloge
from os.path import dirname, realpath


HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
AUTO = '\033[0m'


def print_plug_info(plug):
    COLOR = GREEN if plug.value else RED
    ownerName = plug.owner.name if plug.owner else 'None'
    print('%s.%s: %s\n\tsourcePlug: %s\n\tdestinationPlugs: %s'
            % (ownerName, plug.name, COLOR + str(plug.value) + AUTO,
                str(plug.sourcePlug.name if plug.sourcePlug else ''),
                str([conn.name for conn in plug.destinationPlugs])))


# un simple nand
def nand(a, b):
    # composantes du circuit
    NA0 = NandGate('NA1')
    # positionnement des valeurs d'entrée
    NA0.A.set(a)    # bitA
    NA0.B.set(b)    # bitB
    # affichage des valeurs de sortie
    print('%i' % (int(NA0.C.value)))


# retourne la valeur du bit 'bit' dans x
def bit(x, bit):
    return x[bit] == '1'


# additionneur de 2 mots de 4 bits
def adder_2x4(a, b, TC):
    # composantes du circuit
    F0 = TC.add_circuit(FullAdder('F0'))
    F1 =TC. add_circuit(FullAdder('F1'))
    F2 =TC. add_circuit(FullAdder('F2'))
    F3 =TC. add_circuit(FullAdder('F3'))
    # connexions des composantes du circuit
    F0.output('Cout').connect(F1.input('Cin'))
    F1.output('Cout').connect(F2.input('Cin'))
    F2.output('Cout').connect(F3.input('Cin'))
    # positionnement des valeurs d'entrée
    F0.input('A').set(bit(a, 3))    # bit0 wordA
    F0.input('B').set(bit(b, 3))    # bit0 wordB
    F0.input('Cin').set(0)          # retenue_entrante
    F1.input('A').set(bit(a, 2))    # bit1 wordA
    F1.input('B').set(bit(b, 2))    # bit1 wordB
    F2.input('A').set(bit(a, 1))    # bit2 wordA
    F2.input('B').set(bit(b, 1))    # bit2 wordB
    F3.input('A').set(bit(a, 0))    # bit3 wordA
    F3.input('B').set(bit(b, 0))    # bit3 wordB
    # affichage des valeurs de sortie
    print('%i%i%i%i%i' % (int(F3.Cout.value), int(F3.S.value), int(F2.S.value),
                          int(F1.S.value), int(F0.S.value)))


#================================= PROGRAMME =================================#
from time import sleep


if __name__ == '__main__':
    strFile = (
        dirname(realpath(__file__))
        + '/../lang/strings_' + 'en')
    f = open(strFile, 'r')
    for _, line in enumerate(f):
        if line.startswith('Plug') or line.startswith('Circuit'):
            exec(line)

    # circuit principal
    TC = Circuit("Main_Circuit", None)
    # circuit's inputs
    A = Plug(True, 'A', TC)    # inputList[0]
    B = Plug(True, 'B', TC)    # inputList[1]
    # circuit's outputs
    S = Plug(False, 'S', TC)   # outputList[0]
    C = Plug(False, 'C', TC)   # outputList[1]
    # circuit's components
    XOR = XorGate('XOR', TC)
    AND = AndGate('AND', TC)
    # retrieve gates I/O
    XOR_IN0 = XOR.inputList[0]
    XOR_IN1 = XOR.inputList[1]
    XOR_OUT = XOR.outputList[0]
    AND_IN0 = AND.inputList[0]
    AND_IN1 = AND.inputList[1]
    AND_OUT = AND.outputList[0]
    # connections between circuit's components
    A.connect(XOR_IN0)
    A.connect(AND_IN0)
    B.connect(XOR_IN1)
    B.connect(AND_IN1)
    XOR_OUT.connect(S)
    AND_OUT.connect(C)
    #
    A.set(1)
    B.set(1)

    print('\n______________________________________________________________\n')
    for plug in [A, B, XOR_IN0, XOR_IN1, XOR_OUT, AND_IN0, AND_IN1, AND_OUT, S, C]:
        print_plug_info(plug)

    #~ B.set(0)
#~ 
    #~ print('\n______________________________________________________________\n')
    #~ for plug in [A, B, S, C]:
        #~ print_plug_info(plug)
    
    
    #~ clk = TC.add_input('CLOCK')        # l'horloge est une simple sortie du TL
    #~ bgClockThread = ClockThread(clk)   # mais elle est simulée dans un thread
    #~ bgClockThread.start()              # on démarre l'horloge (1 tic par sec)
#~ 
    #~ AND = TC.add_circuit(AndGate)      # puis on créé une porte AND
    #~ I0 = AND.inputList[0]
    #~ I1 = AND.inputList[1]
    #~ O0 = AND.outputList[0]
#~ 
    #~ I0.set(1)                          # on positionne son entrée I0 à 1
    #~ clk.connect(I1)                    # on connecte l'horloge à son entrée I1
    #~ 
    #~ sleep(bgClockThread.spd)           # on attends un tic d'horloge
    #~ print(O0.value)                    # on imprime la sortie de la porte AND
    #~ time.sleep(1)                      # on attends un second tic d'horloge
    #~ print(O0.value)                    # le tic à modifié la sortie du AND
    #~ time.sleep(1)                      # on attends encore un troisième tic
    #~ print(O0.value)                    # la sortie vaut la valeur de l'horloge
                                       #~ # logique car 1 ET 0 = 0 / 1 ET 1 = 1
    #~ bgClockThread.stop()               # enfin on quite le thread de l'horloge

    #~ HA = TC.add_circuit(HalfAdder)
    #~ A = HA.inputList[0]
    #~ B = HA.inputList[1]
    #~ O = HA.outputList[0]
    #~ COUT = HA.outputList[1]
    #~ A.set(1)
    #~ B.set(1)
    #~ print('A:   ' + str(A.value))
    #~ print('B:   ' + str(B.value))
    #~ print('O:    ' + str(O.value))
    #~ print('COUT: ' + str(COUT.value))
    #~ 
    #~ print('________________________________________________________________\n')
    #~ for plug in [A, B, HA.NOR1.inputList[0], HA.NOR1.inputList[1], HA.NOR1.outputList[0], HA.AND1.inputList[0], HA.AND1.inputList[1], HA.AND1.outputList[0], O, COUT]:
        #~ print_plug_info(plug)
        #~ 
    #~ HA.remove(COUT)
    #~ print('________________________________________________________________\n')
    #~ for plug in [A, B, HA.NOR1.inputList[0], HA.NOR1.inputList[1], HA.NOR1.outputList[0], HA.AND1.inputList[0], HA.AND1.inputList[1], HA.AND1.outputList[0], O, COUT]:
        #~ print_plug_info(plug)
    
    #~ FA = TC.add_circuit(FullAdder)
    #~ I0 = FA.inputList[0]
    #~ I1 = FA.inputList[1]
    #~ CIN = FA.inputList[2]
    #~ O = FA.outputList[0]
    #~ COUT = FA.outputList[1]
    
    #~ NOT = NotGate(None, TC)
    #~ print(TC.circuitList)
    #~ GIN = Plug(True, None, TC)
    #~ GOUT = Plug(False, None, TC)
    #~ I = NOT.inputList[0]
    #~ O = NOT.outputList[0]
    #~ GIN.connect(I)
    #~ O.connect(GOUT)
    #~ GIN.set(False)
#~ 
    #~ print('________________________________________________________________\n')
    #~ for plug in [GIN, I, O, GOUT]:
        #~ print_plug_info(plug)
    #~ 
    #~ O.disconnect(GOUT)
    #~ print('\n___________________DISCONNECTED GOUT AND O____________________\n')
    #~ for plug in [GIN, I, O, GOUT]:
        #~ print_plug_info(plug)


