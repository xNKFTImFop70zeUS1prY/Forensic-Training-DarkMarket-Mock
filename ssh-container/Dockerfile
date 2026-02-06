FROM alpine:3.21.3

# Install minimal SSH server
RUN apk add --no-cache openssh-server && \
    rm -rf /etc/ssh/ssh_host_* && \
    ssh-keygen -A

# Create proxy-only user with no shell
RUN adduser -D -s /sbin/nologin dreadpiraterobertsfree && \
    echo "dreadpiraterobertsfree:password123" | chpasswd

# Security hardening
RUN apk del openssl && \
    find /usr/bin/* -type f | grep -v -E 'ssh|sftp|scp' | xargs rm -f

COPY sshd_config /etc/ssh/sshd_config
COPY entrypoint.sh /entrypoint.sh

# Final setup
RUN chmod 755 /entrypoint.sh && \
    chmod 644 /etc/ssh/sshd_config && \
    chown root:root /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
