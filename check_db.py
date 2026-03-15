import sqlite3
conn = sqlite3.connect('numbersnme.db')
c = conn.cursor()

# Add email_sent column if missing
try:
    c.execute("ALTER TABLE numerology_contacts ADD COLUMN email_sent INTEGER DEFAULT 0")
    print("Added email_sent column")
except Exception as e:
    print(f"Column already exists or error: {e}")

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', [r[0] for r in c.fetchall()])
print()

# Show schema
c.execute("PRAGMA table_info(numerology_contacts)")
print("Columns:", [r[1] for r in c.fetchall()])
print()

c.execute("SELECT * FROM numerology_contacts")
for row in c.fetchall():
    print(row)

conn.commit()
conn.close()
