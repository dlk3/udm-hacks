# Cross-Compiling The Container For UDM

This section outlines the process I used to set up a Docker buildx environment on a Fedora 33 workstation that supports the creation of a arm64 container for the UDM on a amd64 host.

## Remove the Fedora Docker packages
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
