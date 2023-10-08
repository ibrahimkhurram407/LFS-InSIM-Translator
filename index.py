
# import pyinsim
# import threading
# from googletrans import Translator

# def translate_to_turkish(message):
#     # Translate the message to Turkish
#     translator = Translator()
#     translated = translator.translate(message, src='auto', dest='tr')
#     return "Turkish: " + translated.text

#insim.send(pyinsim.ISP_MST, Msg='Hello, InSim!')
# _____
# import pyinsim

# # Define the InSim server connection details
# IP = '127.0.0.1'
# PORT = 29999
# PASS = ''

# # Initialize the InSim object
# insim = pyinsim.insim(IP, PORT, Admin=PASS)

# # Send an IS_ISI (InSim Init) packet to initiate the connection
# insim.send(pyinsim.ISP_ISI,ReqI=0, UDPPort=0, Flags=0, Prefix=b'\x00', Interval=0, Admin=b'', IName=b'pyinsim')

# # Send a message using the IS_MST packet
# insim.send(pyinsim.ISP_MST, Msg='Hello, InSim!')
# # Start pyinsim.
# pyinsim.run()

# Import the pyinsim module.
import pyinsim

# Initialize InSim on the specified host and port.
insim = pyinsim.insim('127.0.0.1', 29999, Admin='')

# Send message 'Hello, InSim!' to the host.s
insim.sendm('Hello, InSim!')

# Run the pyinsim system.
pyinsim.run()