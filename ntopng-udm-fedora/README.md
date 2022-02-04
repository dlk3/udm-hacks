# Building A ntopng Docker Container For The Unifi Dream Machine (UDM)

This repository contains the source material I use to build a container image that can be used to run the ntopng network traffic analysis tool on a Unifi Dream Machine router/switch.  

Please see the [Docker container registry](https://hub.docker.com/repository/docker/dlk3/ntopng-udm) for information on installing and using the ntopng-udm container.

This project was inspired by Carlos Talbot's  [tusc/ntopng-udm project](https://github.com/tusc/ntopng-udm).  This container differs in the following ways:

1. A Fedora container is used, because I like being on the semi-bleeding edge.
2. The unstable development version of ntopng from GitHub is used in this container.  This container is rebuilt weekly, on Monday night.
3. Network Discovery is enabled, i.e., the libcap library is compiled in.
4. An up-to-date version of the geoipupdate tool is used.
5. The start-up process for the container has been modified so that startup will not loop endlessly, blocking startup, when the GeoIP.conf file has errors.
6. An `ethtool` command was added to the startup process to turn off oversized packet handling per the ntopng log.
7. The run command in this documentation has been fixed so that the ntopng configuration data stored in the redis DB is actually persisted through UDM updates and restarts.
8. The run command in this documentation has been updated to include the `--privileged` option.  This gives the commands running inside the container the same access to system devices and files they would have if they were running natively on the UDM, under the root userid.  This fixes a couple of errors seen in the logs.

# Automated Build Process

I run the <code>build-ntopng-docker-image</code> script that's in this project weekly on my local workstation to automate the build of a new RPM with a new unstable release of ntopng from [GitHub](https://github.com/ntop/ntopng), followed by the build and push of a new version of the ARM64 container for the UDM.
