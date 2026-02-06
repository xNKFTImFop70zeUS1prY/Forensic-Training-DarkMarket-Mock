import base64
import io
import math

import nh3
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, \
    send_from_directory
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
import random
# KORREKTUR: timezone importiert für bewusste Zeitstempel
from datetime import datetime, timedelta, timezone
import hashlib
import time
import os

LOCAL_DEV = False
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Setup cache for our counter and other data
config = {"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 31536000}
app.config.from_mapping(config)
cache = Cache(app)
csrf = CSRFProtect(app)

# Initialize counter if it doesn't exist
if not cache.get("message_counter"):
    cache.set("message_counter", random.randint(24, 120))


USER_ACCOUNT = [['SnowTrader', 'NeverGonnaCatchMeVny2vSB9'],
                ['PhishingPhantom', 'PhishingForFun!vmoob2By'],
                ['ExploitEmporium', 'S3cureYourSnacks!bJrA5Ki3'],
                ['DarkWalletDaredevil', 'CryptoC0wboy$v3wZypVd'],
                ['WalletWhisperer', 'CryptoCupcake$CxUcn7qd'],
                ['RansomRogue', 'PayOrCryptit4fVTE6']
                ]
# Store known admin usernames
KNOWN_ADMINS = ['dreadpiraterobertsfree']
LOCKOUT_THRESHOLD = 5
LOCKOUT_TIME = timedelta(minutes=3)
BLACKLIST_DURATION_MINUTES = 10

# Track login attempts by username
if not cache.get("user_attempts"):
    cache.set("user_attempts", {})
if not cache.get("last_user_attempt"):
    # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
    cache.set("last_user_attempt", {"username": random.choice(USER_ACCOUNT)[0], "time": datetime.now(timezone.utc),
                                    'browser_fingerprint': 'Firefox/128.0 | 1400x900 | 24bit | UTC0 | en-US'})

# Initialize last_login_time in cache
if not cache.get("last_login_time"):
    cache.set("last_login_time", "17 Apr 2025, 13:03 UTC")

def generate_captcha_text(length=6):
    clear_letters = "ABCDEFGHJKLMNPQRTUVWXY"
    clear_digits = "34679"
    text = [random.choice(clear_letters), random.choice(clear_digits)]
    remaining_chars = length - 2
    all_chars = clear_letters + clear_digits
    for _ in range(remaining_chars):
        last_char = text[-1]
        available_chars = all_chars.replace(last_char, '')
        text.append(random.choice(available_chars))
    random.shuffle(text)
    return ''.join(text)


def generate_captcha_image(text, width=180, height=60):
    image = Image.new('RGB', (width, height), color=(20, 20, 20))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("courier", 60)
    except IOError:
        font = ImageFont.load_default()
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([x1, y1, x2, y2], fill=(0, random.randint(50, 120), 0), width=1)
    for _ in range(120):
        x_dot, y_dot = random.randint(0, width - 1), random.randint(0, height - 1)
        draw.point((x_dot, y_dot), fill=(0, random.randint(50, 180), 0))
    num_chars = len(text)
    zone_width = (width - 20) // num_chars
    v_center = height // 2
    def draw_rotated_char(char, x_zone_start, zone_width, y_center):
        char_size = int(zone_width * 1.5)
        char_img = Image.new('RGBA', (char_size, char_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        try:
            bbox = char_draw.textbbox((0, 0), char, font=font)
            c_width, c_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            c_width, c_height = char_draw.textsize(char, font=font)
        char_x, char_y = (char_size - c_width) // 2, (char_size - c_height) // 2
        char_draw.text((char_x, char_y), char, font=font, fill=(0, 255, 0))
        angle = random.uniform(-30, 30)
        rotated = char_img.rotate(angle, resample=Image.BICUBIC, expand=0)
        x_jitter = random.randint(-int(zone_width * 0.1), int(zone_width * 0.1))
        x_pos = x_zone_start + (zone_width - char_size) // 2 + x_jitter
        y_jitter = random.randint(-10, 10)
        y_pos = y_center - char_size // 2 + y_jitter
        x_pos = max(0, min(width - char_size, x_pos))
        y_pos = max(0, min(height - char_size, y_pos))
        image.paste(rotated, (x_pos, y_pos), rotated)
    for i, char in enumerate(text):
        x_zone_start = 10 + (i * zone_width)
        draw_rotated_char(char, x_zone_start, zone_width, v_center)
    for _ in range(3):
        y = random.randint(int(height * 0.2), int(height * 0.8))
        for x_pos in range(0, width, 2):
            amplitude = random.randint(3, 9)
            y_wave = y + amplitude * math.sin(x_pos * 0.08)
            draw.point((x_pos, int(y_wave)), fill=(0, random.randint(150, 255), 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

@app.before_request
def process_headers():
    if LOCAL_DEV: return
    if request.path.startswith('/static/'): return
    circuit_id = request.headers.get('X-Forwarded-For')
    parts = circuit_id.split("fc00:dead:beef:4dad")[1]
    if cache.get(f"blacklist_{parts}"): return abort(404)
    sess_circ_id = session.get('circ_id')
    if not sess_circ_id: session['circ_id'] = parts
    else:
        if parts != sess_circ_id:
            cache.set(f"blacklist_{parts}", True, timeout=BLACKLIST_DURATION_MINUTES * 60)
            return abort(404)
    if not request.headers.get('User-Agent') or 'Mozilla' not in request.headers.get('User-Agent'): return abort(404)

@app.route('/refresh-captcha', methods=['GET'])
@csrf.exempt
def refresh_captcha():
    captcha_text = generate_captcha_text()
    session['captcha_text'] = captcha_text
    return jsonify({'image': generate_captcha_image(captcha_text), 'success': True})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'login_attempts' not in session: session['login_attempts'] = 0
    if request.method == 'GET':
        captcha_text = generate_captcha_text()
        session['captcha_text'] = captcha_text
        return render_template('login.html', captcha_image=generate_captcha_image(captcha_text), last_login_time=cache.get("last_login_time") or '17 Apr 2025, 13:03 UTC')
    if request.method == 'POST':
        if session.get('login_attempts', 0) >= 8: return abort(404)
        session['login_attempts'] += 1
        if not LOCAL_DEV:
            circuit_id = request.headers.get('X-Forwarded-For')
            parts = circuit_id.split("fc00:dead:beef:4dad")[1]
            circ_attempts = cache.get(f"attempt_{parts}") or 0
            if circ_attempts >= 8:
                cache.set(f"blacklist_{parts}", True, timeout=BLACKLIST_DURATION_MINUTES * 60)
                return abort(404)
            cache.set(f"attempt_{parts}", circ_attempts + 1, timeout=BLACKLIST_DURATION_MINUTES * 60)
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        captcha_answer = (request.form.get('captcha-text') or '').strip().upper()
        if captcha_answer != session.get('captcha_text', ''):
            flash('Invalid CAPTCHA, please try again.')
            captcha_text = generate_captcha_text()
            session['captcha_text'] = captcha_text
            return render_template('login.html', captcha_image=generate_captcha_image(captcha_text))
        for user, passw in USER_ACCOUNT:
            if username == user and password == passw:
                session['logged_in'] = True
                session['username'] = username
                # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
                session['login_time'] = datetime.now(timezone.utc)
                current_time = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
                cache.set("last_login_time", current_time)
                return redirect(url_for('index'))
        flash('Invalid credentials!')
        captcha_text = generate_captcha_text()
        session['captcha_text'] = captcha_text
        return render_template('login.html', captcha_image=generate_captcha_image(captcha_text))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    message_count = cache.get("message_counter") or random.randint(24, 120)
    if 'users_active' not in session: session['users_active'] = random.randint(5, 490)
    users_online = max(session['users_active'] + random.randint(-5, 5), 3)
    # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
    now = datetime.now(timezone.utc)
    minutes = now.minute
    last_checked = [f"{(i * 1 + (minutes % 10)) % 60} minutes ago" for i in range(4)]
    last_user_attempt = cache.get("last_user_attempt") or {"username": "SnowTrader", "time": now, 'browser_fingerprint': '...'}
    login_time = session.get('login_time', now)
    if session.get('admin_hint_unlocked') or (now - login_time) > timedelta(minutes=10):
        admin_user = KNOWN_ADMINS[0]
        # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
        last_user_attempt = {"username": admin_user, "time": (datetime.now(timezone.utc) - timedelta(minutes=1, seconds=30)), 'browser_fingerprint': '...'}
    username = last_user_attempt['username']
    time_obj = last_user_attempt['time']
    fingerprint = last_user_attempt['browser_fingerprint']
    if isinstance(time_obj, str):
        try:
            time_obj = datetime.strptime(time_obj, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        except ValueError:
            time_obj = now
    time_diff = now - time_obj
    time_str = "just now" if time_diff.total_seconds() < 60 else f"{int(time_diff.total_seconds() / 60)} minutes ago"
    last_attempt = {"username": username, "time": time_str, 'browser_fingerprint': fingerprint}
    return render_template('index.html', message_count=message_count, users_online=users_online, last_checked=last_checked, last_attempt=last_attempt, username=session.get('username', 'Unknown'))

@app.route('/submit', methods=['POST'])
def submit_message():
    if not session.get('logged_in'): return redirect(url_for('login'))
    current_count = cache.get("message_counter") or random.randint(24, 120)
    cache.set("message_counter", current_count + 1)
    flash(f"Message successfully sent to moderators. Your complaint ID is: #{current_count + 1}")
    session['admin_hint_unlocked'] = True
    return redirect(url_for('index'))

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    input_username = request.form.get('admin_username', '')
    input_password = request.form.get('admin_password', '')
    fingerprint = nh3.clean(request.form.get('browser_fingerprint', 'Unknown Browser'), tags=set())
    if not all([input_username, input_password, fingerprint != 'Unknown Browser']):
        return jsonify({"status": "error", "message": "Security error: Missing required fields"})
    user_attempts = cache.get("user_attempts") or {}
    username = session.get('username', 'Unknown')
    # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
    now = datetime.now(timezone.utc)
    if username not in user_attempts:
        user_attempts[username] = {'count': 0, 'last_attempt': now, 'locked_until': None}
    record = user_attempts[username]
    if isinstance(record.get('last_attempt'), str): record['last_attempt'] = datetime.strptime(record['last_attempt'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    if isinstance(record.get('locked_until'), str): record['locked_until'] = datetime.strptime(record['locked_until'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    record['last_attempt'] = now
    if record.get('locked_until') and now < record['locked_until']:
        remaining_seconds = int((record['locked_until'] - now).total_seconds())
        return jsonify({"status": "error", "message": f"Account locked. Try again in {remaining_seconds} seconds.", "lockout": True, "lockout_seconds": remaining_seconds})
    if record.get('locked_until') and now >= record['locked_until']:
        record['count'] = 0
        record['locked_until'] = None
    time.sleep(random.uniform(0.5, 1.5))
    error_msg = f"Authentication failed: Wrong password for {input_username}" if input_username in KNOWN_ADMINS else f"Authentication failed: User {input_username} does not exist"
    record['count'] += 1
    if record['count'] >= LOCKOUT_THRESHOLD: record['locked_until'] = now + LOCKOUT_TIME
    # KORREKTUR: Standardisiere auf bewusste UTC-Zeitstempel
    cache.set("last_user_attempt", {"username": input_username, "time": datetime.now(timezone.utc), 'browser_fingerprint': fingerprint})
    user_attempts[username] = {k: (v.strftime('%Y-%m-%dT%H:%M:%S') if isinstance(v, datetime) else v) for k, v in record.items()}
    cache.set("user_attempts", user_attempts)
    if record.get('locked_until'):
        return jsonify({"status": "error", "message": f"Account locked. Try again in {LOCKOUT_TIME.seconds} seconds.", "lockout": True, "lockout_seconds": LOCKOUT_TIME.seconds})
    return jsonify({"status": "error", "message": error_msg})

@app.errorhandler(404)
def connection_terminated(error):
    return render_template('terminated.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    if os.path.splitext(filename)[1] not in {'.js', '.css'}: abort(403)
    if session.get('logged_in'):
        return send_from_directory('protected_assets', filename)
    return redirect(url_for('login'))

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; script-src 'self'; object-src 'none'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    app.run(debug=True)
