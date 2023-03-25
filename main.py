import sqlite3
import os
import hashlib

c = 0
hashed_data = []


# Подключение к БД
con = sqlite3.connect("files.db")

# Создание курсора
cur = con.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS graphical_files (
    file_name text, 
    path text, 
    file_hash
)""")

con.commit()


def is_image(name):
    ext = ['.jpeg', '.png', '.bmp', '.jpg']
    for i in ext:
        if i in name:
            return True
    return False


ALL_DATA = {}
hashed_data = set()
for j in (os.walk("D:\\")):
    for k in j[2]:
        if is_image(k):
            ALL_DATA[k] = j[0]
            path = j[0] + '\\' + k
            query = f"""select count(1) as cnt from graphical_files where file_name = '{k}' and path='{path}'"""
            result = cur.execute(query)
            if list(result)[0][0] == 0:
                f = open(path, 'rb')
                img = f.read()
                x = hashlib.md5(img).hexdigest()
                hashed_data.add(x)
                query = f"""INSERT INTO graphical_files VALUES ('{k}', '{path}', '{x}')"""
                cur.execute(query)

for i in hashed_data:
    pass


con.commit()
con.close()
