# Block IP Addressed In The Active ntopng Blacklists

The script in this package configures iptables on the UDM Pro to block all traffic from the IP addresses that are listed in the ntopng blacklists.  The script is executed through systemd once a day to refresh the UDM blacklist.  Only the active ntopng blacklists are used.  See the <code>Settings -> Blacklists</code> menu in ntopng to configure the active lists.

This project contains the files that I used to build a Debian package that I host in my PPA repository that i9nstalls this script.   Please go to [this page](https://daveking.com/udm-hacks/blacklists.html) for more details on using that package.
