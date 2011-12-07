# ciscolib

A Python library for interacting with Cisco devices via command line. Only 
telnet is supported at this time.

There is a lack of documentation at the moment, but this library is fairly 
simple. If you dig through device.py, it should be fairly self-explanatory. 
Just keep in mind that functions prefixed with an underscore are not meant 
to be called directly.

See the LICENSE file for license information.

## Basic Usage

    import ciscolib
    switch = ciscolib.Device("hostname or ip", "login password", "optional login username")
    switch.connect()    # Defaults to port 23
    
    # There are some helper commands for common tasks
    print(switch.get_model())
    print(switch.get_ios_version())
    print(switch.get_neighbors())
    
    switch.enable("enable_password")
    
    # Or you can throw plain commands at the switch
    print(switch.cmd("show run"))
    switch.cmd("reload\n")
