##################################################################
##################################################################
### Make directories with dates in the names                   ###
##################################################################
##################################################################

# import outside libraries
import os # operating system libraries
from datetime import datetime, timedelta, date #functions that calculate dates and times
import sys # for graceful exiting of program
from pathlib import Path    # this translates directory path syntax based on the OS (windows: swaps backslash and forward slash)
from tkinter import Tk, StringVar, IntVar, Entry,\
                    Button, Grid, Label, Scale,\
                    Radiobutton, Listbox, Frame,\
                    Grid, Pack, BOTH, N, S, E, W,\
                    HORIZONTAL, Text, END
from tkinter import filedialog # this manages a call to the Win OS in native gui format to pick files or directories

######################################################################
### Build the Tkinter gui as a class object with command functions ###
######################################################################
class Window(Frame):                    #the object is called "Window"
    # Variables used within the scope of this object (used by all child methods)
    series_type = "w"                   # set default to weeks
    series_length_w = 52                # set default to 52 weeks of directories (1 year)
    series_length_m = 12                # set default to 12 months of directories (1 year)
    os_dir_prefix = "c:\\temp\\"        # default location where new directories might be created
    directory_names_list = list()       # instantiate the empty list
    
    def __init__(self, master=None):    # required by Tkinter, this function runs automatically upon object instantiation, setting up all widgets
        Frame.__init__(self, master)    # required by Tkinter, initializes the parent window (aka "master")
        self.master = master            # declares the new object as the parent GUI object

        # parent widget can take all window space
        self.pack(fill=BOTH, expand=1)  # I am using the GRID geometry (not PACK), but I think this is required for the parent window

        start_year = IntVar()           # creates instances of variables that can be passsed
        start_month = IntVar()          # between Tkinter and Python.
        start_day = IntVar()            # IntVar() or StringVar() tells Tkinter to create that variable
        dir_text = StringVar()          # of the string type on the Tkinter side too. (as far as I understand)

        start_year.set(2020)            # set to defaults to make sure there are no null errors
        start_month.set(1)
        start_day.set(1)
        dir_text.set("Default")

        # This calls the validation function as seen on Stackoverflow by Brian Oakley
        # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        validate_cmd = (self.register(self.onValidateIsInteger),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # create input boxes for directory text name, year, month and day
        # text name input box
        self.dir_text_name_label = Label(self, text="Text Name:")
        self.dir_text_name_label.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.dir_text_name = Entry(self, textvariable = dir_text)
        self.dir_text_name.grid(row=4, column=1, padx=5, pady=5, sticky=W)

        # year input box
        self.dir_year_label = Label(self, text="4 Digit Year:")
        self.dir_year_label.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.dir_year = Entry(self, textvariable = start_year, validate="key", validatecommand=validate_cmd)
        self.dir_year.grid(row=5, column=1, padx=5, pady=5, sticky=W)

        # month input box
        self.dir_month_label = Label(self, text="2 Digit Month:")
        self.dir_month_label.grid(row=6, column=0, padx=5, pady=5, sticky=W)
        self.dir_month = Entry(self, textvariable = start_month, validate="key", validatecommand=validate_cmd)
        self.dir_month.grid(row=6, column=1, padx=5, pady=5, sticky=W)

        # day input box
        self.dir_day_label = Label(self, text="2 Digit Day:")
        self.dir_day_label.grid(row=7, column=0, padx=5, pady=5, sticky=W)
        self.dir_day = Entry(self, textvariable = start_day, validate="key", validatecommand=validate_cmd)
        self.dir_day.grid(row=7, column=1, padx=5, pady=5, sticky=W)

        #Create other widgets
        # create file directory request button and label to show selected target location
        self.dirLabel = Label(self, text="[not yet selected]")
        self.dirLabel.grid(row=10, column=1, padx=5, pady=5, sticky=W)
        self.dirButton = Button(self, text="Select Target Directory", command=self.clickDirButton)
        self.dirButton.grid(row=10, column=0, padx=5, pady=5, sticky=W)

        # create a label to show the current text of the starting directory as configured
        self.labelCurDir = Label(self, text="First Directory Name:") # gui label describing the current text field
        self.labelCurDir.grid(row=11, column=0, padx=5, pady=5, sticky=W)
        self.currentDirText = Label(self, text="[not yet constructed]") # label that displays the current text for the first directory
        self.currentDirText.grid(row=11, column=1, padx=5, pady=5, sticky=W)

        # create a lable describing the Text widgets below
        self.dirListingLabel = Label(self,text="List of Proposed Directories to Create:")
        self.dirListingLabel.grid(row=12, column=0, columnspan=2, padx=6, pady=5, sticky=W)
        
        # create a Text widget and a Scrollbar to display the list of proposed directories
        self.dirListingLeft = Text(self, height=26, width=50)   #set to default 52 lines of text for 52 weeks
        self.dirListingLeft.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky=W)
        self.dirListingRight = Text(self, height=26, width=50)   #set to default 52 lines of text for 52 weeks
        self.dirListingRight.grid(row=13, column=2, columnspan=2, padx=5, pady=5, sticky=W)

        # create radio buttons and slider widgets to choose between weekly and monthly directories
        # 2 slider widgets built at same location, only 1 is visible depending on which option was selected
        # weekly radio button and slider
        self.w_radio_button = Radiobutton(self, text="Weeks", value="w", command=self.wRadioSelect)
        self.w_radio_button.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.w_radio_slider = Scale(self, from_=1, to=52, length=220, orient=HORIZONTAL, command=self.wSliderMoved) # max 52 weeks (1 year)
        self.w_radio_slider.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=W) # this slider visible by default
        self.w_radio_slider.set(value=52) #set the slider to the default
        # monthly radio button and slider
        self.m_radio_button = Radiobutton(self, text="Months", value="m", command=self.mRadioSelect) # monthly radio button
        self.m_radio_button.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.m_radio_slider = Scale(self, from_=1, to=12, length=220, orient=HORIZONTAL, command=self.mSliderMoved) # max 12 months (1 year)
        self.m_radio_slider.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=W) # creates slider widget, but next line hides it
        self.m_radio_slider.set(value=12) #set this slider to the deault
        self.m_radio_slider.grid_forget() # make this widget disappear after instantiation by default

        self.w_radio_button.invoke() # trigger weekly radiobutton  option as default when created

        # create EXIT button, link it to clickExitButton()
        self.exitButton = Button(self, text="Exit", command=self.clickExitButton)
        self.exitButton.grid(row=0, column=3, padx=5, pady=5, sticky=E)

        # create APPLY button, gather all inputs and build a starting directory name
        self.applyButton = Button(self, text="Apply", command=self.applyButtonPress)
        self.applyButton.grid(row=1, column=3, padx=5, pady=5, sticky=E)

        # create WRITE button to write new directories to disk
        self.writeButton = Button(self, text="Write", command=self.writeButtonPress)
        self.writeButton.grid(row=2, column=3, padx=5, pady=5, sticky=E)

    # Validation function to check that only integers are put into year/month/day fields
    # Must return only True or False
    def onValidateIsInteger(self, d, i, P, s, S, v, V, W):
        # Disallow anything but integers
        if S.isdigit() or S=="" or S=="\b" or S==None:  # input it digit or null or blank etc
            return True
        else:
            self.bell() #makes a ding error sound?
            return False

    # Command for button to exit program
    def clickExitButton(self):
        exit()
    
    # Command for apply button to update text
    def applyButtonPress(self):
        self.updateCurrentDirText() # update the gui and the variables to build the directory names
    
    # Command for write button to write the directories to disk
    def writeButtonPress(self):
        self.updateCurrentDirText()
        count=0
        for count in range(len(self.directory_names_list)):
            os.makedirs(self.directory_names_list[count])

    # Command when weekly radio button selected
    def wRadioSelect(self):
        global series_type
        series_type = "w"
        self.w_radio_slider.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=W) # make this appear again
        self.m_radio_slider.grid_forget()         # make the other widget disappear
        self.updateCurrentDirText()               # update the gui and the variables to build the directory names

    # Command when Weekly Slider Widget is Moved
    def wSliderMoved(self, event):
        self.series_length_w = self.w_radio_slider.get() # read the current position of the slider widget

    # Command when monthly radio button selected
    def mRadioSelect(self):
        global series_type
        series_type = "m"
        self.m_radio_slider.grid(row=1, column=0, padx=5, pady=5, columnspan=2, sticky=W)   #make this appear again
        self.w_radio_slider.grid_forget()           # make the other widget disappear
        self.dir_day_label.grid_forget()            # make the day label disappear because it isn't used for monthly directory names
        self.dir_day.grid_forget()                  # make the day input disappear because it isn't used for monthly directory names
        self.updateCurrentDirText()                 # update the gui and the variables to build the directory names

    # Command when Monthly Slider Widget is Moved
    def mSliderMoved(self, event):
        self.series_length_m = self.m_radio_slider.get() # read the current position of the slider widget

    # Command when the select directory button is activated
    def clickDirButton(self):
        self.os_dir_prefix = filedialog.askdirectory() + "\\"   # uses the operating system's native file dialog GUI widget
        self.dirLabel.config(text=self.os_dir_prefix)    # label to show the user what they selected
        self.updateCurrentDirText()                 # trigger an update based on new user input

    # This function should be called whenever the user provides new input
    # updates the display of information and updates the directory names being built
    def updateCurrentDirText(self):
        self.directory_names_list.clear()           #clear out the list, just to be safe, before filling it again

        temp_name = self.dir_text_name.get()        # grabing the values from the Entry fields

        temp_year = self.dir_year.get()             # this variable passing stuff is super confusing
        temp_month = self.dir_month.get()           # I doubt this is the best way to do it
        temp_day = self.dir_day.get()               # also: need to convert the entry field data into integers for date calculation

        calc_year = int(self.dir_year.get())        # two sets of date variables retrieved
        calc_month = int(self.dir_month.get())      # because I need to use strings (above) to make the names
        calc_day = int(self.dir_day.get())          # but I also need integers for date fields because timedelta function requires integers

        # build the full starting directory name, weekly includes day, monthly does not include the day
        if series_type == "w":
            start_dir_name = temp_name + "-" + temp_year + "-" + temp_month + "-" + temp_day
            list_date = date(calc_year, calc_month, calc_day)  # turn the start date into 1st list item
            # build the weekly list by calculating weekly dates
            count = 0
            while count < self.series_length_w:
                new_directory_name = Path(self.os_dir_prefix + temp_name + "-" + list_date.strftime("%Y-%m-%d"))  # convert new date to a string
                self.directory_names_list.append(new_directory_name)    # add it to the list
                list_date = list_date + timedelta(days=7)               # advance the date 7 days forward on the calendar
                count = count + 1
        # build the monthly list (doesn't need to calculate dates)
        else:
            start_dir_name = temp_name + "-" + temp_year + "-" + temp_month + "-"
            
            count = 0
            while count < self.series_length_m:
                new_directory_name = Path(self.os_dir_prefix + temp_name + "-" + temp_year + "-" + str(count).zfill(2))
                self.directory_names_list.append(new_directory_name)    # add it to the list
                count = count + 1
        
        # display updated name on the gui label for the user
        self.currentDirText.config(text=start_dir_name)

        # Update the listbox to display the new set of proposed directories to be created
        self.dirListingLeft.delete(1.0, END)                #clear the text box before upating with new info
        self.dirListingRight.delete(1.0, END)
        count = 0
        for count in range(len(self.directory_names_list)):
            temp_string = '{:>3}'.format("#" + (str(count+1))) + ": " + str(self.directory_names_list[count]) + "\n"
            if count<26: self.dirListingLeft.insert(END, temp_string)   #write to the Left Text widget box until full
            else: self.dirListingRight.insert(END, temp_string)         #write to the Right Text widget box after Left is full


############################################################
# This is where the program actually starts running
############################################################

# initialize tkinter and create the root object/process
root = Tk()                 # Tkinter code wrapper assigned to the variable "root." This pulls Tkinter code inside this program.
this_app = Window(root)     # Generates a new master/parent object called "Window" of type "root" (aka Tkinter)

# set basic properties of newly created window
root.wm_title("Create Directories with Names and Dates")
root.geometry("730x750")

# Display new window and start up endless loop that waits for interaction by user
root.mainloop()

#############
sys.exit()   #STOPS THE CODE FOR NOW HERE
#############