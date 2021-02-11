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

There are two major steps in building this container:

1. Use the Fedora COPR facility to build and host a RPM package for ntopng running on an ARM64 system like the UDM.  The [copr](https://github.com/dlk3/udm-hacks/tree/master/ntopng-udm-fedora/copr) directory contains the source files needed to create a COPR package that will build the ntopng RPM.
2. Use the Docker buildx command to build a Fedora ARM64 container with the ntopng RPM installed in it.  The <code>Dockerfile</code> used to build the ntopng-udm Docker container and the <code>entrypoint.sh</code> file that it copies into the container are in the top level directory of this project.  The files in the [data/ntopng](https://github.com/dlk3/udm-hacks/tree/master/ntopng-udm-fedora/data/ntopng) directory are referenced during the installation of the container on the UDM.

I run the <code>build-ntopng-docker-image</code> script that's in this project weekly on my local workstation to automate the COPR build of a new RPM with a new unstable release of ntopng from [GitHub](https://github.com/ntop/ntopng), followed by the Docker build and push of a new version of the ARM64 container for the UDM.

# Additional Notes: Manually Building The Container For The UDM

This outlines the process I used to set up a Docker buildx environment on a Fedora 33 workstation that supports the creation of a arm64 container for the UDM on a amd64 host.

## Remove the Fedora distribution's Docker packages from the workstation
```
sudo dnf remove docker docker-client docker-client-latest docker-common \
  docker-latest docker-latest-logrotate docker-logrotate docker-selinux \
  docker-engine-selinux docker-engine
```
See https://docs.docker.com/engine/install/fedora/ for details

## Enable the Docker RPM repository
```
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/fedora/docker-ce.repo
```
See https://docs.docker.com/engine/install/fedora/ for details

## Install Docker from the Docker repository
```
sudo dnf install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo docker run hello-world
```
Add your userid to the "docker" group in /etc/groups and reboot in order to run docker commands without sudo.

See https://docs.docker.com/engine/install/fedora/ and https://docs.docker.com/engine/install/linux-postinstall/ for details

## Install the Docker buildx plugin

Download the latest binary release from https://github.com/docker/buildx/releases/latest and copy it to ~/.docker/cli-plugins folder with name docker-buildx.

Change the permission to execute:

`chmod a+x ~/.docker/cli-plugins/docker-buildx`

See https://github.com/docker/buildx/#installing for details.

## Install the multiplatform support

Start the docker/binfmt container running to add QEMU support to Docker.  This needs to be done after every system reboot or Docker service restart.

`docker run --rm --privileged docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64`

**Note:** Check to be sure that this is the latest release of the docker/binfmt container at https://hub.docker.com/r/docker/binfmt/tags?page=1&ordering=last_updated

## Create a new builder node
```
docker buildx create --name mybuilder
docker buildx use mybuilder
docker buildx inspect --bootstrap
```

## Build ntopng-udm for an arm64 host, i.e., the UDM

From within the folder which contains the Dockerfile and the other source files:

`docker buildx build --no-cache --platform linux/arm64 -t dlk3/ntopng-udm:latest -t dlk3/ntopng-udm:<VERSION_NUMBER> --load .`

**Note:** Change `--load` to `--push` to push the container directly to the Docker registry after the build completes, thereby skipping the step below.  In this case you must login to the registry before starting the build.

## Push ntopng-udm to the Docker registry by hand

Make sure that dlk3/ntopng-udm project exists in the registry.
```
docker login
docker push dlk3/ntopng-udm:latest
docker push dlk3/ntopng-udm:<VERSION_NUMBER>
docker logout
```
## Clean up after yourself

`docker buildx prune --all`
