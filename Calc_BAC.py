#! usr/bin/python

import time
import sys
import re

# Function to calculate BAC ----------------------------------------------

def calc_BAC(a,b,c): # Calculates BAC based on physical info and # beers consumed

#a--text from DL magnetic strip
#b-- ABV for the current beer
#c-- Pour volume (in oz.)

    ABV=b

    pour_vol=c
    
    raw_text=a
    text=raw_text.replace('\'', ' ').replace('\"', ' ').replace('\*', ' ')

#Parsing text to identify weight and gender

    phys_text=text.split('+') # Remove first half of code
    phys_NoSpace=re.sub(' ','',phys_text[1]) #Removing extra spaces
    phys_split=re.split('(\d+)',phys_NoSpace,flags=re.IGNORECASE) # split out whenever letters and numbers are together
    phys_info=phys_split[3] # This set of numbers contains gender, height, and weight

#Finding the DL number

    split_text_check=text.split(';')
    check_text= split_text_check[1]
    check_num=int(check_text[0:4])

    DL_num=check_text[6:14] #Save DL number for identification

# Assigning weight obtained from DL

    weight_lb=int(phys_info[4:7])
    weight=weight_lb/2.2

# Assigning gender constant for BAC fomula

    if int(phys_info[0])==1 or 'F':
        gen_const= 0.58
    elif int(phys_info[0])==2 or 'M':
        gen_const= 0.49

# Assigning standard BAC constants 

    Body_H2O=0.806
    g_const=1.2
    t_const=0.015
      
## Calculating the BAC for the individual

    swipes=open("swipes.txt", 'r')

    beer_alc_ratio=(pour_vol/12)*(ABV/0.05)   

    BAC=0
    
    for line in swipes:
        if re.search(DL_num, line, re.IGNORECASE):
            unix_time=line.split(' ')[-1]

            time_diff_hrs=(time.time()-float(unix_time))/3600

        ## Formula for calculating BAC
            contributing_BAC=(Body_H2O*g_const*beer_alc_ratio)/(weight*gen_const)-t_const*time_diff_hrs

            if contributing_BAC >0:
                    BAC=BAC + contributing_BAC

# Return variables
    
    return BAC

