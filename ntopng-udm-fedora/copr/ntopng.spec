#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

%define  debug_package %{nil}

Name:		ntopng
#Version:	5.0
#Release:	0%{?dist}
Version:	5.1.%(date +%y%m%d)
Release:	1%{?dist}
Summary:	A next generation network packet traffic probe used for high-speed web-based traffic analysis and flow collection.

License:	GPLv3.0
URL:		https://ntop.org
Source0:	%{name}.tar.gz
Source1:	nDPI.tar.gz
Source2:	%{name}.conf
Source3:	%{name}.service
Source4:	%{name}.sysconfig
#Patch0:		ntopng-utils-manage-config.patch

Requires: geoipupdate, glib2, hiredis, libgcc, libpcap, libxml2, net-tools, openssl, redis, sqlite, zlib

BuildRequires:	autoconf, automake, expat-devel, gcc-c++, git, json-c-devel, kernel-devel, libcap-devel, libcurl-devel, libmaxminddb-devel, libpcap-devel, libsqlite3x-devel, libtool, libxml2-devel, make, mariadb-devel, openssl-devel, pkg-config, readline-devel, rrdtool-devel, zeromq-devel


%description
ntopng is a passive network monitoring tool focused on flows and statistics that 
can be obtained from the traffic captured by the server.


%prep
tar -zxvf %{SOURCE0}
tar -zxvf %{SOURCE1}


#%patch0


%build
cd nDPI
./autogen.sh
make -j
cd ../%{name}
./autogen.sh
./configure
make -j


%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 -t %{buildroot}%{_bindir} ntopng/ntopng
mkdir -p %{buildroot}/usr/man/man8
install -m 644 -t %{buildroot}/usr/man/man8 ntopng/ntopng.8
mkdir -p %{buildroot}/etc/ntopng
install -m 644 -t %{buildroot}/etc/ntopng %{SOURCE2}
mkdir -p %{buildroot}/usr/lib/systemd/system
install -m 644 -t %{buildroot}/usr/lib/systemd/system %{SOURCE3}
mkdir -p %{buildroot}/etc/sysconfig/
install -m 644 %{SOURCE4} %{buildroot}/etc/sysconfig/%{NAME}
mkdir -p %{buildroot}/usr/share/ntopng
cp -r ntopng/httpdocs %{buildroot}/usr/share/ntopng
cp -LR ntopng/scripts %{buildroot}/usr/share/ntopng
find %{buildroot}/usr/share/ntopng -name "*~"   | xargs /bin/rm -f
find %{buildroot}/usr/share/ntopng -name ".git" | xargs /bin/rm -rf


%files
/etc/ntopng/ntopng.conf
/etc/sysconfig/ntopng
/usr/bin/ntopng
/usr/lib/systemd/system/ntopng.service
/usr/man/man8/ntopng.8.gz
/usr/share/ntopng/*


%post
#  Create self-signed SSL certificate
cd /usr/share/ntopng/httpdocs/ssl
openssl req -new -x509 -sha1 -extensions v3_ca -nodes -days 3650 -out cert.pem -subj "/O=ntopng container" &>/dev/null
cat privkey.pem cert.pem > ntopng-cert.pem


%preun
#  Delete the files that the %post scriptlet created
cd /usr/share/ntopng/httpdocs/ssl
rm privkey.pem cert.pem ntopng-cert.pem


%changelog
* Tue Sep 28 2021 David King <dave@daveking.com>
	Update version number to 5.1.x
* Mon Mar 22 2021 David King <dave@daveking.com>
	Remove @BIN_DIR@ patch
* Mon Mar 07 2021 David King <dave@daveking.com>
	Add @BIN_DIR@ patch
* Sat Jan 30 2021 David King <dave@daveking.com>
	Initial Version
