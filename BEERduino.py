# bin/usr/python

# User defined variables----------------------------------------
open_time=2 # number of seconds the solenoid will remain open
pour_vol=16 # Volume of beer dispensed per pour (in oz.)
beer_ABV= 0.05  # Alcoohol by volume for the current keg
intoxicated=0.16 # BAC cutoff level
solenoidPin = 3
# --------------------------------------------------------------

# Setup GPIO pins for switching the solenoid valve
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) # Identifies the pin numbers to the pi
#GPIO.setwarnings(False)
GPIO.setup(solenoidPin, GPIO.OUT) # Should sets pin #3 as an output...but doesnt work yet
GPIO.output(solenoidPin, GPIO.LOW) # Turns initial output for pin 3 off

# Import necessary functions 
from CheckLicense import check_license #function for checking age and validity of DL
from Calc_BAC import calc_BAC #function for calculating BAC of a user             
import getpass, sys, re, time
timestr = time.strftime("%Y%m%d %H%M%S")

# Setting up font classes
class color:
    BOLD='\033[1m'
    END= '\033[0m'
    GREEN= '\033[92m'
    RED='\033[91m'
    
class DLicense():
    '''License object parses input raw text from card reader and holds the appropriate variables.'''
    def __init__(self, raw_text):
        '''Parses raw_text and populates variables.'''
        # vars
        self.isValid = False
        self.num = None
        self.firstName = None
        self.lastName = None
        # Parse input text
        text=raw_text.replace('\'', ' ').replace('\"', ' ').replace('\*', ' ')
        # Check to make sure the swiped card is a drivers license and obtain DL number
        check_text=text.split(';')[1]
        check_num=int(check_text[0:4]) # Indicator of drivers' licenses
        if check_num==6360:
            self.isValid=True
        else:
            self.isValid=False
            print 'Try swiping a drivers license'
        self.num=check_text[6:14] #Save DL number for identification
        # Parsing license info to determine validity of license and age of user
        dates_text=text.split('=')[1]
        # Separate out dates by year, month, and day
        self.exp_yr=int(dates_text[0:2])
        self.exp_mo=int(dates_text[2:4])
        self.br_yr=int(dates_text[4:8])
        self.br_mo=int(dates_text[8:10])
        self.br_dt=int(dates_text[10:12])
        # Identifying the user's  name
        name_text=text.split('^')[1]
        names=name_text.replace('$', ' ').split(' ') # some DLs use $ and spaces in names
        self.firstName=names[0]
        self.lastName=names[-1]
        print color.BOLD + self.firstName, " ", self.lastName + color.END
        #Parsing text to identify weight and gender
        phys_text=text.split('+') # Remove first half of code
        phys_text=re.sub(' ','',phys_text[1]) #Removing extra spaces
        phys_text=re.split('(\d+)',phys_text,flags=re.IGNORECASE) # split out whenever letters and numbers are together
        phys_info=phys_text[3] # This set of numbers contains gender, height, and weight
        # Assigning weight obtained from DL
        weight_lb=int(phys_info[4:7])
        self.weight=weight_lb/2.2
        # Assigning gender constant for BAC fomula
        if int(phys_info[0])==1 or 'F':
            self.gender = 'F'
        elif int(phys_info[0])==2 or 'M':
            self.gender = 'M'
        
    def checkLicense(self):
        '''Ensures swiped card is a license. Also confirms expiration and determines if the user is of age.
        Output modifies self.isValid to be correct.'''
        # Current time
        timestr = time.strftime("%Y%m%d%H%M%S")
        cur_yr=int(timestr[0:4]) #Using 4 digit year
        cur_yr_2=int(timestr[2:4]) #Using 2 digit year
        cur_mo=int(timestr[4:6])
        cur_dt=int(timestr[6:8])
        # check to see that license is still valid
        expired_msg = 'Sorry your license has expired!'
        if self.isValid:
            if cur_yr_2>self.exp_yr:
                print expired_msg
                self.isValid=False
            elif cur_yr_2==self.exp_yr:
                if cur_mo>self.exp_mo:
                        print expired_msg
                        self.isValid=False
    
        #Check to see if the user is over 21
        under_21_msg= 'You appear to be under 21 - no beer for you!'
        if self.isValid:
            if cur_yr-self.br_yr<21:
                self.isValid=False
                print under_21_msg
            elif cur_yr-self.br_yr==21:
                if cur_mo<self.br_mo:
                    self.isValid=False
                    print under_21_msg
                elif cur_mo==self.br_mo:
                    if cur_dt<self.br_dt:
                        self.isValid=False
                        print under_21_msg
                    elif cur_dt==self.br_dt:
                        print 'Happy 21st Birthday!'
                        
def calc_BAC(DL,ABV,pour_vol):
    '''Calculates BAC based on physical info.
    Inputs:
        dl (DLicense obj) - driver license object
        ABV (float) - ABV of the beer on tap
        pour_vol (float) - volume of a single pour (probably 16oz)
    Returns:
        BAC (float)'''
    # Standard BAC constants 
    Body_H2O=0.806
    g_const=1.2
    t_const=0.015

    # Assigning gender constant for BAC fomula
    if DL.gender == 'F':
        gen_const= 0.58
    elif DL.gender == 'M':
        gen_const= 0.49
      
    ## Calculating the BAC for the individual
    swipes=open("swipes.txt", 'r')
    beer_alc_ratio=(pour_vol/12)*(ABV/0.05)   
    BAC=0
    for line in swipes:
        if re.search(DL.num, line, re.IGNORECASE):
            unix_time=line.split(' ')[-1]
            time_diff_hrs=(time.time()-float(unix_time))/3600.0
            ## Formula for calculating BAC
            contributing_BAC=(Body_H2O*g_const*beer_alc_ratio)/(DL.weight*gen_const)-t_const*time_diff_hrs
            if contributing_BAC >0:
                    BAC=BAC + contributing_BAC
    swipes.close()
    return BAC
    
def recordSwipe(DL, mode, swipefile="swipes.txt"):
    '''Records card swipe to swipes file.
    Inputs:
        DL (DLicense obj) - driver license to be recorded
        mode (str) - current operating mode
        swipefile (str) - path to swipes file that will be appended'''
    swipefile = open(swipefile, 'a')
    swipefile.write(DL.lastName+","+DL.firstName+" ")
    swipefile.write(DL.num+" ")
    swipefile.write(mode+" ")
    swipefile.write(time.strftime("%Y-%m-%d")+" ")
    swipefile.write(str(time.time())+"\n")
    swipefile.close()

def dispenseBeer(open_time=open_time, pin=solenoidPin):
    '''Dispenses beer for the set amount of time by opening the
    solenoid valve on the given pin.'''
    GPIO.output(pin, GPIO.HIGH) # Sends output through pin 3 to open solenoid
    print 'Beer time!'
    sleep(open_time); # Holds the solenoid open for a designated period of time (user defined variables)
    GPIO.output(pin, GPIO.LOW) #Closes solenoid
    
def checkMaxBAC(DL, BAC):
    '''Reads list of max BAC values for each user and overwrites value of greater.
    Used for scrolling sign.
    Inputs:
        DL (DLicense obj) -- driver license of the user
        BAC (float) -- current max BAC of the user, to be compared to the stored value
    Returns:
        float -- max recorded BAC for the given user'''
    BAC_max_filename = 'BAC_max.txt'
    BAC_max_file = open(BAC_max_filename, 'rb')
    BAC_max = None
    for line in BAC_max_file:
        if str(DL.num) in line:
            line = line.split('\t')
            BAC_max = [entry.strip() for entry in line]
    if BAC_max is None:
        print "Warning: adding new user to Max BAC list!"
        BAC_max_file.close()
        BAC_max_file = open(BAC_max_filename, 'ab')
        BAC_max_file.write('%s\t%s\t%s\t%s\n'%(DL.num, DL.firstName, DL.lastName, BAC))
        BAC_max_file.close()
        return BAC
    else:
        if BAC > BAC_max[-1]: # write new max to file
            BAC_max_file = open(BAC_max_filename, 'wb')


# Setting a while loop to run continuously and a try statement for error handling------------------
while True:
    try:
# Operating modes---------------------------------------------------------------
        #Have admin set up operating mode
        mode_req=raw_input("Enter Mode(normal, party, barkeep): ")

        # Normal mode is for general tracking of registered users during standard use
        # Party mode is for regulating use while guests are present (ie non registered users)
        # Barkeep mode is used to control BAC levels when numerous guests are present; users can be blacklisted
        if mode_req=="party":
            passwd=getpass.getpass("Enter password: ")
            if passwd=="admin":
                mode="party"
        if mode_req=="normal":
            passwd=getpass.getpass("Enter password: ")
            if passwd=="admin":
                mode="normal"
        if mode_req=="barkeep":
            passwd=getpass.getpass("Enter password: ")
            if passwd=="admin":
                mode="barkeep"

            
#Normal mode operations--------------------------------------------------------------------------------------------
        while mode=='normal':
            try:
                print '{0} mode!'.format(mode)
                
                # Send text from magnetic strip swipe to the function 'check_license' and collect output
                raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 
                DL = DLicense(raw_text)
                
                # Check to see if the user is a registered user
                users=open("users_list.txt", 'r') # use defined users list
                if DL.isValid:
                    for line in users:
                        if DL.num in line:
                            DL.isValid = True
                        else: 
                            print 'Not registered user'
                            DL.isValid=False
                users.close()
                
                # Calculating the user's current BAC
                BAC1_raw=calc_BAC(DL, beer_ABV, pour_vol) # Sends text from DL swipe, ABV of current beer and pour vol to func calc_BAC 
                BAC1=format(BAC1_raw, '.3f') #formats BAC to 3 decimals

                # Opening the solenoid to dispense beer
                if DL.isValid:
                    dispenseBeer()
                    recordSwipe(DL, mode)

                # Calculating the BAC after finishing this beer
                BAC2_raw=calc_BAC(DL, beer_ABV, pour_vol) #Calculates the user's BAC after drinking this beer
                BAC2=format(BAC2_raw, '.3f')

                print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END + '/n'
        
            except (NameError, IndexError, ValueError):
                print color.RED + 'Error!' + color.END
                continue

#Party mode operations--------------------------------------------------------------------------------------------
        while mode=="party":
            try:
                print '{0} mode!' .format(mode)
                 
                # Send text from magnetic strip swipe to the function 'check_license' and collect output
                raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 
                DL = DLicense(raw_text)

                # Calculating the current BAC
                BAC1_raw=calc_BAC(DL, beer_ABV, pour_vol)
                BAC1=format(BAC1_raw, '.3f')

                # Opening the solenoid 
                if DL.isValid:
                    dispenseBeer()
                    recordSwipe(DL, mode)

                # Calculating the BAC after finishing this beer
                BAC2_raw=calc_BAC(DL, beer_ABV, pour_vol)
                BAC2=format(BAC2_raw, '.3f')
                print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END + '/n'

            except (NameError, IndexError, ValueError):
                print color.RED + 'Error!' + color.END
                continue
                                  
#Barkeep mode operations-------------------------------------------------------------------------------------------
        while mode=="barkeep":
            try:
                print '{0} mode!' .format(mode)

                # Send text from magnetic strip swipe to the function 'check_license' and collect output
                raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 
                DL = DLicense(raw_text)

                # Calculating the current BACdddddddddddd
                BAC1_raw=calc_BAC(DL, beer_ABV, pour_vol)
                BAC1=format(BAC1_raw, '.3f')

                # Checking to see if the user has been previously banned from the keg by searching the 'blacklist' file
                blacklist=open("blacklist.txt", 'r')
                blacklisted = False
                if DL.isValid:
                    for line in blacklist:
                        if DL.lastName in line and DL.firstName in line:
                            print "No beer for you!"
                            blacklisted=True
                                     
                #Opening the solenoid (user must not be banned and must have a BAC below the defined level)
                if not blacklisted and DL.isValid:
                    if BAC1 < intoxicated:
                        dispenseBeer()
                        recordSwipe(DL, mode)

                        #Calculating the BAC after finishing this beer
                        BAC2_raw=calc_BAC(DL, beer_ABV, pour_vol)
                        BAC2=format(BAC2_raw, '.3f')
                        print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END + '/n'
                    else:
                        print "Sorry, BAC is too high/n"   
            except (NameError, IndexError, ValueError):
                print color.RED + 'Error!' + color.END
                continue
                        
#---------------------------------------------------------------------------
# Errors for outer while loop
    except (NameError, IndexError, ValueError):
        print color.RED + 'Error!' + color.END
        continue
    
    finally:
        GPIO.cleanup()