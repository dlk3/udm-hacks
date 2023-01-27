# Turn Off POE Power To Selected UDM Cameras Unless SmartThings Says Everyone is Away

For privacy reasons I want to keep my indoor cameras turned off unless the house is empty.  We have already set up SmartThings to use our mobile devices as sensors so that it knows when we are home or away.  I have defined a SmartThings rotine that switches the "Home" location to "Away" mode when we are gone.  This script queries the SmartThings location mode and turns on the cameras listed in its configuration file when we are away and turns them back off when we arrive back home.

This script can be run on the UDM itself, or on another computer in the local network.  

These files all need to be installed together in the same directory:

* **camera_poe_ctl** - the main script file.
* **camera_poe_ctl.conf** - the configuration file.  This file must be edited before use.  See the comments in the file for guidance.
* **udm.py** - a custom UDM API module that I created for this script.

I run this script on my UDM every 10 minutes using crond.  I do this by using John D's [on-boot-script](https://github.com/boostchicken/udm-utilities/tree/master/on-boot-script) utility to construct a custom cron.d file and then restart the cron.d service.  See the **50-camera-poe-ctl-cron.sh** file, the on-boot.d script that implements this.
