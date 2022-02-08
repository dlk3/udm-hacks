# Turn On/Off PoE Power For Cameras

This script will enable or disable PoE power on ports on a Unifi switch that have Unifi cameras plugged into them.  

1.  The script queries the Protect application on the Unifi UDM to get the MAC address of the camera named on the command line.
2.  The script then queries the Network application on the Unifi UDM to find the switch port that is connected to a client with that MAC address.
3.  Finally the script turns PoE power on that port either on or off as was specified on the command line.  If no specific action was specified on the command line then the script toggles the PoE setting, turning power off it is currently on, and on if it is currently off.
4.  In my environment It takes about five seconds for the switch to receive and process the port configuration change.  The switch resets when the change is processed and all of the client devices on that switch can lose their current network connections when that happens.
