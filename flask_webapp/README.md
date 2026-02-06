# DarkNet Market Mock - Moderator Communication Forum

## Introduction

This project is a simulated darknet market forum focused on moderator communications. It creates a realistic-looking interface that mimics the aesthetic and functionality of darknet markets like those found on Tor Onion Services. The application is designed for educational or demonstration purposes to show how these platforms operate without actually implementing illegal functionality.

The mock includes user authentication, message submission to moderators, mirror links management, and a fake admin panel - all styled to match the distinctive green-on-black terminal-like interface common to darknet services.

## Technologies

- **Python 3.11**
- **Flask**: Web framework
- **Gunicorn**: WSGI HTTP Server
- **Nginx**: Reverse proxy (for handling Tor circuit IDs)
- **Pillow/PIL**: For CAPTCHA image generation
- **Flask extensions**:
    - Flask-Caching: For caching and rate limiting
    - Flask-WTF: For CSRF protection
- **Tor**: For Onion Service hosting (optional)

## Features \& Functionality

### User Authentication

- **Login Credentials**: Only selected usernames with their respective passwords are accepted
- **CAPTCHA Security**: Custom CAPTCHA implementation that dynamically generates images
- **Failed Login Handling**: After 8 failed attempts, user is blocked with a 404 error
- **Session Tracking**: Last login time is recorded and displayed

### Message Submission System

- Users can submit messages to "moderators"
- Message counter increases with each submission
- Messages are discarded (not actually stored)
- Flash messages provide confirmation of submission

### Mirror Links Management

The system displays mirror .onion links with different statuses:

- Primary mirror (green/online status)
- Secondary mirror (green/online status)
- Mirror under DDoS attack (orange/warning status)
- Mirror with law enforcement takedown (red/offline status)

Dynamic "last checked" timestamps update based on the current time.

### Admin Panel

- Fake admin authentication with username/password verification
- Brute force protection with account lockout after multiple failures
- Browser fingerprinting for visitor tracking
- Session-based lockout that resets after 3 minutes
- Allows to find out other active usernames

### Security Features

- CSRF protection on all forms
- CAPTCHA on login forms
- Browser fingerprinting
- Session management


## User Flow

1. **Initial Access**: User is presented with a login form requiring username/password and CAPTCHA
2. **Successful Login**: User enters the moderator communication forum
3. **Interface Navigation**: Tabbed interface with:
    - Message Moderators: Form to submit messages
    - Response Policy: Information about moderator responses
    - Mirror Links: Alternative .onion addresses
    - Admin Panel: Restricted access area (always fails authentication)
4. **Message Submission**: User can submit messages to "moderators"

## Project Structure

```
darknet-market-mock/
├── main.py                # Main Flask application
├── templates/             # HTML templates
│   ├── login.html         # Login page
│   ├── index.html         # Main forum interface
│   └── terminated.html    # Connection terminated page
├── static/                # Static assets (CSS, JS) for public assess
├── protected_assets/      # Protected ass[README.md](../nginx/README.md)es (CSS, JS) that require a logged-in session
├── requirements.txt       # Python dependencies
└── Dockerfile             # Dockerfile for statup
```


## Customization Options

### Changing Valid Login Credentials

To add or modify valid login credentials, edit `USER_ACCOUNT` in the login route in `app.py`:

### Adjusting the Hint

The relevant hint that every load there is probability that a `KNOWN_ADMINS` user pops out in the last logins. This gives the users a hint to try these as a ssh username alter. In the index route, this line must be changed:

    if random.random() < X

with X being a float between 0.0 and 1.0. This makes it more time-consuming and likely to spot the admin username.

### Webserver

This service runs via gunicorn listening on `0.0.0.0:8000`. It is very important to set the number of workers to only and only increase the threads for performance increases. Otherwise, the cache and sessions get inconsistent. This causes CSRF token errors for users.  

### Implementation Notes

- Packaged with requirements.txt for dependency management
