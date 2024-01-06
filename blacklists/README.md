# Custom blacklists on UDM Pro

The script in this package configures iptables on the UDM Pro to block all traffic from the IP addresses listed in the [Stratosphere Labs CTU-AIPP Blacklist](https://www.stratosphereips.org/attacker-ip-prioritization-blacklist).  The script is executed once a day using systemd.

This project contains the files that I used to build a Debian package that I host in my PPA repository that i9nstalls this script.   Please go to [this page](https://daveking.com/udm-hacks/blacklists.html) for more details on using that package.
