
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtWidgets import QTextBrowser, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QLineEdit, QRadioButton, QPushButton, QLabel, QLayout
from PyQt5.QtGui import QTextCursor
import search


class ShowFiles(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('show_files.ui', self)
        # self.setFixedSize(240, 50)
        self.func_mappingSignal()
        self.op_file = OpenFile()

    def func_mappingSignal(self):
        self.tableWidget.clicked.connect(self.func_test)

    def func_test(self, item):
        cellContent = item.data()
        lineNo = item.siblingAtColumn(0).data()
        print(cellContent)  # test
        if cellContent[0] == '/':
            # print('well played')  # test

            self.op_file.loadText(cellContent, int(lineNo) + 23)
            self.op_file.show()


class OpenFile(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('file_open.ui', self)

    def loadText(self, file1, lineNo):
        self.setWindowTitle(file1)
        with open(file1, 'r') as f:
            self.textBrowser.setText(f.read())
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(cursor.Down, cursor.MoveAnchor,  lineNo)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('search_parameters.ui', self)
        self.pushButton.clicked.connect(self.run)
        self.sf = ShowFiles()
        self.sf.setWindowTitle('Table')

    def run(self):
        name = self.lineEdit.text()
        args = self.lineEdit_2.text()
        class_name = self.lineEdit_3.text()
        doc_string = self.lineEdit_4.text()

        if self.radioButton.isChecked():
            # функция
            type2 = 'f'
        elif self.radioButton_2.isChecked():
            # класс
            type2 = 'c'
        else:
            # глобальная переменная
            type2 = 'gv'

        result = search.start(type2, name, args, class_name, doc_string)

        self.sf.tableWidget.setRowCount(len(result))
        self.sf.tableWidget.setColumnCount(len(result[0]))
        self.sf.titles = [description[0] for description in search.cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.sf.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        self.sf.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
