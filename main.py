from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
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
        self.stopped = True
        super().__init__()
        uic.loadUi('simple_gui.ui', self)  # Загружаем дизайн
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.stop)

    def run(self):
        self.stopped = False

        ALL_DATA = {}
        text = f''
        hashed_data = []
        print('Начало поиска файлов')
        for j in (os.walk("D:\\")):
            if not self.stopped:
                for k in j[2]:
                    if is_image(k):
                        ALL_DATA[k] = j[0]
                        path = j[0] + '\\' + k
                        query = f"""select count(1) as cnt from graphical_files where file_name = '{k}' and path='{path}'"""
                        result = cur.execute(query)
                        text += f'{k} {path}\n'
                        if list(result)[0][0] == 0:
                            f = open(path, 'rb')
                            img = f.read()
                            x = hashlib.md5(img).hexdigest()
                            hashed_data.append(x)
                            query = f"""INSERT INTO graphical_files VALUES ('{k}', '{path}', '{x}')"""
                            cur.execute(query)
        con.commit()
        self.plainTextEdit.setPlainText(text)
        print('Конец поиска файлов')
        data = []
        print('Поиск хэшей')
        for i in set(hashed_data):
            if hashed_data.count(i) > 1:
                query = f"""select file_name, path from graphical_files where (file_hash = '{i}')"""
                data.append(list(cur.execute(query)))
        print('Конец поиска хэшей')
        text_2 = f''
        for i in range(len(data)):
            for j in range(len(data[i])):
                text_2 += f'{data[i][j][0]} {data[i][j][1]}'

        self.plainTextEdit_2.setPlainText(text_2)

    def closeEvent(self, event):  # Переопределяем кнопку закрытия приложения
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Выход")
        dlg.setText("Вы уверены, что хотите уйти?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            event.accept()
            con.close()
            os.remove('files.db')
        else:
            event.ignore()

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
