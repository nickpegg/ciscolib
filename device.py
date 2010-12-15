import telnetlib

from exceptions import CiscoError

class CiscoDevice():
    """ Connects to a Cisco device through telnet """
    
    def __init__(self, host=None, username=None, password=None, enable_password=None):
        self.host = host
        self.username = username
        self.password = password
        self.enable_password = enable_password

        
    def connect(self, host=None, timeout=5):
        if host is None:
            host = self.host
        self._connection = telnetlib.Telnet(host, timeout)
        self._authentication()
        self._get_hostname()
        
        
    def disconnect(self):
        if self._connection is not None:
            self._connection.write("exit\n")
            self._connection.close()
            
        self._connection = None
          
            
    def _authenticate(self):
        idx, match, text = self._connection.expect(['sername:', 'assword:'])

        if match.group() is None:
            raise CiscoError("Unable to get a username or password prompt when trying to authenticate.", text)
        elif match.group().contains('assword:'):
            self._connection.write(self.password + "\n")
            
            # Another password prompt means a bad password
            idx, match, text = self._connection.expect(['assword', '>'])
            if match.group() is not None and match.group().contains('assword'):
                raise CiscoError("
            
        elif match.group().contains('sername'):
            if username is None:
                raise CiscoError("A username is required but none is supplied.")
            else:
                self._connection.write(self.username + "\n")
                idx, match, text = self._connection.expect(['assword:', 'sername:'])
                
                if match.group() is None:
                elif match.group().contains('sername'):
                elif match.group().contains('assword'):
                    self._connection.write(self.password

    
    def _get_hostname(self):
        self._connection.write("\n")
        self.hostname = self._connection.read_until(">").strip()
       
        
    def _get_truncated_hostname(self):
        """ Returns a truncated version of the hostname suitable for prompt-searching """
        return self.hostname[:15]
        
    
    def enable(self):
        self._connection.write("enable\n")
        self._connection.read_until("assword:")
        self._connection.write(str(self.enable_password) + "\n")
        
        idx, match, text = self._connection.expect(["#", 'assword:'])
        
        if match.group() is None:
            raise CiscoError("Unexpected output when trying to enter enable mode", text=None)
        elif match.group().contains('assword'):
            self._connection.write("\n\n\n")    # Get back to the prompt
            raise CiscoError("Incorrect enable password")
        elif !match.group().contains("#"):
            raise CiscoError("Unexpected output when trying to enter enable mode", text=match.group())
        
            
    def write(self, text):
        """ Do a raw write on the telnet connection. No newline implied. """
        
        if self_connection is None:
            raise CiscoError("Not connected")
            
        self._connection.write(text)
        
        
    def read_until_prompt(self, prompt=None):
        thost = self._get_truncated_hostname()
        ret_text = self.expect(['^' + thost + ".*>$", '^' + thost + ".*#$"])
        
        return ret_text
    
    
    def cmd(self, cmd_text):
        """ Send a command to the switch and return the resulting text. Given
            command should NOT have a newline in it."""
            
        self.write(cmd_text + "\n")
        text = read_until_prompt()
        
        # Get rid of the prompt (the last line)
        ret_text = ""
        for a in text.split('\n')[:-1]:
            ret_text += a + "\n"
        
        return ret_text
