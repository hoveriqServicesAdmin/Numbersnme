import sqlite3
conn = sqlite3.connect(r"C:\Users\Admin\PycharmProjects\Numbersnme\numbersnme.db")
cur = conn.cursor()
print('tables', cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall())
print('appointments schema', cur.execute("PRAGMA table_info(appointments)").fetchall())
print('appointment indexes', cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='appointments'").fetchall())
print('appointments count', cur.execute("SELECT COUNT(*) FROM appointments").fetchone()[0])
conn.close()
