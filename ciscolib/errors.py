class CiscoError(Exception):
    def __init__(self, value, text=''):
        self.value = value
        self.text = text
        
    def __str__(self):
        ret = self.value

        if self.text is not None and self.text != '':
            ret += "\nText returned from switch: " + str(self.text)

        return ret
        
class AuthenticationError(CiscoError):
    pass
    
class AuthorizationError(CiscoError):
    def __init__(self, cmd):
        self.cmd = cmd
        
    def __str__(self):
        return "Authorization error on command: " + str(self.cmd)
    
class InvalidCommand(CiscoError):
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        ret = "Invalid command: " + str(self.cmd)
        return ret

class ModelNotSupported(CiscoError):
    def __init__(self, reason):
        self.value = value
        self.reason = reason
    def __str__(self):
        ret = "This model of switch is not supported by this version of CiscoLib\n"
        ret += "Please contact the CiscoLib developer for help.\n\n"
        ret += "Reason: %s\n" % self.reason
        
        return ret
