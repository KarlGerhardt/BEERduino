# bin/usr/python

#User defined variables----------------------------------------

open_time=2 # number of seconds the solenoid will remain open

pour_vol=16 # Volume of beer dispensed per pour (in oz.)
beer_ABV= 0.05  # Alcoohol by volume for the current keg

intoxicated=0.16 # BAC cutoff level

# Setting up other things--------------------------------------

# Setup GPIO pins for switching the solenoid valve

from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) # Identifies the pin numbers to the pi
GPIO.setwarnings(False)

GPIO.setup(3, GPIO.OUT) # Should sets pin #3 as an output...but doesnt work yet
GPIO.setup(3, GPIO.LOW) # Turns initial output for pin 3 off

# Import necessary functions 

from CheckLicense import check_license #function for checking age and validity of DL
from Calc_BAC import calc_BAC #function for calculating BAC of a user             

import getpass
import sys
import re
import time
timestr = time.strftime("%Y%m%d %H%M%S")
                  

# Setting up font classes
class color:
    BOLD='\033[1m'
    END= '\033[0m'
    GREEN= '\033[92m'
    RED='\033[91m'
    

# Setting a while loop to run continuously and a try statement for error handling------------------

while True:
    try:
    
# Operating modes---------------------------------------------------------------

    #Have admin set up operating mode
        mode_req=raw_input("Enter Mode(normal, party, barkeep): ")

# Normal mode is for general tracking of registered users during standard use
# Party mode is for regulating use while gests are present (ie non registered users)
# Barkeep mode is used to control BAC levels when numerous guests are present

        if mode_req=="party":
             passwd=getpass.getpass("Enter password:")
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
                print '{0} mode!' .format(mode)

            # Send text from magnetic strip swipe to the function 'check_license' and collect output
                raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 

                check_license_out=check_license(raw_text)

                valid_license=check_license_out[0] 
                first_name=check_license_out[1]
                last_name=check_license_out[2]
                DL_num=check_license_out[3]
                
            # Check to see if the user is a registered user

                users=open("users_list.txt", 'r') # use defined users list

                hit=0 #random counter for matching DL line by line
                       
                if valid_license=='Yes':
                      for line in users:
                              if re.search(DL_num, line, re.IGNORECASE):
                                      hit=hit+1
                      if hit>=1:
                              valid_license='Yes'
                      else: 
                              print 'Not registered user'
                              valid_license='No'

            # Calculating the user's current BAC

                BAC1_raw=calc_BAC(raw_text, beer_ABV, pour_vol) # Sends text from DL swipe, ABV of current beer and pour vol to func calc_BAC 
                BAC1=format(BAC1_raw, '.3f') #formats BAC to 3 decimals
               

            # Opening the solenoid to dispense beer
                if valid_license=='Yes':
                      GPIO.setup(3, GPIO.HIGH) # Sends output through pin 3 to open solenoid
                      print 'Beer time!'
                      sleep(open_time); # Holds the solenoid open for a designated period of time (user defined variables)
                      GPIO.setup(3, GPIO.LOW) #Closes solenoid

                      with open("swipes.txt", "a") as myfile:  # Prints the user's info (name, date, and DL number) to a specified 'swipes' file
                              myfile.write(last_name+","+first_name+" ")
                              myfile.write(DL_num+" ")
                              myfile.write(mode+" ")
                              myfile.write(time.strftime("%Y-%m-%d")+" ")
                              myfile.write(str(time.time())+"\n")

            # Calculating the BAC after finishing this beer
                      BAC2_raw=calc_BAC(raw_text, beer_ABV, pour_vol) #Calculates the user's BAC after drinking this beer
                      BAC2=format(BAC2_raw, '.3f')

                      print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END
                      print " "
        
            except (NameError, IndexError, ValueError):
                print color.RED + 'Error!' + color.END
                continue

#Party mode operations--------------------------------------------------------------------------------------------
                                     
        while mode=="party":
            try:
                 print '{0} mode!' .format(mode)
                 
            # Send text from magnetic strip swipe to the function 'check_license' and collect output

                 raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 

                 check_license_out=check_license(raw_text)
                    
                 valid_license=check_license_out[0] 
                 first_name=check_license_out[1]
                 last_name=check_license_out[2]
                 DL_num=check_license_out[3]

            # Calculating the current BAC
                 BAC1_raw=calc_BAC(raw_text, beer_ABV, pour_vol)
                 BAC1=format(BAC1_raw, '.3f')

            # Opening the solenoid 

                 if valid_license=='Yes':
                         GPIO.setup(3, GPIO.HIGH)
                         print 'Beer time!'
                         sleep(open_time);
                         GPIO.setup(3, GPIO.LOW)
                      
                    # write user information to 'swipes' file
                         with open("swipes.txt", "a") as myfile:
                             myfile.write(last_name+","+first_name+" ")
                             myfile.write(DL_num+" ")
                             myfile.write(mode+" ")
                             myfile.write(time.strftime("%Y-%m-%d")+" ")
                             myfile.write(str(time.time())+"\n")

            # Calculating the BAC after finishing this beer
            
                         BAC2_raw=calc_BAC(raw_text, beer_ABV, pour_vol)
                         BAC2=format(BAC2_raw, '.3f')

                         print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END
                         print " "


            except (NameError, IndexError, ValueError):
                 print color.RED + 'Error!' + color.END
                 continue
                                  
#Barkeep mode operations-------------------------------------------------------------------------------------------
     
        while mode=="barkeep":
            try:
                print '{0} mode!' .format(mode)

            # Send text from magnetic strip swipe to the function 'check_license' and collect output

                raw_text=getpass.getpass(color.GREEN + 'Swipe card now:   ' + color.END).strip() 

                check_license_out=check_license(raw_text)
                    
                valid_license=check_license_out[0] 
                first_name=check_license_out[1]
                last_name=check_license_out[2]
                DL_num=check_license_out[3]

            # Calculating the current BAC
                BAC1_raw=calc_BAC(raw_text, beer_ABV, pour_vol)
                BAC1=format(BAC1_raw, '.3f')

            # Checking to see if the user has been previously banned from the keg by searching the 'blacklist' file
                blacklist=open("blacklist.txt", 'r')

                hit=0
                
                if valid_license=='Yes':
                     for line in blacklist:
                             if re.search(last_name, line, re.IGNORECASE):
                                     hit=hit+1
                             if re.search(first_name, line, re.IGNORECASE):
                                     hit=hit+1
                     if hit>=2:
                             print "No beer for you!"
                             blacklisted='Yes'
                     else: 
                             blacklisted='No'

                                     
            #Opening the solenoid (user must not be banned and must have a BAC below the defined level)
                if blacklisted=='No' and valid_license=='Yes':
                    if BAC1 < intoxicated:
                        GPIO.setup(3, GPIO.HIGH) #Opens solenoid
                        print 'Beer time!'
                        print BAC
                        sleep(open_time);
                        GPIO.setup(3, GPIO.LOW)

                     # Write user information to 'swipes' file
                        with open("swipes.txt", "a") as myfile:
                             myfile.write(last_name+","+first_name+" ")
                             myfile.write(DL_num+" ")
                             myfile.write(mode+" ")
                             myfile.write(time.strftime("%Y-%m-%d")+" ")
                             myfile.write(str(time.time())+"\n")

            #Calculating the BAC after finishing this beer
                             BAC2_raw=calc_BAC(raw_text, beer_ABV, pour_vol)
                             BAC2=format(BAC2_raw, '.3f')
                             print color.BOLD + "Your current BAC is",BAC1,"after this beer your BAC will be",BAC2 + color.END
                             print " "


                    else:
                        print "Sorry, BAC is too high"
                        print " "
                            
                        
            except (NameError, IndexError, ValueError):
                print color.RED + 'Error!' + color.END
                continue
                        
#---------------------------------------------------------------------------


    except (NameError, IndexError, ValueError):
        print color.RED + 'Error!' + color.END
        continue


#end ---------------------------------------------------------------------------
        
