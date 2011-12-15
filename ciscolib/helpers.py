import re

def shorten_int_name(interface_name):
    """ 
    Returns the Cisco shortened interface name from a full one.
    If the full interface name is invalid, this will return None
    """
    
    short = None
    regex = "(\w{2}).*?(\d+(?:/\d+)?(?:/\d+)?)"
    
    match = re.match(regex, interface_name)
    
    if match is not None:
        short = ""
        for group in match.groups():
            short += group
            
    return short

