#! usr/bin/python


# Setting up the current date
import time
timestr = time.strftime("%Y%m%d%H%M%S")

cur_yr=int(timestr[0:4]) #Using 4 digit year
cur_yr_2=int(timestr[2:4]) #Using 2 digit year
cur_mo=int(timestr[4:6])
cur_dt=int(timestr[6:8])


# Defining a function to check license validity and user age 

def check_license(n): # Checks for age and validity of license

    raw_text=n
    text=raw_text.replace('\'', ' ').replace('\"', ' ').replace('\*', ' ')


# Check to make sure the swiped card is a drivers license and obtainign DL number

    split_text_check=text.split(';')
    check_text= split_text_check[1]
    check_num=int(check_text[0:4])

    DL_num=check_text[6:14] #Save DL number for identification


    if check_num==6360:
        valid_license='Yes'
    else:
        valid_license='No'
        print 'Try swiping a drivers license'


# Parsing license info to determine validity of license and age of user

    split_text_age=text.split('=')
    dates_text=split_text_age[1]

    # Separate out dates by year, month, and day
    
    exp_yr=int(dates_text[0:2])
    exp_mo=int(dates_text[2:4])

    br_yr=int(dates_text[4:8])
    br_mo=int(dates_text[8:10])
    br_dt=int(dates_text[10:12])


    
# check to see that license is still valid

    xpired= 'Sorry your license has expired'

    if valid_license=='Yes':

        if cur_yr_2>exp_yr:
            print expired
            valid_license='No'
        elif cur_yr_2==exp_yr:
            if cur_mo>exp_mo:
                    print expired
                    valid_license='No'

#Check to see if the user is over 21

    under_21= 'Under 21. No beer for you'

    if valid_license=='Yes':
        if cur_yr-br_yr<21:
            valid_license='No'
            print under_21
        elif cur_yr-br_yr==21:
            if cur_mo<br_mo:
                valid_license='No'
                print under_21
            elif cur_mo==br_mo:
                if cur_dt<br_dt:
                    valid_license='No'
                    print under_21
                elif cur_dt==br_dt:
                    print 'Happy 21st  Birthday!'

# Identifying the user's  name

    split_text_name=text.split('^')
    name_text= split_text_name[1]

    names=name_text.replace('$', ' ').split(' ') # some DLs use $ and spaces in names

    first_name=names[0]
    last_name=names[-1]

    class color:
        BOLD='\033[1m'
        END= '\033[0m'
        
    print color.BOLD + first_name, " ", last_name + color.END
        
    return (valid_license, first_name, last_name, DL_num)
