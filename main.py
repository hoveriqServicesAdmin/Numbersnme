"""
NumbersNMe - Flask Backend
Serves static files and handles contact form submissions with SQLite database.
Sends acknowledgement email to sender and WhatsApp message with service details.
"""

import os
import sqlite3
import smtplib
import string
import random
import threading
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'numbersnme-secret-key-2026')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Add CORS headers for browser requests
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'NumbersNMe Admin API'})

@app.before_request
def handle_preflight():
    """Handle preflight requests"""
    if request.method == 'OPTIONS':
        return '', 204

DB_PATH = os.path.join(os.path.dirname(__file__), 'numbersnme.db')

BUSINESS_WHATSAPP = '918425985792'
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'Sangitha')
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'numbersnme2026'))

# ── Email Configuration ──
# Use App Password for Gmail (enable 2FA → generate App Password at https://myaccount.google.com/apppasswords)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'sangitha@numbersnme.com')
SMTP_PASS = os.environ.get('SMTP_PASS', '')  # Set via environment variable or replace here
SENDER_NAME = 'Numbers N Me Numerology'


def send_acknowledgement_email(to_email, name, service, dob, message):
    """Send an acknowledgement email to the sender in a background thread."""
    def _send():
        try:
            if not SMTP_PASS:
                print(f"[EMAIL] Skipped – SMTP_PASS not configured. Would have sent to {to_email}")
                return

            service_text = service if service else 'Not specified'
            dob_text = dob if dob else 'Not provided'

            # Build HTML email
            html = f"""
            <div style="font-family:'Poppins',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;">
                <div style="background:linear-gradient(135deg,#046bd2,#023e7d);padding:30px 20px;text-align:center;border-radius:8px 8px 0 0;">
                    <h1 style="color:#fff;margin:0;font-size:1.5em;">Numbers N Me Numerology</h1>
                    <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:0.95em;">Thank you for reaching out!</p>
                </div>
                <div style="padding:30px 25px;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 8px 8px;">
                    <p style="font-size:1em;color:#1e293b;">Dear <strong>{name}</strong>,</p>
                    <p style="color:#334155;line-height:1.7;">
                        We have received your inquiry and our numerology expert will get back to you within <strong>24 hours</strong>.
                    </p>

                    <div style="background:#f0f5fa;border-radius:8px;padding:20px;margin:20px 0;">
                        <h3 style="margin:0 0 12px;color:#046bd2;font-size:1em;">Your Inquiry Details</h3>
                        <table style="width:100%;border-collapse:collapse;">
                            <tr><td style="padding:6px 0;color:#64748b;width:40%;">Service Interested In</td><td style="padding:6px 0;color:#1e293b;font-weight:500;">{service_text}</td></tr>
                            <tr><td style="padding:6px 0;color:#64748b;">Date of Birth</td><td style="padding:6px 0;color:#1e293b;">{dob_text}</td></tr>
                            <tr><td style="padding:6px 0;color:#64748b;vertical-align:top;">Your Message</td><td style="padding:6px 0;color:#1e293b;">{message}</td></tr>
                        </table>
                    </div>

                    <p style="color:#334155;line-height:1.7;">
                        In the meantime, feel free to reach us on WhatsApp for a quicker response:
                    </p>
                    <div style="text-align:center;margin:20px 0;">
                        <a href="https://wa.me/{BUSINESS_WHATSAPP}" style="display:inline-block;background:#25D366;color:#fff;padding:12px 30px;border-radius:6px;text-decoration:none;font-weight:600;">💬 Chat on WhatsApp</a>
                    </div>

                    <hr style="border:none;border-top:1px solid #e5e7eb;margin:25px 0;">
                    <p style="color:#94a3b8;font-size:0.85em;text-align:center;">
                        Numbers N Me Numerology<br>
                        📞 +91 8425985792 &nbsp;|&nbsp; ✉️ sangitha@numbersnme.com<br>
                        📍 2303, Crosswinds Apartments, Bhandup West, Mumbai - 400078
                    </p>
                </div>
            </div>
            """

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Thank you for contacting Numbers N Me Numerology, {name}!'
            msg['From'] = f'{SENDER_NAME} <{SMTP_USER}>'
            msg['To'] = to_email
            msg['Reply-To'] = SMTP_USER

            # Plain text fallback
            plain = (
                f"Dear {name},\n\n"
                f"Thank you for reaching out to Numbers N Me Numerology!\n\n"
                f"We have received your inquiry and our numerology expert will get back to you within 24 hours.\n\n"
                f"Your Inquiry Details:\n"
                f"- Service Interested In: {service_text}\n"
                f"- Date of Birth: {dob_text}\n"
                f"- Your Message: {message}\n\n"
                f"In the meantime, feel free to reach us on WhatsApp: https://wa.me/{BUSINESS_WHATSAPP}\n\n"
                f"Warm regards,\n"
                f"Numbers N Me Numerology\n"
                f"+91 8425985792 | sangitha@numbersnme.com\n"
            )

            msg.attach(MIMEText(plain, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, to_email, msg.as_string())

            # Update email_sent flag in DB
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE numerology_contacts SET email_sent = 1
                WHERE email = ? ORDER BY id DESC LIMIT 1
            ''', (to_email,))
            conn.commit()
            conn.close()

            print(f"[EMAIL] Acknowledgement sent to {to_email}")

        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


def init_db():
    """Initialize the SQLite database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Legacy table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            dob TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # New table for numerology contacts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numerology_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            dob TEXT,
            message TEXT NOT NULL,
            whatsapp_sent INTEGER DEFAULT 0,
            email_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_ref TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT,
            appointment_date TEXT NOT NULL,
            time_slot TEXT DEFAULT '',
            status TEXT DEFAULT 'booked',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    appointment_columns = {row[1] for row in cursor.execute("PRAGMA table_info(appointments)").fetchall()}
    if 'time_slot' not in appointment_columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN time_slot TEXT DEFAULT ''")
    if 'first_name' not in appointment_columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN first_name TEXT DEFAULT ''")
    if 'middle_name' not in appointment_columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN middle_name TEXT DEFAULT ''")
    if 'last_name' not in appointment_columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN last_name TEXT DEFAULT ''")
    if 'dob' not in appointment_columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN dob TEXT DEFAULT ''")

    cursor.execute('''
        UPDATE appointments
        SET first_name = COALESCE(first_name, ''),
            middle_name = COALESCE(middle_name, ''),
            last_name = COALESCE(last_name, ''),
            dob = COALESCE(dob, '')
    ''')

    # Time slots are no longer used for booking; remove the old unique slot restriction.
    cursor.execute("DROP INDEX IF EXISTS idx_unique_slot")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments (appointment_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments (status)')
    conn.commit()
    conn.close()


def generate_booking_ref():
    """Generate an 8-character alphanumeric booking reference."""
    return 'NM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def generate_unique_booking_ref(cursor):
    """Generate a unique booking reference not already present in the DB."""
    while True:
        booking_ref = generate_booking_ref()
        row = cursor.execute('SELECT 1 FROM appointments WHERE booking_ref = ?', (booking_ref,)).fetchone()
        if not row:
            return booking_ref


def parse_booking_date(date_str):
    """Parse and validate a booking date string."""
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None, 'Invalid date format. Use YYYY-MM-DD.'

    if parsed_date < date.today():
        return None, 'Cannot book past dates.'

    if parsed_date.weekday() == 6:
        return None, 'Sundays are by appointment only. Please contact us directly via WhatsApp.'

    return parsed_date, None


def parse_dob(dob_str):
    """Parse and validate a DOB string."""
    try:
        parsed_dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        return None, 'Invalid DOB format. Use YYYY-MM-DD.'

    if parsed_dob > date.today():
        return None, 'DOB cannot be in the future.'

    return parsed_dob, None


def build_full_name(first_name='', middle_name='', last_name='', fallback_name=''):
    """Combine name parts into a single display name, with legacy fallback support."""
    name_parts = [part.strip() for part in (first_name, middle_name, last_name) if part and part.strip()]
    if name_parts:
        return ' '.join(name_parts)
    return (fallback_name or '').strip()


def is_admin_authenticated():
    """Return True when the current session belongs to the admin user."""
    return session.get('admin_username', '').casefold() == ADMIN_USERNAME.casefold()


init_db()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submissions, save to numerology_contacts, send email ack and return WhatsApp link."""
    try:
        data = request.get_json()

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        service = data.get('service', '').strip()
        dob = data.get('dob', '').strip()
        message = data.get('message', '').strip()

        # Validate required fields
        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Name, email, and message are required.'}), 400

        # Save to numerology_contacts table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO numerology_contacts (name, email, phone, service, dob, message, whatsapp_sent, email_sent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?)
        ''', (name, email, phone, service, dob, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        # Send acknowledgement email to the sender (non-blocking)
        send_acknowledgement_email(email, name, service, dob, message)

        # Build WhatsApp message
        wa_lines = [
            f"Hi NumbersNMe!",
            f"",
            f"Name: {name}",
            f"Email: {email}",
        ]
        if phone:
            wa_lines.append(f"Phone: {phone}")
        if dob:
            wa_lines.append(f"Date of Birth: {dob}")
        if service:
            wa_lines.append(f"Service Interested In: {service}")
        wa_lines.append(f"")
        wa_lines.append(f"Message: {message}")

        wa_text = urllib.parse.quote('\n'.join(wa_lines))
        whatsapp_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={wa_text}"

        return jsonify({
            'success': True,
            'message': f'Thank you {name}! Your inquiry has been received. A confirmation email has been sent to {email}. Redirecting you to WhatsApp...',
            'whatsapp_url': whatsapp_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Retrieve all contact submissions from numerology_contacts (admin endpoint)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM numerology_contacts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        contacts = [dict(row) for row in rows]
        return jsonify({'success': True, 'contacts': contacts})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ══════════════════════════════════════
#  Appointment Booking Endpoints

# User: Search bookings by reference, name, phone, or email
@app.route('/api/booking/search', methods=['GET'])
def search_bookings():
    """Allow users to search their bookings by reference, name, phone, or email (status=booked only)."""
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({'success': False, 'error': 'Search query required.'}), 400
    q_like = f"%{q}%"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Search by booking_ref (exact), or partial match on name, phone, or email
    cursor.execute('''
        SELECT booking_ref, first_name, middle_name, last_name, name, phone, email, dob, appointment_date, service
        FROM appointments
        WHERE status = 'booked' AND (
            booking_ref = ?
            OR lower(first_name) LIKE lower(?)
            OR lower(middle_name) LIKE lower(?)
            OR lower(last_name) LIKE lower(?)
            OR lower(name) LIKE lower(?)
            OR phone LIKE ?
            OR lower(email) LIKE lower(?)
        )
        ORDER BY appointment_date DESC
        LIMIT 10
    ''', (q.upper(), q_like, q_like, q_like, q_like, q_like, q_like))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append({
            'booking_ref': row['booking_ref'],
            'name': build_full_name(row['first_name'], row['middle_name'], row['last_name'], row['name']),
            'phone': row['phone'],
            'email': row['email'],
            'dob': row['dob'],
            'appointment_date': row['appointment_date'],
            'service': row['service']
        })
    return jsonify({'success': True, 'results': results})
# ══════════════════════════════════════

@app.route('/api/slots', methods=['GET'])
def get_slots():
    """Legacy endpoint retained for compatibility after removing time-slot booking."""
    return jsonify({
        'success': False,
        'error': 'Time-slot booking has been removed. Please choose your preferred appointment date only.'
    }), 410


@app.route('/api/book', methods=['POST'])
def book_appointment():
    """Book an appointment for a selected date."""
    try:
        data = request.get_json(silent=True) or {}
        first_name = data.get('first_name', '').strip()
        middle_name = data.get('middle_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        service = data.get('service', '').strip()
        dob = data.get('dob', '').strip()
        appt_date = data.get('date', '').strip()
        name = build_full_name(first_name, middle_name, last_name)

        if not first_name or not last_name or not phone or not email or not dob or not appt_date:
            return jsonify({'success': False, 'error': 'First name, last name, DOB, phone, email, and date are required.'}), 400

        _, date_error = parse_booking_date(appt_date)
        if date_error:
            return jsonify({'success': False, 'error': date_error}), 400

        _, dob_error = parse_dob(dob)
        if dob_error:
            return jsonify({'success': False, 'error': dob_error}), 400

        now = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            booking_ref = generate_unique_booking_ref(cursor)
            cursor.execute('''
                INSERT INTO appointments (
                    booking_ref, name, first_name, middle_name, last_name, phone, email, service, dob,
                    appointment_date, time_slot, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'booked', ?, ?)
            ''', (booking_ref, name, first_name, middle_name, last_name, phone, email, service, dob, appt_date, '', now, now))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'error': 'Unable to save the appointment right now. Please try again.'}), 409
        conn.close()

        # Build WhatsApp message to owner
        wa_lines = [
            "📅 New Appointment Booking!",
            "",
            f"Name: {name}",
            f"Phone: {phone}",
            f"Email: {email}",
        ]
        wa_lines.append(f"DOB: {dob}")
        if service:
            wa_lines.append(f"Service: {service}")
        wa_lines.extend([
            f"Date: {appt_date}",
            f"Booking Ref: {booking_ref}",
        ])
        wa_text = urllib.parse.quote('\n'.join(wa_lines))
        whatsapp_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={wa_text}"

        return jsonify({
            'success': True,
            'booking_ref': booking_ref,
            'name': name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'dob': dob,
            'appointment_date': appt_date,
            'message': f'Appointment booked for {appt_date}! Your reference: {booking_ref}. Please save this for rescheduling.',
            'whatsapp_url': whatsapp_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/booking/<booking_ref>', methods=['GET'])
def get_booking(booking_ref):
    """Look up an existing booking by reference code."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE booking_ref = ? AND status = 'booked'", (booking_ref.upper(),))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'success': False, 'error': 'No active booking found with this reference code.'}), 404

        return jsonify({
            'success': True,
            'booking': {
                'booking_ref': row['booking_ref'],
                'name': build_full_name(row['first_name'], row['middle_name'], row['last_name'], row['name']),
                'first_name': row['first_name'] if 'first_name' in row.keys() else '',
                'middle_name': row['middle_name'] if 'middle_name' in row.keys() else '',
                'last_name': row['last_name'] if 'last_name' in row.keys() else '',
                'phone': row['phone'],
                'email': row['email'],
                'service': row['service'],
                'dob': row['dob'] if 'dob' in row.keys() else '',
                'appointment_date': row['appointment_date'],
                'status': row['status']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reschedule/<booking_ref>', methods=['PUT'])
def reschedule_appointment(booking_ref):
    """Reschedule an existing booking to a new date."""
    try:
        data = request.get_json(silent=True) or {}
        new_date = data.get('new_date', '').strip()

        if not new_date:
            return jsonify({'success': False, 'error': 'A new appointment date is required.'}), 400

        _, date_error = parse_booking_date(new_date)
        if date_error:
            return jsonify({'success': False, 'error': date_error.replace('book', 'reschedule to')}), 400

        ref = booking_ref.upper()
        now = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check original booking exists
        cursor.execute("SELECT * FROM appointments WHERE booking_ref = ? AND status = 'booked'", (ref,))
        original = cursor.fetchone()
        if not original:
            conn.close()
            return jsonify({'success': False, 'error': 'No active booking found with this reference.'}), 404

        # Update booking
        cursor.execute('''
            UPDATE appointments SET appointment_date = ?, time_slot = '', updated_at = ?
            WHERE booking_ref = ? AND status = 'booked'
        ''', (new_date, now, ref))
        conn.commit()
        conn.close()

        # WhatsApp message for reschedule
        wa_lines = [
            "🔄 Appointment Rescheduled!",
            "",
            f"Name: {build_full_name(original['first_name'], original['middle_name'], original['last_name'], original['name'])}",
            f"Phone: {original['phone']}",
            f"Ref: {ref}",
            f"Old Date: {original['appointment_date']}",
            f"New Date: {new_date}",
        ]
        wa_text = urllib.parse.quote('\n'.join(wa_lines))
        whatsapp_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={wa_text}"

        return jsonify({
            'success': True,
            'message': f'Appointment rescheduled to {new_date}.',
            'whatsapp_url': whatsapp_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Authenticate the appointment admin user."""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if username.casefold() != ADMIN_USERNAME.casefold() or not check_password_hash(ADMIN_PASSWORD_HASH, password):
        return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401

    session['admin_username'] = ADMIN_USERNAME
    return jsonify({'success': True, 'username': ADMIN_USERNAME})


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Log out the appointment admin user."""
    session.pop('admin_username', None)
    return jsonify({'success': True})


# Admin: Update appointment time_slot
@app.route('/api/admin/appointment-time/<booking_ref>', methods=['PUT'])
def admin_update_time_slot(booking_ref):
    """Update the time_slot for an appointment (admin only)."""
    if not is_admin_authenticated():
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401
    try:
        data = request.get_json(silent=True) or {}
        new_time = data.get('time_slot', '').strip()
        if not new_time:
            return jsonify({'success': False, 'error': 'Time is required.'}), 400
        ref = booking_ref.upper()
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments SET time_slot = ?, updated_at = ?
            WHERE booking_ref = ?
        ''', (new_time, now, ref))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'No appointment found with this reference.'}), 404
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Time updated to {new_time}.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin: Update appointment status
@app.route('/api/admin/appointment-status/<booking_ref>', methods=['PUT'])
def admin_update_status(booking_ref):
    """Update the status for an appointment (admin only)."""
    if not is_admin_authenticated():
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401
    try:
        data = request.get_json(silent=True) or {}
        new_status = data.get('status', '').strip().lower()
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required.'}), 400
        ref = booking_ref.upper()
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments SET status = ?, updated_at = ?
            WHERE booking_ref = ?
        ''', (new_status, now, ref))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'No appointment found with this reference.'}), 404
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Status updated to {new_status}.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin: List all appointments (admin only)
@app.route('/api/admin/appointments', methods=['GET'])
def admin_list_appointments():
    if not is_admin_authenticated():
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments ORDER BY appointment_date DESC, created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        appointments = [dict(row) for row in rows]
        # Summary counts
        today = date.today().isoformat()
        total = len(appointments)
        upcoming = sum(1 for a in appointments if a['appointment_date'] >= today and a['status'] == 'booked')
        today_count = sum(1 for a in appointments if a['appointment_date'] == today and a['status'] == 'booked')
        completed_or_old = sum(1 for a in appointments if a['appointment_date'] < today or a['status'] != 'booked')
        summary = {
            'total': total,
            'upcoming': upcoming,
            'today': today_count,
            'completed_or_old': completed_or_old
        }
        return jsonify({'success': True, 'appointments': appointments, 'summary': summary, 'username': session.get('admin_username', 'Sangitha')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Database initialized. Starting server...")
    print(f"SMTP configured: {SMTP_HOST}:{SMTP_PORT} as {SMTP_USER}")
    if not SMTP_PASS:
        print("⚠️  SMTP_PASS not set. Set it via environment variable: set SMTP_PASS=your_app_password")
    print("✅ Visit http://localhost:5000")
    print("🌐 Or visit http://192.168.1.37:5000 from another device")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
