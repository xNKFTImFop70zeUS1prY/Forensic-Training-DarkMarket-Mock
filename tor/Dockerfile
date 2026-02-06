FROM alpine:3.21.3

# Install minimal dependencies
RUN apk update && \
    apk add --no-cache tor && \
    # Create non-root user
    adduser -D -u 1000 -h /etc/tor tor_user && \
    # Create hidden service directories
    mkdir -p -m 700 /etc/tor/hidden_services/{1,2,3} && \
    # Set ownership
    chown -R tor_user:tor_user /etc/tor

# Copy configuration and pre-generated keys
COPY torrc /etc/tor/torrc
COPY --chown=tor_user:tor_user 1/* /etc/tor/hidden_services/1/
COPY --chown=tor_user:tor_user 2/* /etc/tor/hidden_services/2/
COPY --chown=tor_user:tor_user 3/* /etc/tor/hidden_services/3/

RUN find /etc/tor/hidden_services -type d -exec chmod 700 {} \; && \
    find /etc/tor/hidden_services -type f -exec chmod 600 {} \;

USER tor_user
CMD ["tor", "-f", "/etc/tor/torrc"]
