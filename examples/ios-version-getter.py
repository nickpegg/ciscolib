#!/usr/bin/env python

# Gets IOS versions of switches and dumps them into a CSV file

import ciscolib
import csv
import traceback

infile = csv.DictReader(open("switches.csv"))
outfile = csv.DictWriter(open("ios_versions.csv", 'w'), ["Hostname", "IP", "Model", "IOS Version"])

outfile.writeheader()


for row in infile:
    switch = {'IP': row['ip']}

    d = ciscolib.Device(row['ip'], row['password'], row['username'])
    try:
        d.connect()
    except:
        print("Could not connect to %s" % switch['IP'])
        continue
    
    print("Connected to %s (%s)" % (d.host, d.hostname))

    switch['Hostname'] = d.hostname   
    
    try: 
        switch['Model'] = d.get_model()
    except:
        traceback.print_exc()
    
    try:
        switch['IOS Version'] = d.get_ios_version()
    except:
        traceback.print_exc()
    
    outfile.writerow(switch)
    d.disconnect()
    print('')
