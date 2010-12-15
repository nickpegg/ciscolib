import unittest

## Configuration 
# You must supply a valid switch and credentials for testing
host = ''
username = ''
password = ''
enable_password = ''

class TestCiscoDevice(unittest.TestCase):
    def setUp(self):
        self.device = CiscoDevice(host, username, password, enable_password)

if __name__ == '__main__':
    unittest.main()

