#--------------------------------
# Developed in May-November 2018 by Caedmon DelVecchio and Ethan Adams of the Silicon Iniative,
# as part of the Berks Technology Club at Penn State Berks
#--------------------------------

from __future__ import print_function
import sys
import datetime
import json
from random import randint
from tkinter import *
from tkinter import messagebox
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

mGui = Tk()
mGui.configure(background='black')

# ------------ TODO -----------------
#1. Admin ability to add users from the touchscreen
#2. Admin Log out user in case someone forgets to log out. If possible add designation for someone logged out by admin.
#3. Add specified exceptions for errors

#--------- VARIABLES ----------------
SPREADSHEET_ID = '1PePbDjFYSs-XhJ7S470KEMO85hgEcNa9AyNE5a2nTNQ' # Google spreadsheet ID
CLIENT_SECRET_FILEPATH = 'client_secret.json' # Path for the OAuth file provided by Google for the API
STUDENT_JSON_FILEPATH = 'members.json' # Path to JSON file to load student data
APP_FULLSCREEN = False # If true, application runs in fullscreen

signedOutDict = {} # Users signed out {studentID: {lName, Fname}}
signedInDict = {} # Users signed in {studentID: [updateRange, lName, Fname]}

# -------- FUNCTIONS ----------------

#def hide(choice):
#        idTextBox.grid_remove()

def signIn(studentID):
    try:
        student = signedOutDict[studentID]
    except KeyError:
        print("Invalid input in the entry field.")
        messagebox.showerror("Error", "Please swipe your student ID again.")
        idTextBox.delete(0, END) # Clear text field for next entry
        idTextBox.focus() # Apply focus to entry field
        return 1

    timestamp = datetime.datetime.now() # Time logging in
    #GUI Signin
    activeStudent = student["lName"] + ", " + student["fName"] # Student logging in
    activeStudentIndex = outListbox.get(0,END).index(activeStudent)
    inListbox.insert(END, activeStudent) # Inserts selected student to Signed In list
    outListbox.delete(activeStudentIndex) # Deletes selected student from Signed Out list
    signedInDict[studentID] = {"lName": student["lName"], "fName": student["fName"]} # Add student to logged in dict
    signedOutDict.pop(studentID) # Remove student from signed out dictionary
    idTextBox.delete(0, END) # Clear text field for next entry
    idTextBox.focus() # Apply focus to entry field
    
    # Add values to spreadsheet
    body = { 'values' : [[student["lName"], student["fName"], timestamp.strftime("%x"), timestamp.strftime("%X")]]} # [Student Fname, Student Lname, Date, Time]
    range = "A1:D1" # Range of table to append to
    result = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=range, valueInputOption='RAW', body=body).execute() # Execute spreadsheet update

    # Store spreadsheet range for student
    updateResultRange = result.get('updates')["updatedRange"].replace("A", "E").replace("D", "F") # Modify range used for sign out later
    signedInDict[studentID].update({"updateRange": updateResultRange})

    # Output result
    print('{0} cells appended.'.format(result.get('updatedCells')))
    print(activeStudent + " signed in at " + timestamp.strftime("%x %X"))
    

def signOut(studentID):
    studentID = idTextBox.get()[2:11] # Get substring of ID read from ID card
    try:
        student = signedInDict[studentID] # [updateRange, lName, fName]
    except:
        print("Invalid input in the entry field.")
        messagebox.showerror("Error", "Please swipe your student ID again.")
        idTextBox.delete(0, END) # Clear text field for next entry
        idTextBox.focus() # Apply focus to entry field
        return 1
    timestamp = datetime.datetime.now() # Time logging out

    #GUI Signout
    activeStudent = student["lName"] + ", " + student["fName"] # Student logging out
    activeStudentIndex = inListbox.get(0,END).index(activeStudent)
    outListbox.insert(END, activeStudent) # Deletes selected student from Signed In list
    inListbox.delete(activeStudentIndex) # Inserts selected student to Signed Out list
    signedOutDict[studentID] = {"lName": student["lName"], "fName": student["fName"]} # Add student to logged in dict
    signedInDict.pop(studentID) # Remove student from signed in dictionary
    idTextBox.delete(0, END) # Clear text field for next entry
    idTextBox.focus() # Apply focus to entry field

    # Add values to spreadsheet
    body = { 'values' : [[timestamp.strftime("%x"), timestamp.strftime("%X")]]} # Time signed out
    range = student["updateRange"]
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=range, valueInputOption='RAW', body=body).execute() # Execute spreadsheet update

    # Output Result
    print('{0} cells updated.'.format(result.get('updatedCells')))
    print(str(student["lName"]) + ", " + str(student["fName"]) + " signed out at " + timestamp.strftime("%x %X"))
    

def updateClock(): # Update date and time labels every minutes
    #Update time label
    timeString = datetime.datetime.now().strftime("%H:%M")
    timeLabel.configure(text = timeString)
    timeLabel.configure(background='black', foreground="white")
    # Update date label
    dateString = datetime.datetime.now().strftime("%B %dth, %Y")
    dateLabel.configure(text = dateString)
    dateLabel.configure(background='black', foreground="white")

    mGui.after(60000, updateClock) # Run function every minute in the tkinter mainloop

# Runs anytime the Entry field is modified
def callback(sv):
    idEntryText = idTextBox.get()

    # If the input is long enough to contain the ID from the card
    if (len(idEntryText) >= 59):
        print(idEntryText[2:11])
        if (idEntryText[2:11] in signedOutDict):
            print("signedOutDict")
            signIn(idEntryText[2:11])
        elif (idEntryText[2:11] in signedInDict):
            print("signedInDict")
            signOut(idEntryText[2:11])
        else:
            print("Error: Not in dict")

def clearEntry(): # Clear the entry text box
    idTextBox.delete(0, END) # Clear text field for next entry
    idTextBox.focus() # Apply focus to entry field


# -------- END OF FUNCTIONS ----------------

# -------- GOOGLE SPREADSHEETS API ----------------

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILEPATH, SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# -------------- END OF GOOGLE SPREADSHEET API ------------------

# Read student data from JSON file
with open(STUDENT_JSON_FILEPATH, 'r') as f:
        signedOutDict = json.load(f)

# -------------- GUI CREATION --------------------------------
mGui.geometry('800x450+0+0')
mGui.title('Veterans Lounge Sign In Sheet')

#Date
dateString = datetime.datetime.now().strftime("%B %dth, %Y")
dateLabel = Label(mGui, text=dateString, font = 'Helvetica 20 bold')
dateLabel.pack(anchor = "center")

#Time
timeString = datetime.datetime.now().strftime("%H:%M")
timeLabel = Label(mGui, text=timeString, font = 'Helvetica 20 bold')
timeLabel.pack(anchor = "center")

#Instructions
instructLabel = Label(mGui, text="SWIPE YOUR STUDENT ID", font = 'Helvetica 20 bold')
instructLabel.pack(anchor = "center", pady = (30, 0))
instructLabel.configure(background='black', foreground="red")

#Outside Room
outside = Label(mGui, text = "Signed Out", font = 'Helvetica 10 bold')
outside.place(x=50, y=0)
outside.configure(background='black', foreground="white")

#Student List
outListbox = Listbox(mGui, font = 12)
outListbox.place(x=15, y=20, height=420, width=150)
outListbox.configure(background='black', foreground="white", highlightcolor="blue", highlightbackground="blue")

#Penn State ID Text Box
sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: callback(sv))
idTextBox = Entry(mGui, show="*", text='PSU ID', textvariable=sv)
idTextBox.config(state=NORMAL)
idTextBox.pack(anchor = "center")
idTextBox.configure(background='black', foreground="white")

#SIGN IN
#mbutton = Button(mGui, text = 'SIGN IN', command = signin, font = 'Helvetica 30 bold', fg = 'black', bg='#c4c4c4')
#mbutton.pack(anchor = "center")

#SVA LOGO
image = PhotoImage(file="Logo.png") # Load image
banner = Label(image=image)
banner.pack(anchor = "center", pady = (15, 15))
banner.configure(background='black', foreground="white")

#Clear Entry
button2 = Button(mGui, text = 'CLEAR ENTRY', command = clearEntry, font = 'Helvetica 30 bold', fg = 'black', bg='#c4c4c4')
button2.pack(anchor = "center")

#Inside Room
inside = Label(mGui, text = "Signed In", font = 'Helvetica 10 bold')
inside.place(x=675, y=0)
inside.configure(background='black', foreground="white")

#inListbox
inListbox = Listbox(mGui, font = 12)
inListbox.place(x=635, y=20, height=420, width=150)
inListbox.configure(background='black', foreground="white", highlightcolor="blue", highlightbackground="blue")

for items in signedOutDict.items():
    outListbox.insert(END, items[1]["lName"] + ", " + items[1]["fName"])

idTextBox.focus() # Apply focus to entry field

mGui.attributes("-fullscreen",APP_FULLSCREEN)
mGui.after(1000, updateClock) # Begin updating clock datetime loop
mGui.config(cursor="none")
mGui.mainloop()
