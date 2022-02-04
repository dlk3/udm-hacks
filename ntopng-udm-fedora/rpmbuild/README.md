These files provide the necessary support to build RPM packages for ntopng in the Fedora COPR repositories.  Packages may be built for both the x86_64 and aarch64 (arm64) architectures.

The copr-test script allows for local testing of the process using a podman container before setting up the actual COPR package.  The script contains the custom build method script that will be used within the COPR package definition.
