class CiscoError(Exception):
    def __init__(self, value, text=''):
        self.value = value
        self.text = text
        
    def __str__(self):
        ret = self.value

        if self.text is None or self.text != '':
            ret += "\nText returned from switch: " + str(self.text)

        return repr(ret)
