import sys
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import * 
from src.trans import process
import uuid
from src.dict import read
import configparser
import pyperclip

class MyButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(MyButtonDelegate, self).__init__(parent)
    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_read = QPushButton(
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_read.index = [index.row(), index.column()]
            button_read.setIcon(QIcon('./src/close.png'))
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_read)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(
                index,
                widget
            )

class MyRadioDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(MyRadioDelegate, self).__init__(parent)
    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_ex = QRadioButton('Ex',
                self.parent(),
            )
            button_chaos = QRadioButton('Chaos',
                self.parent(),
            )
            button_ex.index = [index.row(), index.column()]
            button_chaos.index = [index.row(), index.column()]
            button_ex.setChecked(True)
            button_ex.toggled.connect(lambda :self.parent().btnstate(button_ex))
            button_chaos.toggled.connect(lambda :self.parent().btnstate(button_chaos))
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_ex)
            h_box_layout.addWidget(button_chaos)
            h_box_layout.setContentsMargins(0,0,0,0)
            h_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            
            self.parent().setIndexWidget(
                index,
                widget
            )

class MyTableView(QTableView):
    def __init__(self, parent=None):
        super(MyTableView, self).__init__(parent)
        self.setItemDelegateForColumn(5, MyButtonDelegate(self))
        self.setItemDelegateForColumn(4, MyRadioDelegate(self))

    def cellButtonClicked(self):
        index = self.model().index(self.sender().index[0], 0)
        index2 = self.model().index(self.sender().index[0], 1)
        craft = self.model().data(index,Qt.ItemDataRole.DisplayRole)
        level = self.model().data(index2,Qt.ItemDataRole.DisplayRole)
        self.model().delete(craft,level)

    def btnstate(self,btn):
        index = self.model().index(self.sender().index[0], 4)
        if btn.text()=='Ex':
            if btn.isChecked()==True:
                self.model().setData(index,0,Qt.ItemDataRole.EditRole)

        if btn.text()=="Chaos":
            if btn.isChecked() == True:
                self.model().setData(index,1,Qt.ItemDataRole.EditRole)
    
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(TableModel, self).__init__()
        testdata = []
        self._data = testdata
        self._dict = {}

    def data(self, index, role):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                if index.column()<4:
                    value = self._data[index.row()][index.column()]
                    return str(value)
    
    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 6

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def clear(self):
        self._data = []
        self._dict.clear()
        return

    def add(self,data):
        for d in data:
            if tuple(d) in self._dict:
                self._dict[tuple(d)][0] += 1
            else:
                self._dict[tuple(d)] = [1,0]
        self.dictToData()

    def dictToData(self):
        res = []
        for i in self._dict.items():
            res.append([i[0][0],i[0][1],i[1][0],i[1][1],0])
        self._data = res
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        col = {0:'工艺',1:'等级',2:'数量',3:'价格',4:'单位',5:'操作'}
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return col[section]
        return super().headerData(section, orientation, role)

    def generate(self,name):
            if name: 
                header = "> **WTS Archnemesis Softcore**\n> **IGN: "+name+"**\n"
                config['UserInfo']['name'] = name
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
            else:
                header = "> **WTS Archnemesis Softcore**\n>"
            res = ""
            for d in self._data:
                if d[0] in dict:
                    print(d)
                    output = "> `" + str(d[2]) + 'x ' + dict[d[0]].rstrip("\n")
                    while len(output) < 60:
                        output += " "
                    output += "[" + str(d[1])+ "]  " + "< " + str(d[3]) + ('ex' if d[4]==0 else 'c')  + " >`\n"
                    res += output
            pyperclip.copy(header+res)
            return

    def delete(self,craft,level):
        self.layoutAboutToBeChanged.emit()
        if tuple([craft,level]) in self._dict:
                
                self._dict.pop(tuple([craft,level]))
        self.dictToData()
        self.layoutChanged.emit()

class MainWindow(QDialog) :
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('HarvestTrade')
        self.setFixedWidth(800)
        self.setFixedHeight(560)

        tableView = MyTableView()

        nameLabel = QLabel('IGN:',self)
        nameLineEdit = QLineEdit(self)
        nameLabel.setBuddy(nameLineEdit)
        nameLineEdit.setMaximumWidth(100)
        if config.has_option('UserInfo','name'):
            nameLineEdit.setText(config['UserInfo']['name'])
        formLayout = QFormLayout()
        formLayout.addRow(nameLabel, nameLineEdit)
        formLayout.setContentsMargins(5,5,0,0)

        btnCapture = QPushButton('抓取')
        btnOK = QPushButton('生成')
        btnCancel = QPushButton('清空')

        btnCapture.clicked.connect(self.capture)
        btnCancel.clicked.connect(self.clear)
        btnOK.clicked.connect(self.generate)

        mainLayout = QGridLayout(self)
        self.model = TableModel()
        tableView.setModel(self.model)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        tableView.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        tableView.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeMode.Fixed)
        mainLayout.addWidget(tableView,0,0,15,6)

        mainLayout.addLayout(formLayout,16,0,1,2)
        

        mainLayout.addWidget(btnCapture,17,0,1,2)
        mainLayout.addWidget(btnOK,17,2,1,2)
        mainLayout.addWidget(btnCancel,17,4,1,2)
        

    def capture(self):
        screen = QApplication.primaryScreen()
        # grabWindow(winId,left,top,height,width)
        screenshot = screen.grabWindow(0,1060,410,650,635)
        path = './temp/' + str(uuid.uuid4()) +'.jpg'
        screenshot.save(path, 'jpg')
        self.res = process(path,dict)
        self.add()

    def add(self):
        self.model.layoutAboutToBeChanged.emit()
        self.model.add(self.res)
        self.model.layoutChanged.emit()

    def clear(self):
        self.model.layoutAboutToBeChanged.emit()
        self.model.clear()
        self.model.layoutChanged.emit()

    def generate(self):
        name = self.layout().itemAt(1).itemAt(1).widget().text()
        self.model.generate(name)


if __name__ == '__main__':
    dict = read()
    config = configparser.ConfigParser()
    config.read('config.ini')
    app = QApplication(sys.argv)
    main = MainWindow()
    main.move(1920,700)
    main.show()
    sys.exit(app.exec())