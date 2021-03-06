# Cameras Only Record When I'm Away

This script integrates Unifi Protect with my SmartThings service so that I only record camera events when I'm away from home or asleep.  SmartThings uses my cell phone as a sensor to determine whether or not I'm at home or away.  The ```away-recording``` script in this repository uses the UDM API to turn off event recording on some of my cameras during the day when SmartThings says I'm at home.  At night, or whenever I am away, recording is turned on.

## Installation

I wanted to run this script on the UDM itself so it is written for the version of Python available in the UDM's unifi-os container, Python 2.7.  It can be run elsewhere, but it may need to be modified if elsewhere uses a later version of Python.

Here is the process I went through to install the script on the UDM:

1.  I already have John D (boostchicken)'s [on-boot-script](https://github.com/boostchicken/udm-utilities/tree/master/on-boot-script) utility installed.  If you don't, I highly recommend it.  You'll need it, or something very much like it, down below.
2.  Modify the ```away-recording``` script to include your UDM login credentials, your SmartThings API token and the list of cameras you want to control.
3.  Install the ```away-recording``` script into the ```/mnt/data/unifi-os/dlk-udm-hacks/``` directory on your UDM.  Make sure that the file has execute permissions for the root id.  (If you install the script in a different subdirectory underneath /mnt/data/unifi-os, be sure to make the corresponding change in the ```20-away-recording.sh``` boot script that is mentioned below.)
4.  Access the unifi-os container's shell with the command: ```unifi-os shell```
5.  Install the Python requests module: ```apt install python-requests```<br />This install will persist through system reboots but will need to be repeated whenever Ubiquiti updates the network controller, i.e., installs a new version of the unifi-os container, on your UDM.
6.  Press Ctrl-D to exit the unifi-os container's shell and return to the base operating system's shell prompt.
7.  Install the ```20-away-recording.sh``` script from this repository in your /mnt/data/on-boot.d/ directory.  Make sure that the script has execute file permissions for the root id.  Every time your UDM boots, this script will create a crontab configuration file that will run the away-recording script every 10 minutes to check your status and that of your cameras.  If you want to change this frequency, you can edit this script to make that modification.  Run the script manually once after you modify it to put the changes you've made into effect.
8.  If you want to test the script, run the command that the ```20-away-recording.sh``` writes into the crontab file:<br />```podman exec -it unifi-os /data/dlk-udm-hacks/away-recording -q -l /data/dlk-udm-hacks/away-recording.log```<br />then check the contents of the /mnt/data/unifi-os/dlk-udm-hacks/away-recording.log file.
