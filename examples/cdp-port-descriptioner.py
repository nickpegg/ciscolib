#!/usr/bin/env python

# Runs through a list of switches and if there is a neighbor on a given port,
# set the port's description to that neighbor's name

from getpass import getpass

import ciscolib


def main():
    # These variables can be assigned in-code, or will be asked at runtime
    USERNAME = ''
    PASSWORD = ''
    ENABLE_PWD = ''

    DESCRIPTION_PREFIX = ''
    DESCRIPTION_SUFFIX = ' Uplink'
    
    DOMAIN_NAME = ''        # Domain name of the switches. This will get dropped.
    
    
    # Get credentials if they aren't already supplied
    if USERNAME is None or USERNAME == '':
        USERNAME = raw_input("What is your switch username (blank for none)? ")
    if PASSWORD is None or PASSWORD == '':
        PASSWORD = getpass("What is your switch password? ")
    if ENABLE_PWD is None or ENABLE_PWD == '':
        ENABLE_PWD = getpass("What is your enable password? ")
  
    
    # Load the switch file and iterate through the switches
    for ip in open('switches.txt').readlines():
        ip = ip.strip() # Endline characters are for the birds
        
        if USERNAME != "":
            switch = ciscolib.Device(ip, PASSWORD, USERNAME, ENABLE_PWD)
        else:
            switch = ciscolib.Device(ip, PASSWORD, enable_password=ENABLE_PWD)
            
        try:
            switch.connect()
            print("Logged into %s" % ip)
        except ciscolib.AuthenticationError as e:
            print("Couldn't connect to %s: %s" % (ip, e.value))
            continue
        except Exception as e:
            print("Couldn't connect to %s: %s" % (ip, str(e)))
            continue
            
        
        print switch.get_neighbors()
        print switch.get_model()
        print switch.get_ios_version()
        print switch.get_interfaces()

         
        switch.cmd("exit")          # Get out of config mode
        switch.disconnect()
        print('')
        
    

if __name__ == "__main__":
    main()

