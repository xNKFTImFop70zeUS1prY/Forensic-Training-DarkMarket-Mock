# DarkNet Market Mock - Moderator Communication Forum


## SSH Port Forwarding Container

A lightweight, security-hardened Docker container that provides SSH TCP forwarding capabilities to access internal infrastructure without shell access.

### Overview

This project creates a dedicated SSH jump host container that only allows TCP port forwarding. It's designed as a secure gateway to reach internal services without exposing them directly to the internet or granting shell access to users.

### Features

- **Minimal footprint**: Built on Alpine Linux with only essential SSH components
- **Security-focused**: Hardened configuration with unnecessary binaries removed
- **Single purpose**: Container permits only SSH port forwarding (no shell access)
- **Access control**: Configurable restrictions on permitted connections
- **Simple authentication**: Password-based login for the forwarding user


### How It Works

The container runs an OpenSSH server with a restricted configuration that:

1. Creates a dedicated user with no shell access
2. Allows only SSH TCP forwarding functionality (disables X11, tunneling, agent forwarding)
3. Prevents command execution on the container


### Connecting Through the Container

To create a local socks proxy port that is usable for tunneling requests, use:

    ssh -D [localport] -N [user]@[host]

If the host is an Onion service, the following config entry should be set in ~/.ssh/config (assuming local tor socks port is under 9050):

    Host *
      ProxyCommand connect -a none -S 127.0.0.1:9050 %h %p

Then a request with `curl -x socks5h://[localip]:[localport] [targetip]:[targetport]` can be done.


## Security Considerations

- **Password authentication**: The container uses simple password authentication. 
- **Restricted user**: The user account can only perform port forwarding operations
- **Limited binaries**: Container has minimal tools installed to reduce attack surface
- **No shell access**: Users cannot execute commands on the container
