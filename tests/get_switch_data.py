#!/usr/bin/env python

# get_switch_data.py
#
# Gets fixture data out of a set of switches (located in switches.txt)

import threading
import time
import datetime
import re
import os


import ciscolib


PASSWORD = ''

USERNAME = ''
USER_PASSWORD = ''  # Password to use if we need to use a username

models = []
models_lock = threading.Lock()
        

class Grabber(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        
        self.host = host
        
        
    def run(self):
        # Connect up
        try:
            device = ciscolib.Device(self.host, PASSWORD)
            device.connect()
        except ciscolib.AuthenticationError:
            try:
                device = ciscolib.Device(self.host, USER_PASSWORD, USERNAME)
                device.connect()
            except:
                print("Unable to connect to %s" % self.host)
                return
        except:
            print("Unable to connect to %s" % self.host)
            return
            
        try:
            model = device.get_model()
        except ciscolib.ModelNotSupported:
            print("!! Model of %s is not supported!" % self.host)
            return
            
        if model in models:
            return  # We already have a data for this switch model
        else:           
            with models_lock:
                models.append(model)
        
        output_dir = 'fixtures/%s/' % model
        try: 
            os.mkdir(output_dir)
        except OSError as e:
            if e.errno != 17:
                print("!! Unable to create model directory %s" % output_dir)
                return
            
        open(output_dir + "show_int_status.txt", 'w').write(device.cmd("show int status"))
        open(output_dir + "show_cdp_neighbors_detail.txt", 'w').write(device.cmd("show cdp neighbors detail"))
        open(output_dir + "show_version.txt", 'w').write(device.cmd("show version"))
        open(output_dir + "show_arp.txt", 'w').write(device.cmd("show arp"))
        
    
        mac_data = ''
        mac_cmd = ''
        try:
            mac_cmd = 'show mac-address-table'
            mac_data = device.cmd(mac_cmd)
        except ciscolib.InvalidCommand:
            try:
                mac_cmd = 'show mac address-table'
                mac_data = device.cmd(mac_cmd)
            except:
                print("!! Unable to get mac data for %s" % self.host)
            
        if mac_data != '':
            open(output_dir + mac_cmd.replace(' ', '_') + ".txt", 'w').write(mac_data)
        
    
        interfaces_re = "((?:\w+|-|/!)+\d+(?:/\d+)*) is (?:up|down)"
        interfaces = device.cmd("show interfaces")
        open(output_dir + "show_interfaces.txt", 'w').write(interfaces)
        
        for result in re.findall(interfaces_re, interfaces):
            filename = "show_interface_%s_status.txt" % result
            filename = filename.replace("/", "+")
            open(output_dir + filename, 'w').write(device.cmd("show interface %s status" % result))
            


grabber_pool = []

for ip in open('fixtures/switches.txt'):
    print("Connecting to %s" % ip)
    t = Grabber(ip)    
    t.start()
    grabber_pool.append(t)
    
    while len(grabber_pool) >= 20:
        [grabber_pool.remove(thread) for thread in grabber_pool if not thread.is_alive()]
        time.sleep(0.01)

# Wait for the threads to die out
while len(grabber_pool) > 0:
    [grabber_pool.remove(thread) for thread in grabber_pool if not thread.is_alive()]
    time.sleep(0.01)
    
print("Models found: %s" % str(models))

