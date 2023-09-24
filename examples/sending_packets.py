"""Example 2: Same as example 1, except we create and send an actualy MST packet."""

import pyinsim

with open('example_credentials.txt') as f :
    content = f.read().split('\n')
    IP   = content[0].split("=")[1].strip()
    PORT = int(content[1].split("=")[1].strip())
    PASS = content[2].split("=")[1].strip()

# Initialize the InSim object
insim = pyinsim.insim(IP, PORT, Admin=PASS)

# Send an MST packet with the message 'Hello, InSim!' to the game.
insim.send(pyinsim.ISP_MST, Msg='Hello, InSim!')

# Start pyinsim.
pyinsim.run()
