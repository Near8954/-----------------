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
        if i in name or i.upper() in name:
            return True
    return False


ALL_DATA = {}
hashed_data = []
for j in (os.walk("D:\\gr_test")):
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
                hashed_data.append(x)
                query = f"""INSERT INTO graphical_files VALUES ('{k}', '{path}', '{x}')"""
                cur.execute(query)
data = []
for i in set(hashed_data):
    if hashed_data.count(i) > 1:
        query = f"""select file_name, path from graphical_files where (file_hash = '{i}')"""
        data.append(list(cur.execute(query)))
print(data)
for i in range(len(data)):
    f1 = open(data[i][0][1], 'rb')
    f2 = open(data[i][1][1], 'rb')
    if f1 == f2:
        print('check')


con.commit()
con.close()
