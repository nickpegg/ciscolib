# This is unfortunately mostly unused at the moment. I would like to set up 
# some sort of test framework which tests helper functions based on pre-fetched
# switch output

import unittest
import telnetlib

from device import Device
from errors import CiscoError

## Configuration 
# You must supply a valid switch and credentials for testing
host = ''
username = ''
password = ''
enable_password = ''

class TestCiscoDevice(unittest.TestCase):
    def setUp(self):
        self.device = CiscoDevice(host, username, password, enable_password)
        self.device._connection = telnetlib.Telnet(host, 5)
        
    def tearDown(self):
        self.device.disconnect()
    
    def test_disconnect(self):
        self.device.disconnect()
        self.assertIsNone(self.device._connection)
        
    def test_authenticate(self):
        # Set an incorrect password and check that it barfs
        self.device.password = self.device.password + "test"
        self.assertRaises(CiscoError, self.device._authenticate)
        self.device.password = self.device.password[:-3]
        
        try:
            self.tearDown()
            self.setUp()
        except:
            pass
            
class TestAuthenticatedCiscoDevice(TestCiscoDevice):
    def setUp(self):
        super(TestAuthenticatedCiscoDevice, self).setUp()
        self.device._authenticate()
        
    def test_enable(self):
        self.device.enable_password = self.device.enable_password + "test"
        self.assertRaises(CiscoError, self.device.enable)
        self.device.enable_password = self.device.enable_password[:-3]
        
    def test_read_until_prompt(self):
        ret = self.device.read_until_prompt()
        self.assertNotEqual(ret, '')
        
        

if __name__ == '__main__':
    unittest.main()

