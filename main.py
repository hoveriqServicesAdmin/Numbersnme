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
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

DB_PATH = os.path.join(os.path.dirname(__file__), 'numbersnme.db')

BUSINESS_WHATSAPP = '918425985792'

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
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'booked',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Unique index to prevent double-booking
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_slot
        ON appointments (appointment_date, time_slot)
        WHERE status = 'booked'
    ''')
    conn.commit()
    conn.close()


# ── Appointment Slot Configuration ──
SLOTS_MON_FRI = [
    '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM',
    '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM', '06:00 PM'
]
SLOTS_SATURDAY = [
    '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM',
    '02:00 PM', '03:00 PM', '04:00 PM'
]


def generate_booking_ref():
    """Generate an 8-character alphanumeric booking reference."""
    return 'NM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


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
# ══════════════════════════════════════

@app.route('/api/slots', methods=['GET'])
def get_slots():
    """Return available and booked slots for a given date."""
    try:
        date_str = request.args.get('date', '')
        if not date_str:
            return jsonify({'success': False, 'error': 'Date parameter is required.'}), 400

        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        if d < date.today():
            return jsonify({'success': False, 'error': 'Cannot view slots for past dates.'}), 400

        day_of_week = d.weekday()  # 0=Mon, 6=Sun

        if day_of_week == 6:  # Sunday
            return jsonify({'success': True, 'sunday': True, 'slots': [], 'message': 'Sundays are by appointment only. Please contact us directly via WhatsApp.'})

        all_slots = SLOTS_MON_FRI if day_of_week < 5 else SLOTS_SATURDAY

        # Get booked slots for this date
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT time_slot FROM appointments WHERE appointment_date = ? AND status = 'booked'", (date_str,))
        booked = {row[0] for row in cursor.fetchall()}
        conn.close()

        slots = []
        for s in all_slots:
            slots.append({'time': s, 'booked': s in booked})

        return jsonify({'success': True, 'sunday': False, 'slots': slots, 'date': date_str})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/book', methods=['POST'])
def book_appointment():
    """Book an appointment slot."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        service = data.get('service', '').strip()
        appt_date = data.get('date', '').strip()
        time_slot = data.get('time_slot', '').strip()

        if not name or not phone or not email or not appt_date or not time_slot:
            return jsonify({'success': False, 'error': 'Name, phone, email, date, and time slot are required.'}), 400

        # Validate date
        try:
            d = datetime.strptime(appt_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format.'}), 400

        if d < date.today():
            return jsonify({'success': False, 'error': 'Cannot book past dates.'}), 400

        booking_ref = generate_booking_ref()
        now = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO appointments (booking_ref, name, phone, email, service, appointment_date, time_slot, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'booked', ?, ?)
            ''', (booking_ref, name, phone, email, service, appt_date, time_slot, now, now))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'error': 'This slot has just been booked by someone else. Please choose another slot.'}), 409
        conn.close()

        # Build WhatsApp message to owner
        wa_lines = [
            "📅 New Appointment Booking!",
            "",
            f"Name: {name}",
            f"Phone: {phone}",
            f"Email: {email}",
        ]
        if service:
            wa_lines.append(f"Service: {service}")
        wa_lines.extend([
            f"Date: {appt_date}",
            f"Time: {time_slot}",
            f"Booking Ref: {booking_ref}",
        ])
        wa_text = urllib.parse.quote('\n'.join(wa_lines))
        whatsapp_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={wa_text}"

        return jsonify({
            'success': True,
            'booking_ref': booking_ref,
            'message': f'Appointment booked! Your reference: {booking_ref}. Please save this for rescheduling.',
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
                'name': row['name'],
                'phone': row['phone'],
                'email': row['email'],
                'service': row['service'],
                'appointment_date': row['appointment_date'],
                'time_slot': row['time_slot'],
                'status': row['status']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reschedule/<booking_ref>', methods=['PUT'])
def reschedule_appointment(booking_ref):
    """Reschedule an existing booking to a new date/time."""
    try:
        data = request.get_json()
        new_date = data.get('new_date', '').strip()
        new_time = data.get('new_time_slot', '').strip()

        if not new_date or not new_time:
            return jsonify({'success': False, 'error': 'New date and time slot are required.'}), 400

        try:
            d = datetime.strptime(new_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format.'}), 400

        if d < date.today():
            return jsonify({'success': False, 'error': 'Cannot reschedule to a past date.'}), 400

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

        # Check new slot is free
        cursor.execute("SELECT id FROM appointments WHERE appointment_date = ? AND time_slot = ? AND status = 'booked' AND booking_ref != ?",
                        (new_date, new_time, ref))
        conflict = cursor.fetchone()
        if conflict:
            conn.close()
            return jsonify({'success': False, 'error': 'The new slot is already booked. Please choose another.'}), 409

        # Update booking
        cursor.execute('''
            UPDATE appointments SET appointment_date = ?, time_slot = ?, updated_at = ?
            WHERE booking_ref = ? AND status = 'booked'
        ''', (new_date, new_time, now, ref))
        conn.commit()
        conn.close()

        # WhatsApp message for reschedule
        wa_lines = [
            "🔄 Appointment Rescheduled!",
            "",
            f"Name: {original['name']}",
            f"Phone: {original['phone']}",
            f"Ref: {ref}",
            f"Old: {original['appointment_date']} at {original['time_slot']}",
            f"New: {new_date} at {new_time}",
        ]
        wa_text = urllib.parse.quote('\n'.join(wa_lines))
        whatsapp_url = f"https://wa.me/{BUSINESS_WHATSAPP}?text={wa_text}"

        return jsonify({
            'success': True,
            'message': f'Appointment rescheduled to {new_date} at {new_time}.',
            'whatsapp_url': whatsapp_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    print("Database initialized. Starting server...")
    print(f"SMTP configured: {SMTP_HOST}:{SMTP_PORT} as {SMTP_USER}")
    if not SMTP_PASS:
        print("⚠️  SMTP_PASS not set. Set it via environment variable: set SMTP_PASS=your_app_password")
    print("Visit http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
