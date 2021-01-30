FROM fedora:latest

RUN dnf -y update
RUN dnf -y install autoconf automake ethtool expat-devel gcc-c++ git geoipupdate \
    iproute json-c-devel kernel-devel libcap-devel libcurl-devel libmaxminddb-devel \
    libpcap-devel libsqlite3x-devel libtool libxml2-devel make mariadb-devel net-tools \
    openssl openssl-devel pkg-config readline-devel redis rrdtool-devel wget zeromq-devel
run dnf -y clean all

RUN mkdir /root/src
RUN cd /root/src && GIT_SSL_NO_VERIFY=1 git clone https://github.com/ntop/nDPI.git && cd nDPI && ./autogen.sh && make -j4
RUN cd /root/src && GIT_SSL_NO_VERIFY=1 git clone https://github.com/ntop/ntopng && cd ntopng && ./autogen.sh && ./configure && \
    openssl req -new -x509 -sha1 -extensions v3_ca -nodes -days 3650 -out httpdocs/ssl/cert.pem -subj "/c=US/ST=All/O=Unifi UDM Users" && \
    cat privkey.pem httpdocs/ssl/cert.pem > httpdocs/ssl/ntopng-cert.pem && \
    make install -j4
RUN rm -fr /root/src

EXPOSE 3000/tcp
EXPOSE 3001/tcp

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh

LABEL maintainer="David King dave@daveking.com"
