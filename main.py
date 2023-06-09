from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal  # Импортируем uic
import sys
import sqlite3
import os
import hashlib
import time


class Worker(QObject):
    finished = pyqtSignal()
    progress1 = pyqtSignal(str)
    progress2 = pyqtSignal(str)
    progress3 = pyqtSignal(str)
    stop = pyqtSignal()

    stopped = False

    def is_image(self, name):
        ext = ['.jpeg', '.png', '.bmp', '.jpg']
        for i in ext:
            if i in name or i.upper() in name:
                return True
        return False

    def setupDB(self):
        self.con = sqlite3.connect("files.db")  # Подключение к БД
        self.cur = self.con.cursor()  # Создание курсора
        self.cur.execute("""CREATE TABLE IF NOT EXISTS graphical_files (
            file_name text, 
            path text, 
            file_hash text
        )""")
        self.con.commit()

    def run(self):
        self.setupDB()
        ALL_DATA = {}
        text = f''
        text_2 = f''
        text_3 = f''
        hashed_data = []
        text_3 += 'Начало поиска файлов\n\n'
        self.progress3.emit(text_3)
        cnt2 = 0
        time_start = time.time()
        for j in (os.walk("D:\\")):
            if self.stopped:
                break
            for k in j[2]:
                if not self.stopped:
                    cnt2 += 1
                    if self.is_image(k) and not '$' in k:
                        ALL_DATA[k] = j[0]
                        path = j[0] + '\\' + k
                        query = "select count(1) as cnt from graphical_files where file_name = :filename and path=:path"
                        try:
                            result = self.cur.execute(
                                query, {'filename': k, 'path': path})
                        except Exception:
                            print(k, path)
                            continue
                        text += f'{k} {path}\n'
                        if list(result)[0][0] == 0:
                            f = open(path, 'rb')
                            img = f.read()
                            x = hashlib.md5(img).hexdigest()
                            hashed_data.append(x)
                            query = """INSERT INTO graphical_files VALUES (:k, :path, :x)"""
                            self.cur.execute(
                                query, {'k': k, 'path': path, 'x': x})
        time_all = time.time() - time_start
        self.progress1.emit(text)
        self.con.commit()
        text_3 += 'Конец поиска файлов\n\n'
        text_3 += 'Поиск хэшей\n\n'
        self.progress3.emit(text_3)
        data = []
        for i in set(hashed_data):
            if hashed_data.count(i) > 1:
                query = f"""select file_name, path from graphical_files where (file_hash = '{i}')"""
                data.append(list(self.cur.execute(query)))
        text_3 += 'Конец поиска хэшей\n\n'
        self.progress3.emit(text_3)
        cnt = 0
        for i in range(len(data)):
            for j in range(len(data[i])):
                cnt += 1
                text_2 += f'name: {data[i][j][0]} path: {data[i][j][1]}\n'
            text_2 += '---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n'
        text_3 += 'Конец работы программы\n\n'
        text_3 += (str(cnt) + '\n\n')
        text_3 += str(int(cnt2 / time_all))
        self.progress3.emit(text_3)
        self.progress2.emit(text_2)
        self.con.close()
        self.finished.emit()


class MyWidget(QMainWindow):
    def __init__(self):
        self.stopped = True
        self.started = False
        super().__init__()
        uic.loadUi('simple_gui.ui', self)  # Загружаем дизайн
        self.setWindowIcon(QtGui.QIcon('icon2.png'))
        self.pushButton.clicked.connect(self.run_cmd)
        self.pushButton_2.clicked.connect(self.stop)
        self.pushButton_2.setEnabled(False)

    def setupDB(self):
        # Подключение к БД
        self.con = sqlite3.connect("files.db")

        # Создание курсора
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS graphical_files (
            file_name text, 
            path text, 
            file_hash
        )""")

        self.con.commit()

    def run_cmd(self):
        self.started = True
        self.plainTextEdit.setPlainText('')
        self.plainTextEdit_2.setPlainText('')
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(
            lambda: self.pushButton_2.setEnabled(False))
        self.worker.finished.connect(lambda: os.remove('files.db'))
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress1.connect(self.reportProgress1)
        self.worker.progress2.connect(self.reportProgress2)
        self.worker.progress3.connect(self.reportProgress3)
        self.thread.finished.connect(lambda: self.pushButton.setEnabled(True))
        self.thread.start()

    def stop(self):
        if self.started:
            self.worker.stopped = True
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(False)

    def reportProgress1(self, s):
        self.plainTextEdit.setPlainText(s)

    def reportProgress2(self, s):
        self.plainTextEdit_2.setPlainText(s)

    def reportProgress3(self, s):
        self.plainTextEdit_3.setPlainText(s)

    def closeEvent(self, event):  # Переопределяем кнопку закрытия приложения
        self.setupDB()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Выход")
        dlg.setText("Вы уверены, что хотите уйти?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            self.con.close()
            os.remove('files.db')
            self.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
