'''import sqlite3

con = sqlite3.connect("db.sqlite3")
type(con)
cursor = con.cursor()

cursor.execute("SELECT * FROM school_report_teacher")
print(cursor.fetchall())

cursor.execute("INSERT INTO school_report_teacher \
    VALUES(8, 'Lee', 999999, '1', '6')" )
cursor.execute("SELECT * FROM school_report_teacher")
print(cursor.fetchall())
con.commit()
con.close()'''
import random

p = random.random()
print(p)
print(p)