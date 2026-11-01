import sqlite3

conn = sqlite3.connect("restraunt.db")

cursor = conn.cursor()

cursor.executescript("CREATE TABLE users (id TEXT, name VARCHAR(50), password BLOB, role VARCHAR(10));")
cursor.executescript("CREATE TABLE orders (id TEXT, item VARCHAR(50));")
cursor.executescript("CREATE TABLE sessions (token VARCHAR(100), id TEXT);")

conn.commit()
conn.close()

