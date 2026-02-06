#!/bin/sh
# Generate host keys if missing
ssh-keygen -A

# Start SSH in foreground
exec /usr/sbin/sshd -D -e
