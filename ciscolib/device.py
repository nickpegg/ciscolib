import telnetlib
import re
import time

from errors import *

class Device(object):
    """ Connects to a Cisco device through telnet """
    
    def __init__(self, host=None, password=None, username=None, enable_password=None):
        self.host = host
        self.username = username
        self.password = password
        self.enable_password = enable_password
        
        self.connected = False
        self._connection = None
        
        if self.username == '':
            self.username = None

        
    def connect(self, host=None, port=23, timeout=5):
        if host is None:
            host = self.host
            
        self._connection = telnetlib.Telnet(host, port, timeout)
        self._authenticate()
        self._get_hostname()
        
        self.cmd("term len 0")
        
        self.connected = True
        
        
    def disconnect(self):
        if self._connection is not None:
            self._connection.write("exit\n")
            self._connection.close()
            
        self._connection = None
        self.connected = False
          
            
    def _authenticate(self):
        idx, match, text = self._connection.expect(['sername:', 'assword:'], 5)

        if match is None:
            raise AuthenticationError("Unable to get a username or password prompt when trying to authenticate.", text)
        elif match.group().count('assword:'):
            self._connection.write(self.password + "\n")
            
            # Another password prompt means a bad password
            idx, match, text = self._connection.expect(['assword', '>', '#'], 5)
            if match.group() is not None and match.group().count('assword'):
                raise AuthenticationError("Incorrect login password")            
        elif match.group().count('sername') > 0:
            if self.username is None:
                raise AuthenticationError("A username is required but none is supplied.")
            else:
                self._connection.write(self.username + "\n")
                idx, match, text = self._connection.expect(['assword:'], 5)
                
                if match is None:
                    raise AuthenticationError("Unexpected text when trying to enter password", text)
                elif match.group().count('assword'):
                    self._connection.write(self.password + "\n")
                
                # Check for an valid login
                idx, match, text = self._connection.expect(['#', '>', "Login invalid", "Authentication failed"], 2)
                if match is None:
                    raise AuthenticationError("Unexpected text post-login", text)
                elif "invalid" in match.group() or "failed" in match.group():
                    raise AuthenticationError("Unable to login. Your username or password are incorrect.")
        else:
            raise AuthenticationError("Unable to get a login prompt")

    
    def _get_hostname(self):
        self._connection.write("\n")
        
        idx, match, text = self._connection.expect(['#', '>'], 2)
        
        if match is not None:
            self.hostname = text.replace('>', '').replace('#', '').strip()
       
        
    def _get_truncated_hostname(self):
        """ Returns a truncated version of the hostname suitable for prompt-searching """
        return self.hostname[:15]
        
    
    def enable(self, password=None):
        if password is not None:
            self.enable_password = password
            
        self.write("enable\n")
        
        idx, match, text = self._connection.expect(['#', 'assword:'], 1)
        if match is None:
            raise CiscoError("I tried to enable, but didn't get a command nor a password prompt")
        else:
            if '#' in text:
                return  # We're already enabled, dummy!
            elif 'assword' in text:
                self.write(str(self.enable_password) + "\n")
        
        idx, match, text = self._connection.expect(["#", 'assword:'], 1)
        
        if match.group() is None:
            raise CiscoError("Unexpected output when trying to enter enable mode", text=None)
        elif match.group().count('assword') > 0:
            self._connection.write("\n\n\n")    # Get back to the prompt
            raise CiscoError("Incorrect enable password")
        elif not match.group().count("#"):
            raise CiscoError("Unexpected output when trying to enter enable mode", text=match.group())
        
            
    def write(self, text):
        """ Do a raw write on the telnet connection. No newline implied. """
        
        if self._connection is None:
            self.connect()
            raise CiscoError("Not connected")
            
        self._connection.write(text)
        
        
    def read_until_prompt(self, prompt=None, timeout=5):
        thost = self._get_truncated_hostname()
        
        if prompt is None:
            expect_re = [thost + ".*>$", thost + ".*#$"]
        else:
            expect_re = [thost + ".*" + prompt + "$"]
            
        # TODO: Error instead of timing out
        idx, match, ret_text = self._connection.expect(expect_re, 5)
        
        return ret_text
    
    
    def cmd(self, cmd_text):
        """ Send a command to the switch and return the resulting text. Given
            command should NOT have a newline in it."""
            
        self.write(cmd_text + "\n")
        text = self.read_until_prompt()
        
        # Get rid of the prompt (the last line)
        ret_text = ""
        for a in text.split('\n')[:-1]:
            ret_text += a + "\n"
            
        # If someone changed the hostname, we need to update that
        if 'hostname' in cmd_text:
            self._get_hostname()
            
        if "Invalid input" in ret_text or "Incomplete command" in ret_text:
            raise InvalidCommand(cmd_text)
        
        return ret_text
        
   
    def get_neighbors(self):
        """ Returns a list of dicts of the switch's neighbors: 
            {hostname, ip, local_port, remote_port} """
        
        re_text = "-+\r?\nDevice ID: (.+)\\b\r?\n.+\s+\r?\n\s*IP address:\s+(\d+\.\d+\.\d+\.\d+)\s*\r?\n.*\r?\nInterface: (.+),.+Port ID.+:(.+)\\b\r?\n"
        
        neighbors = list()
        for neighbor in re.findall(re_text, self.cmd('show cdp neighbors detail')):
            n_dict = dict()
            
            n_dict['hostname'], n_dict['ip'], n_dict['local_port'], n_dict['remote_port'] = neighbor
            
            neighbors.append(n_dict)
        
        return neighbors
        
   
    def get_model(self):
        """ Gets the model number of the switch using the `get version` command """
        
        re_text = '(?:cisco (.+?) \(.+\) processor)|(?:Model number\s*:\s+(.+))'    
        
        cmd_output = self.cmd('show version')
        match = re.search(re_text, cmd_output)
        
        if match is not None:
            model = match.group(1)
        else:
            model = None
            raise ModelNotSupported(cmd_output)
            
        
        return model
        
    def get_ios_version(self):
        """ Gets the IOS software version """
        
        needle = "IOS.*Software.*Version ([\w\.\(\)]+)"
        haystack = self.cmd('show version')
        
        match = re.search(needle, haystack)
        
        if match is not None:
            version = match.group(1)
        else:
            version = None
            raise ModelNotSupported(cmd_output)
        
        return version
        
    
    def get_interface(self, interface):
        """ 
        Gets information on one interface and returns it as a dict.
        Input interface name must be in a form that Cisco likes
        
        Returned fields: name, description, status, vlan, duplex, speed, media
        """
        #TODO: Implement this
        pass
        
   
    def get_interfaces(self):
        detail_re = "((?:\w+|-|/!)+\d+(?:/\d+)*) is (?:up|down).+? \((.+)\) \r?\n(?:.+\r?\n)(?:\s+Description: (.+)\r?\n)?"
        
        status_re = "(\w{2}\d+(?:/\d+)+)\s+(.+?)\s+(\w+)\s+(\d+|trunk)\s+((?:\d|\w|-)+)\s+((?:\d|\w|-)+)\s+(.+)"
        
        ports = []
        
        port_matches = re.findall(detail_re, self.cmd('show interfaces'))
        if port_matches == []:
            raise ModelNotSupported(self.cmd('show interfaces'))

            
        for match in port_matches:
            port = dict()
            port['name'], port['status'], port['description'] = match
            
            # Not exactly the most efficient, but it guarantees that we get the right ports
            status_match = re.search(status_re, self.cmd('show interface ' + port['name'] + ' status'))
            if status_match is None:
                port['vlan'] = None
                port['duplex'] = None
                port['speed'] = None
                port['media'] = None
            else:
                port['vlan'], port['duplex'], port['speed'], port['media'] = status_match.groups()[3:]
            
            port['media'] = port['media'].strip()
            port['description'] = port['description'].strip()
                
            ports.append(port)
                
        return ports
            
            
            
        
