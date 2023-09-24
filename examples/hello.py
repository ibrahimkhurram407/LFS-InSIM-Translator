"""Example 1: Initialize InSim and send the message 'Hello, InSim!' to the chat."""

import pyinsim

with open('example_credentials.txt') as f :
    content = f.read().split('\n')
    IP   = content[0].split("=")[1].strip()
    PORT = int(content[1].split("=")[1].strip())
    PASS = content[2].split("=")[1].strip()

print(IP,PORT,PASS)

# Initialize the InSim system #The IP and Port are to be found in the options when hosting a server
insim = pyinsim.insim(host=IP, port=PORT, Admin=PASS)

# Send message 'Hello, InSim!' to the game
insim.sendm('Hello, InSim!')

# Start pyinsim.
pyinsim.run()
