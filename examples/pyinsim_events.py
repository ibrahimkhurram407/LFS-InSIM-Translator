"""Example 4: Bind pyinsim top-level events."""

import pyinsim

def init(insim):
    print('InSim initialized')

def closed(insim):
    print('InSim connection closed')

def error(insim):
    print('InSim error:')
    import traceback
    traceback.print_exc()

def all(insim, packet):
    print(vars(packet))

with open('example_credentials.txt') as f :
    content = f.read().split('\n')
    IP   = content[0].split("=")[1].strip()
    PORT = int(content[1].split("=")[1].strip())
    PASS = content[2].split("=")[1].strip()

# Initialize the InSim object
insim = pyinsim.insim(IP, PORT, Admin=PASS)

insim.bind(pyinsim.EVT_INIT, init)
insim.bind(pyinsim.EVT_CLOSE, closed)
insim.bind(pyinsim.EVT_ERROR, error)
insim.bind(pyinsim.EVT_ALL, all)

pyinsim.run()
