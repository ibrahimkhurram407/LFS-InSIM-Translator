"""Example 3: Bind a handler for the MSO packet event."""

import pyinsim

def autstr(ob):
    """AutoString
    Automatically converts bytes to string if it has to
    """
    return ob.decode() if type(ob)==bytes else ob

def message_out(insim, mso):
    # Print out the MSO message.
    print(autstr(mso.Msg))

with open('example_credentials.txt') as f :
    content = f.read().split('\n')
    IP   = content[0].split("=")[1].strip()
    PORT = int(content[1].split("=")[1].strip())
    PASS = content[2].split("=")[1].strip()

# Initialize the InSim object
insim = pyinsim.insim(IP, PORT, Admin=PASS)

# Bind packet called for the MSO packet.
insim.bind(pyinsim.ISP_MSO, message_out)

# Start pyinsim.
pyinsim.run()
