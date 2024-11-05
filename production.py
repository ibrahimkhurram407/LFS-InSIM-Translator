#product key system
import mysql.connector
import wmi
import os
from dotenv import load_dotenv
import tkinter as tk
from functools import partial
import pyautogui
global productKey
productKey = ""

def submit(root,entry):
    global productKey
    productKey = entry.get()
    # Do something with the product key, for example, save it in a variable
    print(f"Product key submitted: {productKey}")
    root.destroy()

def getProductKey():
    # Create the main window
    root = tk.Tk()
    root.title("Product Key Entry")

    # Create a label
    label = tk.Label(root, text="Enter your product key:")
    label.pack(pady=10)

    # Create an entry widget
    entry = tk.Entry(root)
    entry.pack(pady=10)

    # Create a submit button
    subFunc = partial(submit,root,entry)
    button = tk.Button(root, text="Submit", command=subFunc)
    button.pack(pady=10)

    # Run the main loop
    root.mainloop()

# Check if .env file exists
def checkENV():
    if os.path.exists('.env'):
        # Load the contents of .env file
        load_dotenv()

        # Access environment variables
        key = os.getenv('product_key')

        if key:
            return key
        else:
            return False
    else:
        return False

def writeENV(name,value):
    # Create or update the .env file
    with open('.env', 'w') as env_file:
        env_file.write(f'{name}={value}\n')

def get_unique_hardware_info():
    c = wmi.WMI()
    for item in c.Win32_BaseBoard():
        return item.SerialNumber

def product_verification():
    global productKey
    env = checkENV()
    if env == False:
        getProductKey()
    else:
        productKey = env

    #Get Motherboard Serial Number
    unique_hardware_info = get_unique_hardware_info()
    print("Unique Hardware Info:", unique_hardware_info)

    mydb = mysql.connector.connect(
    host="ibrahimkhurram.com",
    port=3306,
    user="kali-server",
    password="Kali User 407",
    database="translator_production"
    )

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM productKeys;")

    productKeys = mycursor.fetchall()
    valid = False
    used = True
    productId = None
    for row in productKeys:
        IdCell= row[0]
        keyCell = row[1]  # Assuming 'key' is in the second column
        usedCell = row[2]  # Assuming 'used' is in the third column

        if keyCell == productKey:
            productId = IdCell
            valid = True
            if usedCell:
                used = True
                print("Product key has already been used before.")
            else:
                used = False
                print("Product key is valid.")
                mycursor.execute(f"""
                UPDATE productKeys
                SET used = 1
                WHERE id = {productId};
                """)
                # print(str(mycursor.fetchall()))
                mydb.commit()
                break
        else:
            valid = False
    if valid == False:
        print("Product key not valid")
        mydb.close()
        return False
    mycursor.execute(f"SELECT * FROM paired_hardware;")
    paired_hardware = mycursor.fetchall()
    for row in paired_hardware:
        IdCell = row[0]
        serialCell = row[1]

        if IdCell == productId:
            if serialCell == unique_hardware_info and used == True:
                if env == False:
                  writeENV('product_key', productKey)
                return True
            elif serialCell == f"noSerial{IdCell}" or used == False:
                mycursor.execute(f"""
                UPDATE paired_hardware
                SET serial = '{unique_hardware_info}'
                WHERE id = {IdCell};
                """)
                # print(str(mycursor.fetchall()))
                mydb.commit()
                if env == False:
                  writeENV('product_key', productKey)
                return True
            else:
                return False
            

    mydb.close()

product = product_verification()
if product == False:
    exit()


print("works!")