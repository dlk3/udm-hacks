FROM fedora:latest

RUN dnf -y update && \
	dnf -y install dnf-plugins-core ethtool geoipupdate iproute && \
	dnf -y copr enable dlk/rpms && \
	dnf -y install ntopng && \
	dnf -y clean all

EXPOSE 3000/tcp
EXPOSE 3001/tcp

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh

LABEL maintainer="David King <dave@daveking.com>"
