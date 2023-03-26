from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5 import uic  # Импортируем uic
import sys
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


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('simple_gui.ui', self)  # Загружаем дизайн
        self.pushButton.clicked.connect(self.run)
        # Обратите внимание: имя элемента такое же как в QTDesigner

    def run(self):

        ALL_DATA = {}
        text = f''
        hashed_data = []
        for j in (os.walk("D:\\")):
            for k in j[2]:
                if is_image(k):
                    ALL_DATA[k] = j[0]
                    path = j[0] + '\\' + k
                    query = f"""select count(1) as cnt from graphical_files where file_name = '{k}' and path='{path}'"""
                    result = cur.execute(query)
                    text += f'{k} {path}\n'
                    self.plainTextEdit.setPlainText(text)
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
            # self.label_2.setText(f'{data[0][i][0]}, {data[0][i][1]}')
            pass

    def closeEvent(self, event):  # Переопределяем кнопку закрытия приложения
        text, ok_pressed = QInputDialog.getText(
            self, 'Вы покидаете приложение', 'Вы уверены что хотите уйти?(y/n)')
        if ok_pressed and text.lower() == 'y':
            # print(text)
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
    con.commit()
    con.close()
