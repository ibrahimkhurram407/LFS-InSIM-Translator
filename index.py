
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

import struct
import socket

# Define the InSim server connection details
IP = '127.0.0.1'
PORT = 29999
PASS = ''

# Initialize the InSim object
# Send the IS_ISI packet to initiate the connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))

    # Encode string values to bytes before packing them into the packet.
admin_password = b'0907'
InSIM_Nick = b'^3MyInsim'

    # Pack the ISI packet into a string.
isi = struct.pack('BBBBHHBBH16s16s',
                    44,          # Size
                    1,           # Type
                    1,           # ReqI - causes LFS to send an IS_VER. 
                    0,           # Zero
                    0,           # UDPPort
                    0,           # Flags
                    0,           # Sp0
                    0,           # Prefix
                    0,           # Interval
                    b'',  # Admin 
                    b'') # IName

# Send the ISI packet to InSim.
sock.send(isi)

# Send a message using the IS_MST packet
class IS_MSO(object):
    """MSg Out - system messages and user messages"""
    pack_s = struct.Struct('8B')
    
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.Zero, self.UCID, self.PLID, self.UserType, self.TextStart = self.pack_s.unpack(data[:8])
        self.Msg = data[8:].decode('utf-8', errors='ignore')  # Convert bytes to a string
        return self

# Simulated incoming message data (corrected format)
incoming_data = b'\x13\x10\x00\x00\x00\x01\x00\x00Hello World\x00'

# Create an instance of the IS_MSO class and unpack the incoming data
mso_packet = IS_MSO()
mso_packet.unpack(incoming_data)

# Print the unpacked message
print(f"Size: {mso_packet.Size}")
print(f"Type: {mso_packet.Type}")
print(f"ReqI: {mso_packet.ReqI}")
print(f"UCID: {mso_packet.UCID}")
print(f"PLID: {mso_packet.PLID}")
print(f"UserType: {mso_packet.UserType}")
print(f"Text: {mso_packet.Msg}")