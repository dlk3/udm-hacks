#!/bin/sh

MY_SSH_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA2YrKZDC2p65DHSwhah/FbhMEv6LcIOZAoeeygNMEwgfw3DtGYDgtwo8A0QhnhQLhcFRRpGGW66v2uAlJFibhJ2GRXsH6h/vW+ewkUq5sC+ngWGOFMHWZZD0Bol75ZEKzzygIQvyVN+o59Qxut40khy58WqOu5X6NGl2C7tEtp4RMFV72ap0W/uTvEi25MvaouhMnLz+2tbLH+ycNiswZI0qBZQx1oSDzVdfbiAv0AqceyY+2MLsrl8GAt17b4fq8FFwOJcV+S3P9EkjTqeXjrLGzYMB0rr/jokVhPJwnciLYD9QOovGBwqQfDNvuTL8G2VWJGWZHkuXJOIRdho7vRQ== dlk@fang.localdomain"
KEYS_FILE="/root/.ssh/authorized_keys"

# Places public key in ~/.ssh/authorized_keys if not present
if ! grep -Fxq "$MY_SSH_KEY" "$KEYS_FILE"; then
    echo "$MY_SSH_KEY" >> "$KEYS_FILE"
fi
