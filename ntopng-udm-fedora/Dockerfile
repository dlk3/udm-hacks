FROM docker.io/arm64v8/fedora:35

COPY ntopng-*.aarch64.rpm /tmp/
RUN dnf -y update && \
	dnf -y install dnf-plugins-core ethtool geoipupdate iproute && \
	dnf -y install /tmp/ntopng* && \
	dnf -y clean all && \
	rm /tmp/ntopng*

EXPOSE 3000/tcp
EXPOSE 3001/tcp

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh

LABEL maintainer="David King <dave@daveking.com>"
