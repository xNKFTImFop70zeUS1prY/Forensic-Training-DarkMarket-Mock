# DarkNet Market Mock - Moderator Communication Forum


## Tor Proxy

This spins up a container for the tor proxy that hosts overall three Onion Services. Since the addresses should be known in advance, the keys are copied from [1](1), [2](2) and [3](3) into the container.

## Routes 

The Tor container runs the Tor daemon and configures three Onion Services:

- **Onion Service 1**: Routes to the Flask application (port 80 → Nginx:7000) 
- **Onion Service 2**: Routes to the Flask application (port 80 → Nginx:7000)
- **Onion Service 3**:
  - Routes to the SSH server (port 22 → Nginx:2222)
  - Configured to cause timeout/waiting on connections (port 80 → Nginx:7001)
  
### Flask Route

The default route for Onion Service [1](1) and [2](2) attaches the CircuitID via the `HiddenServiceExportCircuitID haproxy` flat, meaning that the target must understand the proxy control. It represents the Tor CircuitID.

### Timeout and SSH Route

[3](3) leads on :80 to the nginx timeout config simulating the attacked address. On :22 requests are sent to the SSH container to show an unintentionally publicly exposed SSH service.


