import sqlite3

conn = sqlite3.connect('sql.db')

sel = conn.execute('''SELECT COUNT(USERNAME) FROM users WHERE USERNAME = ?''', ('giangpt',))
for i in sel:
    print(i)