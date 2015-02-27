#BioE 521 Final Project (BEERduino)
####Authors: Karl Gerhardt, Samantha Paulsen

##Overview

Our project uses a Raspberry Pi microcontroller system to regulate an at-home kegerator system. We designed the BEERduino with two main goals in mind: (1) to be able to identify kegerator users and record their requests to pour beer, and (2) to control who, specifically, is able to pour beer based on criteria decided by the kegerator owner(s). Moreover, we wanted a design that was fast and robust to errors, didn’t require generating special identification materials, and could be used to control kegerator access based on several criteria (not just pre-approved identity). 

To operate the system an administrator must define an approved user's lists (user_list.txt), he/she may also define a banned user list (blacklist.txt), and he/she must select the operating mode (Normal, Party, or Barkeep). The operating mode determines which specific criteria a user must meet in order to access beer. The user inputs his/her information by swiping a driver's license in a magnetic card reader. If the user is approved, the Raspberry Pi ouputs 3.3 volts via pin 3 to activate a solenoid valve and allow beer to flow. 

### BEERduino Operation

With a fully assembled device, one begins by executing the program BEERduino.py in the python shell. When the program executes, a prompt is given to select the desired operating mode (normal, party, or barkeep) followed by a prompt to input a password (“admin” by default). The system is now ready for user requests for beer and displays the prompt: “Swipe card now:”. Now, when an eligible user (eligibility being contingent on the user and the current operating mode) makes a request for beer by swiping their driver’s license, BEERduino verifies eligibility, records the user’s information and the current time, and finally signals the solenoid circuit to turn on for a period of time needed to pour approximately one pint of beer. Concurrently, the user is shown as standard ouput (printed on a monitor) along with their current predicted blood alcohol concentration (BAC) and the predicted BAC after consuming the freshly poured beer. 

### Operating Modes

The criteria by which beer eligibility is determined depends on the BEERduino “operating mode”. In every mode users must swipe a valid driver’s license and be over the age of 21. In “normal” mode (the standard mode for every day use), eligible users must also have a driver’s license listed in a local file “user_list.txt”. If the driver's license number provided by the magnetic card reader matches one in the approved user list,  the solenoid valve will open. “Party” mode has no additional restrictions, and is generally used when a few guests are present. “Barkeep” mode is is the most dynamic of the three modes, and is designed for large numbers of guests and regulating alcohol consumption. Here, users must meet the following criteria to have a request granted. They must swipe a valid driver’s license, be over 21 years of age, have a predicted blood alcohol content under an admin specified value, and must not have a driver’s license number listed in a file “blacklist.txt”. The decision to blacklist someone is at the discretion of the admin. After a swipe is approved, the user's first name, last name, driver’s license number, request time, as well as the current operating mode are all recorded in a file “swipes.txt”. Once the keg has been exhausted, the admin can tally the “swipes.txt” list and assign balances to user accounts based on how many swipes they made and what mode it was made in.       

### Card Reader

The magnetic stripe on a driver's license contains most of the information presented on the face of the card along with multiple field separation characters. Though the exact format varies by state, the general format and many key field separators are consistent. From the raw text we use regular expressions based on unique field separators to determine the user’s name, driver’s license number (DL #), license expiration date, birth date, and physical information (gender and weight). To parse the raw text from the magnetic stripe the program uses unique field separators present within the text. For example, to identify the DL # we split the text after the only semi-colon within the text and assigned the following digits to the expiration date and birth date, respectively.  However,formatting varies between states and only around half of all states have a magnetic stripe on their driver's license. For example, in the user’s physical information Texas IDs use a number (1 or 2) to specify gender as male or female, while a Minnesota license uses either an F or an M. In this project we accounted for some of these differences, but focused the majority of our work on Texas IDs. 

### Solenoid Valve

In the BEERduino system Beer flow is regulated by a solenoid valve. The valve has a gate separating the inlet and outlet port, and the position of the gate is controlled by powering the solenoid. Without power, the gate remains closed, and does not allow liquid to flow between the ports. When 12 volts of power is delivered to valve, the solenoid lifts the gate to allows beer to flow. The BEERduino solenoid valve is connected to a wall outlet through a TIP120 transistor that acts as a switch. This transistor’s logic pin is controlled by a GPIO pin on the Raspberry Pi. When 3.3 volds is delivered from the pi to the transistor, the transistor allows power to pass to the valve, which opens the gate and allows beer to flow normally.


### Calculating BAC

BAC depends on many things: alcohol tolerance, weight, rate of absorption (have you eaten?), and gender. A generally accepted formula that takes into account a person’s weight (in kilograms), gender, the number of drinks, and time passed since drinking is shown below.

Estimated BAC =[(%Body water)(# of Standard drinks)(Scaling Factor)]/[(Weight in Kg)(Gender constant)]  -(Metabolism Const.)(Hours passed)  

To compute the user’s estimated BAC we use the physical information (gender and weight) obtained from the drivers’ license along with historical information stored in the ‘swipes.txt’ file. Every time a user is poured a beer the user’s name, driver’s licence number, the current date, and the current time (in Unix time) are stored. Using the current user’s DL #, we search through the ‘swipes’ file and export the time stamp for every beer that user has received. We then calculate the ‘contributing BAC’ from every beer that user has logged, using the formula below. Since the formula is a simple linear decay (as the body metabolizes alcohol) the BAC will become negative after a few hours, negative values are ignored. We then sum all of the contributing BAC values above 0 to give the estimated BAC. The equation and relevant constants are listed below.


  		         Variable | Value/source
  		         -------- |------
		     % Body water | 0.86
	Number of standard drinks | 1 *scaled by ABV and beer volume
       		   Scaling factor | 1.2
			   Weight | From DL
		  Gender constant | Gender from DL (Male=0.58, Femal = 0.49)
	      Metabolism constant | 0.015
		     Hours passed | calculated from swipe log



