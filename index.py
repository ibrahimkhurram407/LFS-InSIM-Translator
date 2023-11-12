#Dependencies.
import os
import socket
import struct 
import time
from googletrans import Translator
import tkinter as tk
from tkinter import ttk
import datetime
import threading
import queue
from functools import partial
import asyncio
from flask import Flask
import re

#variables
global batchCount
global batchApproval
global road_lanes
global controlAvailability
global top_left
global top_right
global bottom_right
global RoadExitsArray
global firstMsg
global user_name
global CarInfo
global native_lang
native_lang = "en"
# global road_exits
# road_exits = "1,2,3|1,2,3|1,2,3"
CarInfo = {}
user_name= "ibrahim407"
firstMsg = "First Message from Insim!"
RoadExitsArray = []
top_left = "29.75,-1180,50"
top_right = "23,-1180,50"
bottom_right = "22.94,-1175.50,50"
instance_threads = []          # Dictionary to store threads
batchCount = 0          #A variable to store the current batch numbers
batchApproval = False   # local variable Decides whether the batch is ready to go?
waitingList = []        #List of waiting instances to take control
controlAvailability = False    #is any instance is controlling?
LFSwindows = []          #an array to store all the LFS windows
mysql_user = "kali-server"
mysql_pass = "Kali User 407"
mysql_host = "0.tcp.eu.ngrok.io"
mysql_port = 16624
mysql_db = "insim"
insim_host = "127.0.0.1"
insim_port = 29999
admin_pass = None

game_version = "0.6r"

road_speed = 120
road_lanes = 2
top_right = None
top_left = None
bottom_right = None
lfs_name = "Live for Speed"
log_destination = "./logs/"

packet = None #Variable to store received packets

#Some constants.
INSIM_VERSION = 7
BUFFER_SIZE = 2048

# Enum for the second byte of any packet

enum_second_byte = {
    0: ["not used", "ISP_NONE"],
    1: ["instruction: insim initialise", "ISP_ISI"],
    2: ["info: version info", "ISP_VER"],
    3: ["both ways: multi-purpose", "ISP_TINY"],
    4: ["both ways: multi-purpose", "ISP_SMALL"],
    5: ["info: state info", "ISP_STA"],
    6: ["instruction: single character", "ISP_SCH"],
    7: ["instruction: state flags pack", "ISP_SFP"],
    8: ["instruction: set car camera", "ISP_SCC"],
    9: ["both ways: cam pos pack", "ISP_CPP"],
    10: ["info: start multiplayer", "ISP_ISM"],
    11: ["info: message out", "ISP_MSO"],
    12: ["info: hidden /i message", "ISP_III"],
    13: ["instruction: type message or /command", "ISP_MST"],
    14: ["instruction: message to a connection", "ISP_MTC"],
    15: ["instruction: set screen mode", "ISP_MOD"],
    16: ["info: vote notification", "ISP_VTN"],
    17: ["info: race start", "ISP_RST"],
    18: ["info: new connection", "ISP_NCN"],
    19: ["info: connection left", "ISP_CNL"],
    20: ["info: connection renamed", "ISP_CPR"],
    21: ["info: new player (joined race)", "ISP_NPL"],
    22: ["info: player pit (keeps slot in race)", "ISP_PLP"],
    23: ["info: player leave (spectate - loses slot)", "ISP_PLL"],
    24: ["info: lap time", "ISP_LAP"],
    25: ["info: split x time", "ISP_SPX"],
    26: ["info: pit stop start", "ISP_PIT"],
    27: ["info: pit stop finish", "ISP_PSF"],
    28: ["info: pit lane enter / leave", "ISP_PLA"],
    29: ["info: camera changed", "ISP_CCH"],
    30: ["info: penalty given or cleared", "ISP_PEN"],
    31: ["info: take over car", "ISP_TOC"],
    32: ["info: flag (yellow or blue)", "ISP_FLG"],
    33: ["info: player flags (help flags)", "ISP_PFL"],
    34: ["info: finished race", "ISP_FIN"],
    35: ["info: result confirmed", "ISP_RES"],
    36: ["both ways: reorder (info or instruction)", "ISP_REO"],
    37: ["info: node and lap packet", "ISP_NLP"],
    38: ["info: multi-car info", "ISP_MCI"],
    39: ["instruction: type message", "ISP_MSX"],
    40: ["instruction: message to local computer", "ISP_MSL"],
    41: ["info: car reset", "ISP_CRS"],
    42: ["both ways: delete buttons / receive button requests", "ISP_BFN"],
    43: ["info: autocross layout information", "ISP_AXI"],
    44: ["info: hit an autocross object", "ISP_AXO"],
    45: ["instruction: show a button on local or remote screen", "ISP_BTN"],
    46: ["info: sent when a user clicks a button", "ISP_BTC"],
    47: ["info: sent after typing into a button", "ISP_BTT"],
    48: ["both ways: replay information packet", "ISP_RIP"],
    49: ["both ways: screenshot", "ISP_SSH"],
    50: ["info: contact between cars (collision report)", "ISP_CON"],
    51: ["info: contact car + object (collision report)", "ISP_OBH"],
    52: ["info: report incidents that would violate HLVC", "ISP_HLV"],
    53: ["instruction: player cars", "ISP_PLC"],
    54: ["both ways: autocross multiple objects", "ISP_AXM"],
    55: ["info: admin command report", "ISP_ACR"],
    56: ["instruction: car handicaps", "ISP_HCP"],
    57: ["info: new connection - extra info for host", "ISP_NCI"],
    58: ["instruction: reply to a join request (allow / disallow)", "ISP_JRR"],
    59: ["info: report InSim checkpoint / InSim circle", "ISP_UCO"],
    60: ["instruction: object control (currently used for lights)", "ISP_OCO"],
    61: ["instruction: multi-purpose - target to connection", "ISP_TTC"],
    62: ["info: connection selected a car", "ISP_SLC"],
    63: ["info: car state changed", "ISP_CSC"],
    64: ["info: connection's interface mode", "ISP_CIM"],
    65: ["both ways: set mods allowed", "ISP_MAL"]
}

# Enum for the fourth byte of an IS_TINY packet
enum_fourth_byte_tiny = {
    0: ["keep alive: see 'maintaining the connection'", "TINY_NONE"],
    1: ["info request: get version", "TINY_VER"],
    2: ["instruction: close insim", "TINY_CLOSE"],
    3: ["ping request: external program requesting a reply", "TINY_PING"],
    4: ["ping reply: reply to a ping request", "TINY_REPLY"],
    5: ["both ways: game vote cancel (info or request)", "TINY_VTC"],
    6: ["info request: send camera pos", "TINY_SCP"],
    7: ["info request: send state info", "TINY_SST"],
    8: ["info request: get time in hundredths (i.e. SMALL_RTP)", "TINY_GTH"],
    9: ["info: multi player end", "TINY_MPE"],
    10: ["info request: get multiplayer info (i.e. ISP_ISM)", "TINY_ISM"],
    11: ["info: race end (return to race setup screen)", "TINY_REN"],
    12: ["info: all players cleared from race", "TINY_CLR"],
    13: ["info request: get NCN for all connections", "TINY_NCN"],
    14: ["info request: get all players", "TINY_NPL"],
    15: ["info request: get all results", "TINY_RES"],
    16: ["info request: send an IS_NLP", "TINY_NLP"],
    17: ["info request: send an IS_MCI", "TINY_MCI"],
    18: ["info request: send an IS_REO", "TINY_REO"],
    19: ["info request: send an IS_RST", "TINY_RST"],
    20: ["info request: send an IS_AXI - AutoX Info", "TINY_AXI"],
    21: ["info: autocross cleared", "TINY_AXC"],
    22: ["info request: send an IS_RIP - Replay Information Packet", "TINY_RIP"],
    23: ["info request: get NCI for all guests (on host only)", "TINY_NCI"],
    24: ["info request: send a SMALL_ALC (allowed cars)", "TINY_ALC"],
    25: ["info request: send IS_AXM packets for the entire layout", "TINY_AXM"],
    26: ["info request: send IS_SLC packets for all connections", "TINY_SLC"],
    27: ["info request: send IS_MAL listing the currently allowed mods", "TINY_MAL"]
}

# Enum for the fourth byte of an IS_SMALL packet
enum_fourth_byte_small = {
    0: ["not used", "SMALL_NONE"],
    1: ["instruction: start sending positions", "SMALL_SSP"],
    2: ["instruction: start sending gauges", "SMALL_SSG"],
    3: ["report: vote action", "SMALL_VTA"],
    4: ["instruction: time stop", "SMALL_TMS"],
    5: ["instruction: time step", "SMALL_STP"],
    6: ["info: race time packet (reply to GTH)", "SMALL_RTP"],
    7: ["instruction: set node lap interval", "SMALL_NLI"],
    8: ["both ways: set or get allowed cars (TINY_ALC)", "SMALL_ALC"],
    9: ["instruction: set local car switches (lights, horn, siren)", "SMALL_LCS"]
}

# Enum for the fourth byte of an IS_TTC packet
enum_fourth_byte_ttc = {
    0: ["not used", "TTC_NONE"],
    1: ["info request: send IS_AXM for a layout editor selection", "TTC_SEL"],
    2: ["info request: send IS_AXM every time the selection changes", "TTC_SEL_START"],
    3: ["instruction: switch off IS_AXM requested by TTC_SEL_START", "TTC_SEL_STOP"]
}

#Setup Flags
setupFlags = {
    1: "SETF_SYMM_WHEELS",
    2: "SETF_TC_ENABLE",
    4: "SETF_ABS_ENABLE"
}

# Group Player Flags
playerFlags = {
    1: "PIF_SWAPSIDE",
    2: "PIF_RESERVED_2",
    4: "PIF_RESERVED_4",
    8:  "PIF_AUTOGEARS",
    16: "PIF_SHIFTER",
    32: "PIF_RESERVED_32",
    64: "PIF_HELP_B",
    128: "PIF_AXIS_CLUTCH",
    256: "PIF_INPITS",
    512: "PIF_AUTOCLUTCH",
    1024: "PIF_MOUSE",
    2048: "PIF_KB_NO_HELP",
    4096: "PIF_KB_STABILISED",
    8192: "PIF_CUSTOM_VIEW"
}

#Enum for the twelfth byte of an IS_NPL packet
TyreTypes = {
    0: "TYRE_R1",
    1: "TYRE_R2",
    2: "TYRE_R3",
    3: "TYRE_R4",
    4: "TYRE_ROAD_SUPER",
    5: "TYRE_ROAD_NORMAL",
    6: "TYRE_HYBRID",
    7: "TYRE_HYBRID"
}

isp_packet_types = enum_second_byte
ttc_packet_types = enum_fourth_byte_ttc
tiny_packet_types = enum_fourth_byte_tiny
small_packet_types = enum_fourth_byte_small

db_config = {
    "host": mysql_host,
    "port": mysql_port,
    "user": mysql_user,
    "password": mysql_pass,
    "database": mysql_db,
}

#Get Configurations
# Create the main window of config
root = tk.Tk()
root.title("Configuration")

style = ttk.Style()
style.theme_use("clam")

# Configure the style for various elements
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TEntry", font=("Helvetica", 12))
style.configure("TLabel", background="black", foreground="white")
style.configure("TFrame", background="black")
style.configure("TEntry", fieldbackground="gray", borderwidth=5)
style.configure("TCombobox", fieldbackground="gray", borderwidth=5)

# Server Insim Info Frame
insim_frame = ttk.LabelFrame(root, text="Server Insim Info")
insim_frame.grid(row=1, column=0, padx=10, pady=5, sticky='w')

# Labels and Entry fields for Server Insim Info
insim_host_label = ttk.Label(insim_frame, text="Insim Host:")
insim_host_label.grid(row=0, column=0, sticky='w')
insim_host_entry = ttk.Entry(insim_frame)
insim_host_entry.grid(row=0, column=1)

insim_port_label = ttk.Label(insim_frame, text="Insim Port:")
insim_port_label.grid(row=1, column=0, sticky='w')
insim_port_entry = ttk.Entry(insim_frame)
insim_port_entry.grid(row=1, column=1)

admin_pass_label = ttk.Label(insim_frame, text="Admin Pass:")
admin_pass_label.grid(row=2, column=0, sticky='w')
admin_pass_entry = ttk.Entry(insim_frame, show="*")  # Mask password input
admin_pass_entry.grid(row=2, column=1)

game_frame = ttk.LabelFrame(root, text="Config")
game_frame.grid(row=4, column=0, padx=10, pady=5, sticky='w')

log_destination_label = ttk.Label(game_frame, text="Log Destination:")
log_destination_label.grid(row=5, column=0, sticky='w')
log_destination_entry = ttk.Entry(game_frame)
log_destination_entry.grid(row=5, column=1)

native_lang_label = ttk.Label(game_frame, text="Your Native Lang (en,tr):")
native_lang_label.grid(row=6, column=0, sticky='w')
native_lang_entry = ttk.Entry(game_frame)
native_lang_entry.grid(row=6, column=1)

# Create a log file to start logging
log_file = open("log.txt", "w")
log_file.write("+---This is an Log File for LFS Traffic Mod--+" + "\n")
log_file.flush()

# Create a thread-safe queue for log messages
log_queue = queue.Queue()

# Log viewer Class
class LogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Log Window")

        self.log_text = tk.Text(self.root, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Start a separate thread to process log messages
        self.start_log_thread()

    def start_log_thread(self):
        # This function runs in the main thread
        def process_log_queue():
            while True:
                try:
                    log_message = log_queue.get(block=True, timeout=1)  # Wait for log message
                except queue.Empty:
                    continue
                self.update_log(log_message)

        log_thread = threading.Thread(target=process_log_queue)
        log_thread.daemon = True
        log_thread.start()

    def set_log_function(self, log_function):
        self.log_function = log_function  # Store the log function

    def log(self, message):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{current_time}] {message}"
        log_queue.put(log_message)  # Put the log message into the queue

    def update_log(self, message):
        try:
            # Append the log message to the log text widget in the GUI
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)  # Scroll to the end of the text widget

            if hasattr(self, 'log_function') and callable(self.log_function):
                self.log_function(message)  # Call the provided log function

        except Exception as e:
            print(f"An error occurred while updating the log window: {str(e)}")

    def run(self):
        self.root.mainloop()

# Create the log window
log_window = LogWindow()

# Function to replace the filename in a given path
def replace_filename(destination, new_filename):
    # Split the destination into directory and filename
    directory, old_filename = os.path.split(destination)
    
    # Combine the directory path and the new filename
    new_destination = os.path.join(directory, new_filename)
    
    return new_destination

# Function to copy the log content to a destination file with a timestamp
def storeLogs(log_destination):
    # Ensure the destination folder exists or create it
    if not os.path.exists(log_destination):
        os.makedirs(log_destination)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")  # Use underscores instead of colons

    # Create the new log file name with the timestamp
    new_log_file_name = f"{current_time}_log.txt"

    # Combine the destination folder and the new log file name
    destination_file_path = os.path.join(log_destination, new_log_file_name)

    try:
        with open("log.txt", "r") as source_file:
            # Read the content of the source file
            file_content = source_file.read()

        # Open the destination file for writing
        with open(destination_file_path, "w") as destination_file:
            # Write the content to the destination file
            destination_file.write(file_content)

        log_window.log(f"File log.txt copied to '{destination_file_path}' successfully.")

    except FileNotFoundError:
        log_window.log("Source file not found of logs.")
    except Exception as e:
        log_window.log(f"An error occurred: {str(e)}")

def log(message):
    # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # log_message = f"[{current_time}] {message}"
    log_file.write(message + "\n")
    log_file.flush()  # Flush the buffer to write immediately
    print(message)  # Print to console as well

def get_values():
    global mysql_user, mysql_pass, mysql_host, mysql_port, mysql_db
    global insim_host, insim_port, admin_pass
    global game_version
    global road_speed, road_lanes, top_right, top_left, bottom_right, lfs_name, log_destination
    global user_name
    global road_exits
    global native_lang
    
    insim_host_input = insim_host_entry.get()
    if insim_host_input:
        insim_host = insim_host_input

    insim_port_input = insim_port_entry.get()
    if insim_port_input:
        insim_port = insim_port_input

    admin_pass_input = admin_pass_entry.get()
    if admin_pass_input:
        admin_pass = admin_pass_input

    log_destination_input = log_destination_entry.get()
    if log_destination_input:
        log_destination = log_destination_input
    
    native_lang_input = native_lang_entry.get()
    if native_lang_input:
        native_lang = native_lang_input

    # Close the configuration window
    root.destroy()

    # Continuing the rest of the script in another thread
    newThreadInit(mainExecutor, "Main")

    # Launch the log window after the configuration window is destroyed
    launchLogWindowAfterConfig()

# Button to get the entered values
get_values_button = ttk.Button(root, text="Submit Values", command=get_values)
get_values_button.grid(row=6, column=0, padx=10, pady=10)

def mainExecutor(): 
    asyncio.run(main())

def launchLogWindowAfterConfig():
    log_window.set_log_function(log)
    log_window.run()

    # Schedule the log window to close after 3 seconds
    log_window.root.after(3000, log_window.root.destroy)

# Function to simulate a time-consuming task
def newThreadInit(task, instance):
    thread = threading.Thread(target=task)  # Create a new thread with the given task
    thread.start()  # Start the thread
    instance_threads.append((instance, thread))  # Store the (instance, thread) pair in the list

#Function to run the GUI
def launchConfigGUI():
    root.mainloop()

def retriveAllData():
    log_window.log("Waiting List")
    log_window.log("LFS Instances")


def string_to_integers(input_string):
    # Split the string by commas and convert each part to an integer
    integers_array = [int(part) for part in input_string.split(',')]
    return integers_array

# Example usage
input_string = "334,454,545"
integers_array = string_to_integers(input_string)
print(integers_array)

def sendToSocket(packet, sock):
    sock.send(packet)

def dicExtractor(string, dictionary):
    for packet_type, names in dictionary.items():
        if string in names:
            return packet_type

def KeepAlive(packet,sock) :
    size, type, reqi, subt = struct.unpack('BBBB', packet)
    if subt == dicExtractor("ISP_NONE", isp_packet_types):
        sendToSocket(packet, sock)# Respond to keep-alive.
    

def _eat_null_chars(str_):
    return str_.rstrip(b'\x00')

class IS_MSO(object):
    """MSg Out - system messages and user messages"""
    pack_s = struct.Struct('8B')
    
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.Zero, self.UCID, self.PLID, self.UserType, self.TextStart = self.pack_s.unpack(data[:8])
        self.Msg = data[8:].decode('utf-8', errors='ignore')  # Convert bytes to a string
        return self

#packet = b'\x13\x10\x00\x00\x00\x01\x00\x00Hello World\x00'
#unpackPacket("ISP_MSO",packet,ID)

class IS_NPL(object):
    """New PLayer joining race (if PLID already exists, then leaving pits)"""
    pack_s = struct.Struct('6BH23sx8s3sx15sx8Bi4B')
    def unpack(self, data):
        self.Tyres = [0,0,0,0]
        self.Size, self.Type, self.ReqI, self.PLID, self.UCID, self.PType, self.Flags, self.PName, self.Plate, self.CName, self.SName, self.Tyres[0], self.Tyres[1], self.Tyres[2], self.Tyres[3], self.H_Mass, self.H_TRes, self.Model, self.Pass, self.Spare, self.SetF, self.NumP, self.Sp2, self.Sp3 = self.pack_s.unpack(data)
        self.PName = _eat_null_chars(self.PName)
        #self.Plate = _eat_null_chars(self.Plate) # No trailing zero
        self.CName = _eat_null_chars(self.CName)
        self.SName = _eat_null_chars(self.SName)
        return self
    
class IS_MCI(object):
    """Multi Car Info - if more than 8 in race then more than one of these is sent"""
    pack_s = struct.Struct('4B')
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.NumC = self.pack_s.unpack(data[:4])
        data = data[4:]
        self.Info = [CompCar(data, i) for i in range(0, self.NumC * 28, 28)]
        return self

class CompCar(object):
    """Car info in 28 bytes - there is an array of these in the :class:`IS_MCI`

    """
    pack_s = struct.Struct('2H4B3i3Hh')
    def __init__(self, data, index):
        """Initialise a new CompCar sub-packet."""
        self.Node, self.Lap, self.PLID, self.Position, self.Info, self.Sp3, self.X, self.Y, self.Z, self.Speed, self.Direction, self.Heading, self.AngVel = self.pack_s.unpack(data[index:index+28])

class IS_NCN(object):
    """New ConN

    """
    pack_s = struct.Struct('4B23sx23sx4B')
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.UCID, self.UName, self.PName, self.Admin, self.Total, self.Flags, self.Sp3 = self.pack_s.unpack(data)
        self.UName = _eat_null_chars(self.UName)
        self.PName = _eat_null_chars(self.PName)
        return self

class CarContact(object):
    """Info about one car in a contact - two of these in the IS_CON"""
    pack_s = struct.Struct('3Bb6b2B2h')
    def __init__(self, data):
        self.PLID, self.Info, self.Sp2, self.Steer, self.ThrBrk, self.CluHan, self.GearSp, self.Speed, self.Direction, self.Heading, self.AccelF, self.AccelR, self.X, self.Y = self.pack_s.unpack(data)

class IS_CON(object):
    """CONtact - between two cars (A and B are sorted by PLID)"""
    pack_s = struct.Struct('4B2H')
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.Zero, self.SpClose, self.Time = self.pack_s.unpack(data[:8])
        self.A = CarContact(data[8:24])
        self.B = CarContact(data[24:])
        return self

class CarContOBJ(object):
    def __init__(self):
        self.Direction = 0
        self.Heading = 0
        self.Speed = 0
        self.Zbyte = 0
        self.X = 0
        self.Y = 0

OBH_LAYOUT = 1
OBH_CAN_MOVE = 2
OBH_WAS_MOVING = 4
OBH_ON_SPOT = 8

class IS_OBH(object):
    pack_s = struct.Struct('4B2H4B2h2h4B')
    def unpack(self, data):
        self.C = CarContOBJ()
        self.Size, self.Type, self.ReqI, self.PLID, self.SpClose, self.Time, self.C.Direction, self.C.Heading, self.C.Speed, self.C.Zbyte, self.C.X, self.C.Y, self.X, self.Y, self.Zbyte, self.Sp1, self.Index, self.OBHFlags = self.pack_s.unpack(data)
        return self

# Add More info packet classes

classesDic = {
    "ISP_MSO": IS_MSO(),
    "ISP_NPL": IS_NPL(), 
    "ISP_MCI": IS_MCI(),
    "ISP_NCN": IS_NCN(),
    "ISP_OBH": IS_OBH(),
    "ISP_CON": IS_CON(),
    #"ISP_TINY": IS_TINY()
}

def unpackPacket(packetType, packetReceived,ID):
    packet = classesDic[packetType]
    if packet != None:
        packet = packet.unpack(packetReceived)
        if packetType == "ISP_MSO":
            log_window.log(f"{ID}| Size: {packet.Size}\nType: {packet.Type}\nReqI: {packet.ReqI}\nUCID: {packet.UCID}\nPLID: {packet.PLID}\nUserType: {packet.UserType}\nText: {packet.Msg}")
            return {
                "kind": packetType,
                "size": packet.Size,
                "type": packet.Type,
                "reqi": packet.ReqI,
                "ucid": packet.UCID,
                "plid": packet.PLID,
                "user-type": packet.UserType, 
                "msg": packet.Msg
            }
        elif packetType == "ISP_NPL":
            log_message = f"{ID}| Size: {packet.Size}\nType: {packet.Type}\nReqI: {packet.ReqI}\nPlayer Name: {packet.PName}\nCar Name: {packet.CName}\nUCID: {packet.UCID}\nplayer Type: {packet.PType}\nFlags: {packet.Flags}\nTyre Type \nrear L:{TyreTypes[packet.Tyres[0]]}\nRear R:{TyreTypes[packet.Tyres[1]]}\nFront L: {TyreTypes[packet.Tyres[2]]}\nFront R:{TyreTypes[packet.Tyres[3]]}\nSkin Name: {packet.SName}\nAdded Mas: {packet.H_Mass}\nIntake Restriction: {packet.H_TRes}\nDriver Model: {packet.Model}\nPassengers {packet.Pass}\nSetupFlags: {packet.SetF}"
            log_window.log(log_message)
            return {
                "kind": packetType,
                "size": packet.Size,
                "type": packet.Type,
                "size": packet.Size,
                "type": packet.Type, 
                "reqi":packet.ReqI,
                "plid": packet.PLID,
                "ucid": packet.UCID,
                "playerType": packet.PType,
                "flags": packet.Flags,
                "playerName": packet.PName,
                "plate": packet.Plate,
                "carName": packet.CName,
                "skinName": packet.SName,
                "tyreTypes": packet.Tyres,
                "addedMass": packet.H_Mass,
                "intakeRestriction": packet.H_TRes,
                "playerModel": packet.Model,
                "passengerByte": packet.Pass,
                "setupFlags": packet.SetF,
                "numberInRace": packet.NumP,
            }
        elif packetType == "ISP_MCI":
            log_window.log(f"{ID}| Size: {packet.Size}\nType: {packet.Type}\nReqI: {packet.ReqI}\nNumC: {packet.NumC}\nInfo: {packet.Info}")
            # Extract relevant information from the IS_MCI packet and return it
            return {
                "kind": packetType,
                "size": packet.Size,
                "type": packet.Type,
                "reqi": packet.ReqI,
                "numc": packet.NumC,
                "info": [info.__dict__ for info in packet.Info]
            }
        elif packetType == "ISP_NCN":
            log_window.log(f"{ID}| Size: {packet.Size}\nType: {packet.Type}\nReqI: {packet.ReqI}\nUCID: {packet.UCID}\nUsername: {packet.UName}\nPlayer Name: {packet.PName}\nAdmin: {packet.Admin}\nTotal: {packet.Total}\nFlags {packet.Flags}")
            return {
                "kind": packetType,
                "size": packet.Size,
                "type": packet.Type,
                "reqi": packet.ReqI,
                "ucid": packet.UCID,
                "username": packet.UName,
                "playerName": packet.PName, 
                "admin": packet.Admin, 
                "Total": packet.Total,
                "flags": packet.Flags
            }
    else:
        log_window.log(f"{ID}| unknow type of packet received to unpack")

class IS_SMALL(object):
    pack_s = struct.Struct('4BI')
    
    def __init__(self, ReqI=0, SubT=0, UVal=0):
        self.Size = int(8)
        self.Type = dicExtractor ("ISP_SMALL", isp_packet_types)
        self.ReqI = ReqI
        self.SubT = SubT
        self.UVal = UVal
    
    def pack(self):
        return self.pack_s.pack(self.Size, self.Type, self.ReqI, self.SubT, self.UVal)
    
    def unpack(self, data):
        self.Size, self.Type, self.ReqI, self.SubT, self.UVal = self.pack_s.unpack(data)
        return self

# Function to send the IS_SMALL packet
def sendIS_SMALL_SSP(sock, interval):
    small_ssp_packet = IS_SMALL(SubT=dicExtractor("SMALL_SSP", small_packet_types), UVal=interval)
    packed_data = small_ssp_packet.pack()  # Pack the IS_SMALL packet
    sendToSocket(packed_data, sock)  # Send the packed data over the socket

async def sendISP_ISI(password, nick, ID, sock, flag, udpPort):
    # Pack the ISI packet into a string.
    if not isinstance(flag, int):
        log_window.log(ID + "| flag bit set to 0 because flag not an integer")
        flag = 0
    
    # Ensure 'nick' is null-terminated
    nick = nick[:15].ljust(16, b'\0')  # Pad 'nick' to a length of 16 characters with null characters ('\0')
    
    isi = struct.pack('BBBBHHBBH16s16s',
        44,                         # Size
        dicExtractor("ISP_ISI", isp_packet_types),  # Type
        1,                          # ReqI - causes LFS to send an IS_VER.
        0,                          # Zero
        udpPort,                    # UDPPort
        int(flag),                  # Flags (ISF_MCI: bit 5)
        0,                          # Sp0
        0,                          # Prefix
        0,                          # Interval
        password,                   # Admin (already bytes, no need to encode)
        nick                        # IName (already bytes, no need to encode)
    )

    # Send the ISI packet to InSim.
    log_window.log(str(ID) + "| Sending ISI packet...")
    sendToSocket(isi, sock)

    # Sleep for 1 second
    await asyncio.sleep(0.5)

def sendISP_MSL(message, ID, sock):
    msl_packet = struct.pack('BBBB128s',
                            132,           # Size
                            dicExtractor("ISP_MSL", isp_packet_types),       # Type
                            1,             # ReqI
                            0,             # Sound
                            message.encode('utf-8'))
    
    log_window.log(str(ID) + "| Sending MSL packet with message: " + message)
    sendToSocket(msl_packet, sock)

class IS_TINY(object):
    """General purpose packet.

    """
    pack_s = struct.Struct('4B')
    def __init__(self, ReqI=0, SubT=dicExtractor("TINY_NONE", tiny_packet_types)):
        """Initialise a new IS_TINY packet.

        Args:
            ReqI : zero (0) unless in response to a request.
            SubT : subtype from ``TINY_*`` enumeration (e.g. ``TINY_REN``)

        """
        self.Size = int(4)
        self.Type = dicExtractor("ISP_TINY", isp_packet_types)
        self.ReqI = ReqI
        self.SubT = SubT

    def pack(self):
        return self.pack_s.pack(self.Size, self.Type, self.ReqI, self.SubT)

    def unpack(self, data):
        fields = self.pack_s.unpack(data)
        self.Size, self.Type, self.ReqI, self.SubT = fields
        return self

def sendIS_TINY(subT, ReqI, sock, ID):
    mst_packet = IS_TINY(ReqI=ReqI, SubT=dicExtractor(subT, tiny_packet_types))
    log_window.log(str(ID) + "| sending IS_TINY to request: " + subT)
    sendToSocket(mst_packet.pack(), sock)
    
class IS_MST(object):
    """Msg Type - send to LFS to type message or command"""
    def __init__(self, Msg=b''):
        """Initialize a new IS_MST packet.

        Args:
            Msg: message (63 characters or less)

        """
        self.Size = 68  # Calculate the actual size, which is 68 bytes
        self.Type = dicExtractor("ISP_MST", isp_packet_types)
        self.ReqI = 0
        self.Zero = 0
        self.Msg = Msg

    def pack(self):
        # Ensure the message is at most 63 characters and pad with null bytes
        truncated_msg = self.Msg[:63].ljust(63, b'\x00')
        return struct.pack('4B63sB', self.Size, self.Type, self.ReqI, self.Zero, truncated_msg, 0)

def sendISP_MST(message_or_command, ID, sock):
    # Ensure the message is not longer than 63 characters
    truncated_message = message_or_command[:63]
    # Create an instance of the IS_MST class with the message or command
    mst_packet = IS_MST(Msg=truncated_message.encode('utf-8'))
    log_window.log(str(ID) + "| sending message/command: " + message_or_command)
    sendToSocket(mst_packet.pack(), sock)

def sendISP_SCH(charB, sock, shift=False, ctrl=False, ID=None):
    flags = 0
    if shift:
        flags |= 1
    if ctrl:
        flags |= 2

    charB_byte = ord(charB)  # Convert charB to a byte
    
    sch_packet = struct.pack('BBBBBBB',
                             8,           # Size
                             dicExtractor("ISP_SCH", isp_packet_types),  # Type
                             0,           # ReqI
                             0,           # Zero
                             charB_byte,  # CharB as a byte
                             flags,       # Flags
                             0)           # Spare2 (you can set this to 0 as well)
    if ID != None:
        log_window.log(str(ID) + "| Sending SCH packet with CharB: {}, SHIFT: {}, CTRL: {}".format(charB, shift, ctrl))
    else:
        log_window.log("Sending SCH packet with CharB: {}, SHIFT: {}, CTRL: {}".format(charB, shift, ctrl))
    sendToSocket(sch_packet, sock)

def translator(msg, lang='en'):
    """
    Translates a message to the specified language.

    Args:
    - msg (str): The message to be translated.
    - lang (str): The language code to translate the message into. Default is 'en' (English).

    Returns:
    - str: The translated message.
    """

    translator = Translator()

    try:
        translation = translator.translate(msg, dest=lang)
        translated_msg = translation.text
    except Exception as e:
        print(f"Translation failed: {e}")
        translated_msg = msg  # If translation fails, return the original message

    return translated_msg

def remove_color_codes(input_string):
    """
    Removes color codes (^a, ^L, etc.) from a string.

    Args:
    - input_string (str): The string containing color codes.

    Returns:
    - str: The string with color codes removed.
    """
    # Define a regular expression pattern to match color codes (^a, ^L, etc.)
    color_code_pattern = re.compile(r'\^\w', re.IGNORECASE)

    # Use sub() function to replace color codes with an empty string
    result_string = re.sub(color_code_pattern, '', input_string)

    return result_string

def handle_MSO(packet,ID, sock):
    global native_lang
    if packet['ucid'] != 0:
        msg = remove_color_codes(packet['msg'])
        translated_message = translator(msg, native_lang)
        log_window.log(ID + "| Translated: " + translated_message)
        if translated_message != packet['msg']:
            sendable_message = "^1Translated: ^6" + translated_message
            sendISP_MSL(sendable_message, id, sock)

def closeConnection(ID,sock):
    packet_size = 4  # Size of the packet (excluding the size field itself)
    packet_type = dicExtractor("TINY_CLOSE", tiny_packet_types) # Type for IS_TINY_CLOSE
    reqi = 0  # ReqI (can be set to 0)
    subtype = 0  # Subtype for TINY_CLOSE

    # Pack the IS_TINY_CLOSE packet into a string
    packet = struct.pack('BBBB', packet_size, packet_type, reqi, subtype)
    log_window.log(ID + "| Closing Connection from Insim")
    sendToSocket(packet, sock)
    log_window.log(str(ID) + "| closing socket...")
    sock.close()

def CheckQuit (ID,sock):
    global quit
    if quit == True:
        Quit(ID,sock)

def Quit(ID,sock):
    global quit
    quit = True
    closeConnection(ID,sock)
    if ID == "Main":
        retriveAllData()
        storeLogs(log_destination)
        root.quit()
    exit()

async def positionReached(ID):
    while True:
        log_window.log(ID + "| waiting for car to reach position")
        await asyncio.sleep(2)

def checkPacket(sock,ID, buffer):
    global firstMsg
    data =  sock.recv(BUFFER_SIZE)
    Return = []
    if data:
        log_window.log(str(ID) + "| Received something, Analyzing...")
        buffer += data

        # Loop through completed packets.
        while len(buffer) >= 1:
            i = 0
            while int(buffer[i]) == 0:
                i = i +1
                time.sleep(0.1)
                log_window.log("First byte of the packet is 0")
            packet_size = buffer[i]
            if len(buffer) >= packet_size:
                # Copy the packet from the buffer.
                packet = buffer[:packet_size]
                buffer = buffer[packet_size:]
                # Check packet type.
                packet_type = packet[1]
                if isp_packet_types[packet_type]:
                    log_window.log(f"{str(ID)}| It's {isp_packet_types[packet_type]} Packet ({packet_type}).")
                    if packet_type == dicExtractor("ISP_TINY", isp_packet_types):
                        size, type, reqi, subt = struct.unpack('BBBB', packet)

                        # Check the subtype (SubT) of the TINY packet
                        if tiny_packet_types[subt][1] == "TINY_NONE":
                            # Keep alive signal
                            log_window.log(str(ID) + "| Received keep-alive signal, responding..")
                            KeepAlive(packet,sock)
                            Return.append("KeepAlive")
                        elif tiny_packet_types[subt][1] =="TINY_VER":
                            # Info request: get version, respond with version info
                            # Build and send the response packet
                            response_packet = struct.pack('BBBB8s6sH', 20, dicExtractor("ISP_VER", isp_packet_types), reqi, 0, b'0.6R\x00\x00\x00\x00', b'S2\x00\x00\x00\x00\x00', INSIM_VERSION, 0)
                            sendToSocket(response_packet, sock)
                            Return.append("VarReq")
                        elif tiny_packet_types[subt][1] == "TINY_CLOSE":
                            # Instruction: close insim, you can handle the closing logic here
                            log_window.log(str(ID) + "| Received close insim instruction")
                            closeConnection(ID,sock)
                            Quit(ID,sock)
                            Return.append("CloseInSim")
                        elif tiny_packet_types[subt][1] == "TINY_PING":
                            # Ping request: external program requesting a reply
                            # Respond with a TINY_REPLY packet
                            response_packet = struct.pack('BBBB', 4, dicExtractor("ISP_TINY", isp_packet_types), reqi, enum_fourth_byte_tiny["TINY_REPLY"][0])
                            sendToSocket(response_packet)
                            Return.append("ping")
                        else:
                            # Handle other subtypes as needed
                            log_window.log(ID + f"|I am not asked to do anything of this {subt} subtye of TINY packet.")
                    elif packet_type == dicExtractor("ISP_VER", isp_packet_types):
                        # Unpack the VER packet and check the InSim version.
                        size, type, reqi, _, version, product, insimver = struct.unpack('BBBB8s6sH', packet)

                        # Extract LFS version and product type from the received data
                        lfs_version = version.decode('utf-8').strip('\x00')  # Decode bytes to string and remove null characters
                        lfs_product = product.decode('utf-8').strip('\x00')  # Decode bytes to string and remove null characters

                        # Log the information
                        log_window.log(f"{ID}| Received LFS Version: {lfs_version}")
                        log_window.log(f"{ID}| Received LFS Product: {lfs_product}")
                        log_window.log(f"{ID}| Received InSim Version: {insimver}")

                        if insimver != INSIM_VERSION:
                            log_window.log(f"Breaking connection because invalid InSim version. Insim Version: {insimver}")
                            Quit(ID,sock)
                            closeConnection(ID,sock)
                            Return.append("invalidVer")
                        else:
                            Return.append("Ver")
                    elif packet_type == dicExtractor("ISP_MSO", isp_packet_types):
                        unPackedPacket = unpackPacket("ISP_MSO", packet, ID)
                        received_msg = unPackedPacket["msg"].rstrip('\x00')  # Remove trailing null characters
                        if received_msg == firstMsg:
                            unPackedPacket["firstMSOReceived"] = True
                        handle_MSO(unPackedPacket, ID, sock)
                        Return.append(unPackedPacket)
                else:
                    log_window.log(f"Received an unknown packet type ({packet_type}).")
                    Return.append("unknownPacket")
            else: 
                break
        return Return
        #while loop end
    else:
        log_window.log(str(ID) + "| Breaking connection because of no response!")
        Return.append(False)  # Connection has closed.
    return Return
    
app = Flask(__name__)

# Define a route to display the CarInfo dictionary as JSON

def getPackets(sock,ID,buffer,packetReceivedAll,packetReceived):
    packetsReceived = checkPacket(sock,ID,buffer)
    packetReceivedAll += packetsReceived
    #lastPacketReceived = packetReceivedAll[-1]
    #log_window.log(f"{ID}| packetsReceived: {str(packetsReceived)}")
    return packetsReceived;

async def main():
    global firstMsg
    global batchCount
    global batchApproval
    global road_lanes
    global firstMSOReceived
    sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    packetReceived = {}
    packetReceivedAll = []
    ID = "Main"
    buffer = b''  # Initialize the buffer as bytes.
    packetGetter = partial(getPackets,sock,ID,buffer,packetReceivedAll,packetReceived)
    log_window.log("LFS Translator Mod")
    log_window.log("Author - Ibrahim Khurram")
    log_window.log("Email - ibrahimkhurram407@gmail.com")
    log_window.log("Discord - anonymousgambeats")
    log_window.log("Github - github.com/ibrahimkhurram407")
    log_window.log("Threads Running: " + str(instance_threads))
    log_window.log("log Destination: " + log_destination)
    log_window.log(f"{ID}| Connecting to InSim: {insim_host}:{insim_port}")
    sock.connect((insim_host, int(insim_port)))
    # Encode string values to bytes before packing them into the packet.
    if admin_pass == None:
        admin_password = b'0907'
    else:
        admin_password = admin_pass
    InSIM_Nick = b'^3TRAFFIC AI'
    uport = 0
    await sendISP_ISI(admin_password, InSIM_Nick, ID,sock, 32, uport)
    packetsReceived = packetGetter()# ISP_VER received

    # Add functionality to verify that if the message was sent ISP_MSO
    firstMSOReceived = False
    sendISP_MSL(firstMsg, ID, sock)

    while not firstMSOReceived:
        CheckQuit(ID,sock)
        log_window.log(str(ID) + "| Waiting for first messaged to be Sent!")
        log_window.log(f"{ID}| looppacketsReceived: {str(packetsReceived)}")
        for packet in packetsReceived:
            if isinstance(packet,dict):
                if packet['kind'] == "ISP_MSO":
                    log_window.log(f"Received Packet: {packet}")
                    if "firstMSOReceived" in packet:
                        log_window.log(packet['firstMSOReceived'])
                        if packet["firstMSOReceived"] == True:
                            log_window.log("triggered!")
                            firstMSOReceived = True
                            break
            await asyncio.sleep(0.5)
        if firstMSOReceived == False:
            packetsReceived = packetGetter()
        else: 
            break
    log_window.log(f"{ID}| First message Received!")
    #Add functionality to listen for mso packets and input commands
    while True:
        packetReceived = packetGetter()
        if False in packetReceived:
            break
    #And also add responding logic for mso and input commands 
        
    # Release the socket.
    closeConnection(ID,sock)
    retriveAllData()
    # Copy the log file before closing the GUI window
    storeLogs(log_destination)
    # Close the root window when your application is done
    root.quit()  # Use root.quit() to properly close the GUI window
# Check if this script is the main script being run
if __name__ == "__main__":
    # Launch the GUI configuration window
    launchConfigGUI()