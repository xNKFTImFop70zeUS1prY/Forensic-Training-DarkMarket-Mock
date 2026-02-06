# Darknet Market Mock - Moderator Communication Forum

## ⚠️ Disclaimer
**This environment contains intentionally vulnerable services and misconfigurations.** Do not deploy this in an unsecured network. It is designed solely for educational forensic training and security testing..


## Overview

This repository contains a comprehensive Docker Compose setup that simulates a darknet market environment for educational and security testing purposes. The system implements a multi-container architecture with network isolation, simulated vulnerabilities, and realistic darknet market aesthetics.

## System Architecture

The environment consists of four primary containers, each with specific roles:

```
                    ┌─────────────────┐
                    │                 │
Internet ───────────► Tor Onion       │
                    │ Services        │
                    │ (.onion domains)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │                 │
                    │ Nginx Proxy     │
                    │                 │
                    └─┬───────┬───────┘
                      │       │
          ┌───────────┘       └─────────┐
          ▼                             ▼
┌─────────────────┐             ┌─────────────────┐
│                 │             │                 │
│ Flask App       │             │ SSH Server      │
│ (Gunicorn)      │             │ (No internet)   │
│                 │             │                 │
└─────────────────┘             └─────────────────┘
```
This system creates a private network of Docker containers that expose services through Tor hidden services (.onion domains). The setup includes:

- **Tor container**: Manages three Onion Services with distinct purposes
- **Nginx container**: Acts as a proxy and routes traffic differently based on the .onion domain
- **Flask container**: Runs a leaked Darknet Market web application with Gunicorn
- **SSH container**: Provides a highly restricted SSH server with no internet access

### Network Topology

The containers are connected through three isolated Docker networks:

- **external_net (172.19.0.0/24)**: Only for Tor to allow internet access
- **tor_net (172.20.0.0/24)**: Connects Tor and Nginx, no internet access
- **flask_net (172.21.0.0/24)**: Connects Nginx and Flask application, no internet access
- **ssh_net (172.22.0.0/24)**: Connects Nginx and SSH container, no internet access


## Container Details

### 1. Tor Container

**Purpose**: Provides Onion routing and Onion Service functionality

**Key Features**:

- Hosts three Onion Services (.onion domains)
- Interfaces with the Nginx container
- Uses internal directory structure for Onion Service keys
- Proper ownership and permissions for Tor functionality

### 2. Nginx Container

**Purpose**: Serves as a reverse proxy and implements routing logic

**Key Features**:

- Route 1: Simulates timeout/high-load waiting page
- Route 2: Proxies requests to the Flask application
- Route 3: Forwards SSH connections
- Implements directory listing vulnerability (intentionally) for private blog
- Adds revealing HTTP headers for security testing in timeout route

### 3. Flask Application Container

**Purpose**: Hosts the main web application

**Key Features**:

- Served via Gunicorn with specified worker configuration
- Contains HTML templates and Python backend
- Secured container with minimal permissions
- Accessed through Nginx reverse proxy


### 4. SSH Container

**Purpose**: Provides restricted SSH access with port forwarding capabilities

**Key Features**:

- Uses restricted shell and chroot jail
- Allows only port forwarding (no command execution)
- User account: user with password authentication
- Strictly controlled access to TCP forwarding
- Can be used to access Nginx endpoints via tunneling


## Security Features

### Network Isolation

- Each service is isolated in its own network segment
- Only Tor container has internet access
- Services can only communicate through designated paths


### Container Hardening

- Read-only filesystems where possible
- Dropped capabilities
- Non-privileged users
- No unnecessary software
- Limited exposed ports


### SSH Restrictions

- Allows port forwarding only
- No shell access
- Limited to internal container networks


## Implementation Notes

- Container IP addresses are statically assigned for predictability

## Setup


### Prerequisites

The following software must be installed

- **Docker Engine (version 20.10 or newer)**
- **Docker Compose (version 2.0 or newer)**

### Deployment

The environment is fully managed via docker compose. Therefore, clone project and navigate to the directory. Then generate the docker images with:
```bash
   docker compose build
```
and start everything in the detached mode:
```bash
   docker compose up -d
```

After the startup, the services might require a few minutes to establish connectivity with the Tor network and set up the Onion Services.

### Onion Services 

The environment exposes three distinct Onion Services, each corresponding to a specific training scenario.

- **Onion Service 1 (HTTP):** Routes to the Flask application (port 80 → Nginx:7000).
  - onion address: [ONION_SERVICE_1_ADDRESS].onion

- **Onion Service 2 (HTTP):** Routes to the Flask application (port 80 → Nginx:7000)
  - onion address: [ONION_SERVICE_2_ADDRESS].onion

- **Onion Service 3 (SSH & HTTP):** 
  - Access point for lateral movement (SSH)
  - Configured to cause timeout/waiting on connections (port 80 → Nginx:7001)
  - onion address: [ONION_SERVICE_3_ADDRESS].onion

## Configuration

The environment allows for several easy modifications in the `flask_webapp/main.py` program:

- Usernames can be changed in the `USER_ACCOUNT` variable together with the administrator username in `KNOWN_ADMINS`.
- The threshold for allowed login attempts in the admin portal before blocking the Tor circuit can be adjusted with the `LOCKOUT_THRESHOLD` variable.
- The lockout time for the block can be adjusted in `LOCKOUT_TIME`.
- If the Tor circuit is blocked (either by too many login attempts or switching the circuit for same login session), the lockout time can be adjusted with `BLACKLIST_DURATION_MINUTES`.


---

## 🛠️ Instructor Setup Guide

**Follow these phases sequentially to prepare the training environment.**

### Prerequisites
* Docker Engine (v20.10+)
* Docker Compose (v2.0+)
* `tor` installed locally (optional, but recommended for key generation)

### Phase 1: Forensic Artifacts Setup (Critical)
The repository includes a `handout-and-keys` directory containing the forensic evidence chain. This key links the persona "Phoenix" to the known actor "Joe Doe" via a cryptographic signature. The public key (`handout-and-keys\joe_doe_public.asc`) of Joe Doe must be made available to participants to allow them linking the DarkMarket admin to Joe Doe.

A starting mail is given as inspiration how to introduce the scenario to the participants.


### Phase 2: Generate Onion Service Keys
You must pre-generate v3 Onion Service keys so the addresses are known before the container starts.

**Perform this procedure for EACH service folder (`tor/1/`, `tor/2/`, and `tor/3/`):**

1.  Create a temporary directory:
    ```bash
    mkdir -p /tmp/tor-gen/data && chmod 700 /tmp/tor-gen/data
    ```
2.  Create a temporary config:
    ```bash
    echo "HiddenServiceDir /tmp/tor-gen/data" > /tmp/tor-gen/torrc
    echo "HiddenServicePort 80 127.0.0.1:80" >> /tmp/tor-gen/torrc
    ```
3.  Run Tor briefly (approx. 10-15s) until bootstrapped (100%), then stop it (`Ctrl+C`):
    ```bash
    tor -f /tmp/tor-gen/torrc
    ```
4.  **Copy the keys to the project:**
    ```bash
    # Example for Service 1 (Repeat for folders 2 and 3!)
    cp /tmp/tor-gen/data/hostname ./tor/1/
    cp /tmp/tor-gen/data/hs_ed25519_public_key ./tor/1/
    cp /tmp/tor-gen/data/hs_ed25519_secret_key ./tor/1/
    ```
5.  Clean up: `rm -rf /tmp/tor-gen/data/*`


### Phase 3: Finalize Configuration
Now that you have the keys, you must update the configuration files and the student handout.

1.  **Get your Onion Addresses:**
    ```bash
    cat tor/1/hostname  # [ONION_SERVICE_1] (Market Entry)
    cat tor/2/hostname  # [ONION_SERVICE_2] (Mirror)
    cat tor/3/hostname  # [ONION_SERVICE_3] (SSH/Timeout)
    ```

2.  **Update Nginx Configs:**
    Open `nginx/00_flapp.conf` and `nginx/01_timeout.conf`. Replace the placeholders `[ONION_SERVICE_X_ADDRESS]` with your actual generated addresses.

3.  **Update Flask Templates:**
    Open `flask_webapp/templates/index.html` (Mirror Links section). Replace the placeholders so the mirror links on the site point to your actual services.

4.  **Update Student Briefing (Crucial):**
    Open `handout-and-keys/Start_Mail.txt`.
    * Replace the `[INSERT_ONION_ADDRESS_HERE]` placeholder with the address of **Service 1**.
    * Save the file.

### Phase 4: Build and Deploy
```bash
docker compose build
docker compose up -d
```

### Note regarding PGP Signature Validity:

By replacing the `[ONION_SERVICE_...]` placeholders in `flask_webapp/templates/index.html` with your actual generated addresses, the PGP signature block displayed on the main page (Mirror List) will become mathematically invalid.

**For the Scenario:** This mismatch is **irrelevant** for the forensic solution path. The critical evidence is the *Phoenix* key found later on the internal blog, which remains valid.
**Optional (High Authenticity):** If you want a perfectly consistent environment, you can re-sign the mirror list text using the provided admin key:

1. Import the key: `gpg --import handout-and-keys/DarkMarket_private.asc`
2. Create the new text body with your onion addresses.
3. Sign it: `gpg --clearsign --local-user "DarkMarket Admin"`
4. Replace the PGP block in `flask_webapp/templates/index.html` with your new output.

## Student Handout Preparation

To start the scenario, the participants need specific files to begin their investigation. Create a zip archive or folder for the trainees containing **only** the following two files:

1.  **Briefing Email:** The updated `handout-and-keys/Start_Mail.txt`.
    * *Recommendation:* Save this as a `.eml` file or PDF to make it look like a real evidence export. Also adapt this to the local language and participants background.
2.  **Intelligence Key:** `handout-and-keys/joe_doe_public.asc`.
    * *Context:* This key represents intelligence found on a suspect's device in a prior case, which is necessary to verify the final attribution.

** WARNING:** Do NOT give students the private keys (`*_private.asc`) or the `Phoenix_public.asc` directly. They must discover the public key on the internal blog server during their investigation to prove they successfully pivoted through the network.



---

## Solution

Identifying the administrator requires several steps:

1. The last login changes to a KNOWN_ADMINS user after a message is sent in the interface or the user stays 10 minutes on the website.
2. The identified username in last login (KNOWN_ADMINS) is a SSH user in one Onion Service referenced in the mirror page.
3. This enables brute force attacks on the simple password that then gives access for the TCP forwarding.
4. The TCP forwarding can be used to systematically scan for open ports in the internal network.
5. A blog site runs on the local network in the nginx container.
6. An embedded PGP key in the blog implicates the market administrator in the signature metadata
