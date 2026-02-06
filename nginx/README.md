# DarkNet Market Mock - Moderator Communi cation Forum

## Nginx

nginx serves as a mediator between the Tor proxy and the flask application. The website configs are under `http.d` and the SSH forwarding is under `stream.d`. The config removes the server token identifying the nginx version. 

## Routes

The Nginx container serves as a reverse proxy and handles traffic differently based on the incoming .onion domain:

- **Onion Service 1**: Proxies to the Flask application 
- **Onion Service 2**: Proxies to the Flask application
- **Onion Service 3**:
    - Routes to the SSH server (port 22 → Nginx:2222)
    - Configured to cause timeout/waiting on connections (port 80 → Nginx:7001) by serving [timeout.html](html_timeout/timeout.html) with intentionally slow config [01_timeout.conf](http.d/01_timeout.conf)
- **ssh_net:80 default**: Serves static files from [blog_site](blog_site) to simulate a misconfigured personal blog.

### Flask Route

The default route gets the CircuitID from the Tor proxy and therefore proxy_pass must be enabled to passthorugh the CircID and adding the normal HTTP elements again.

### Timeout Route

The timeout route mocks the attacked part by using the following two variables for simulation slow loading:

    limit_rate 25;  # Bytes per second
    limit_rate_after 10;  # Allow header to load

This makes it painfully slow to load the entire document. Furthermore, a static html is served from the html_timeout path. While this shouldn't reveal sensitive information, the header gives an IP-address that people can later use:

    add_header X-Forwarded-For "172.22.0.2";
    add_header X-Load-Balancer "nginx-DarkMarket-03.internal";

The timeout route on :22 routes to ssh_container:2222 to forward the SSH connection.

### Exposed Personal Blog

The [02_personal_blog.conf](http.d/02_personal_blog.conf) config uses `listen 172.22.0.2:80;` to only listen to incoming requests from the SSH Docker Container to simulate an accidentally exposed default page. The website contains `autoindex on;' to flood users with information. The main information is the PGP key in the same directory that includes sensitive signatures leading to the operators.

