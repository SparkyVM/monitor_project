import sys
import sqlite3
##import cx_Oracle

#from PyQt6.QtCore import *
from PyQt6.QtCore import Qt
import PyQt6.QtGui as QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QMainWindow, QListWidget, QLineEdit, \
    QTreeView, QPushButton, QComboBox, QRadioButton, QMessageBox, QListWidgetItem

g_lbv = None
g_br = None
src = None
select = None
qn = None
DB_PATH = 'tkrs.db'

class MyComboBox(QComboBox):
    """Класс для отображения выпадающего списка
    Вывод списка возможных ремонтных бригад
    """

    def __init__(self):
        QComboBox.__init__(self)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT name FROM brigades ORDER BY 1')
            items = []
            for item in c.fetchall():
                items.append(item[0])

            self.addItems(items)

        self.setCurrentIndex(0)

        global g_br
        g_br = self.currentText()

    def selectBrig(self):
        global g_br
        g_br =  self.currentText()
        print (self.currentText())

class MySQLlist(QListWidget):
    """
    Класс виджета списка
    Вывод скважин из БД
    """

    def __init__(self):
        QListWidget.__init__(self)
        data = self.get_data()
        print(data)
        for elem in data:
            item = QListWidgetItem(elem)
            self.addItem(item)
        #self.set_on_map() #- ИЗ БД НА КАРТУ АВТОМАТИЧЕСКИ
        self.set_on_map_auto()

    def get_data(self):
        """Процедура получения данных об актуальном расположении бригад"""

        my_y = []

        '''        
            # подключение Oracle   
        try:
            my_connection=cx_Oracle.connect('***/****@***')
        except cx_Oracle.DatabaseError,info:
            my_y.append('Logon  Error')
            print "Logon  Error:",info
        else:

            try:
                my_cursor=my_connection.cursor()
                my_cursor.execute("SELECT * FROM ****")

            except cx_Oracle.DatabaseError,info:
                print "SQL Error:",info
                my_cursor.close()
                my_connection.close()
            else:
                for row in my_cursor.fetchall():
                    my_y.append(row[0])

                my_cursor.close()
                my_connection.close()
        '''

        return my_y

    def set_on_map(self):
        """Процедура добавления на карту"""

        data = self.selectedItems()[0].text().split(', ')
        gm = data[0]
        ceh = data[1]
        ms = data[2]
        well = data[3]
        brig = data[4] + u', ' + data[5]
        qoil = data[6]

        reply = QMessageBox.question(self, u'Дробавить на карту?' , self.selectedItems()[0].text(), QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            conn.text_factory = str
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM wells WHERE gm = :gm1 \
                   AND ceh = :ceh1 and ms = :ms1 and well_num = :well_num1', \
                   {'gm1':  (gm), 'ceh1':  (ceh), \
                   'ms1':  (ms), 'well_num1':  (well)})
            well_exsist = str(c.fetchone()[0])

            if well_exsist != u'0':
                c.execute('SELECT well_id FROM wells WHERE gm = :gm1 \
                   AND ceh = :ceh1 and ms = :ms1 and well_num = :well_num1', \
                   {'gm1':  (gm), 'ceh1':  (ceh), \
                   'ms1':  (ms), 'well_num1':  (well)})
                wid = str(c.fetchone()[0])

                c.execute('SELECT COUNT(*) FROM on_map WHERE well = :wid', {'wid': wid})
                exist1 = str(c.fetchone()[0])

                if exist1 == u'0':
                    c.execute('INSERT INTO on_map (well, brigade, gm, qoil) VALUES (:well1, :brig1, :gm1, :qoil)', \
                    {'well1': wid, 'brig1':  (brig), 'gm1':  (gm), 'qoil':  (qoil)})
                    conn.commit()
                    conn.close()
                else:
                    QMessageBox.about(self, u'Скважина уже на карте!', u'Уже добавлена.')

            else:
                QMessageBox.about(self, u'Координаты не найдены!', u'Не найдены координаты!')
        else:
            pass

    def set_on_map_auto(self):
        repair = []
        k = 0
        for i in range(0, self.count()):
            temp = self.item(i).text().split(u', ')
            repair.append([])
            for j in range(len(temp)):
                repair[k].append( temp[j] )
            k = k + 1
        #for i in repair:
        #    print i

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            for i in repair:
                c.execute('SELECT well_id FROM wells WHERE gm = :gm AND ceh = :ceh AND ms = :ms AND well_num = :well_num',
                         {'gm':  (i[0]), 'ceh':  (i[1]), \
                          'ms':  (i[2]), 'well_num': str(i[3])})
                try:
                    well_id = str(c.fetchone()[0])
                    c.execute('SELECT COUNT(*) FROM on_map WHERE well = :well_id',
                         {'well_id': well_id})
                    count = str(c.fetchone()[0])
                    if count == u'0':
                        brig =  (i[4]) + u', ' +  (i[5])
                        c.execute('INSERT INTO on_map (well, brigade, gm, qoil) VALUES (:well1, :brig1, :gm1, :qoil)', \
                        {'well1': well_id, 'brig1': brig, 'gm1':  (i[0]), 'qoil':  (i[6])})
                        conn.commit()

                except TypeError:
                    pass



class MyListWidget(QListWidget):
    """Класс Список *** """

    def __init__(self):
        QListWidget.__init__(self)
        #item = QtGui.QListWidgetItem(u'ТКРС-1')
        #self.addItem(item)
        self.populate()

    def selectItem(self):
        global select
        select = self.selectedItems()[0].text()
        #print  (select)

    def deleteItem(self):
        """Процедура удаления с карты"""

        data = self.selectedItems()[0].text().split(u', ')
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT well_id FROM wells WHERE gm = :gm AND ceh = :ceh AND ms = :ms AND well_num = :well_num',
            {'gm':  (data[0]), 'ceh':  (data[1]), \
                       'ms':  (data[2]), 'well_num': str(data[3])})

            delete_id = str(c.fetchone()[0])

            reply = QMessageBox.question(self, u'Удалить с карты?', self.selectedItems()[0].text(), QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:

                c.execute('DELETE FROM on_map WHERE well = :wid', {'wid': delete_id})
                conn.commit()
                self.populate()
            else:
                pass

    def populate(self):
        """Процедура получения списка скважин на карте"""

        self.clear()
        data = []
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT w.gm, w.ceh, w.ms, w.well_num, m.brigade, m.qoil FROM wells as w INNER JOIN on_map as m ON w.well_id = m.well \
                       ORDER BY w.gm')

            for i in c.fetchall():
                data.append(i[0] + u', '+ \
                            i[1] + u', '+ \
                            i[2] + u', '+ \
                            str(i[3]) + u', '+ \
                            i[4] + u', '+ \
                            str(i[5])
                            )
            for elem in data:
                item = QListWidgetItem(elem)
                self.addItem(item)

    def addCell(self):
        self.populate() #запрс из таблицы "в ремот"

class MyLineEdit(QLineEdit):
    """Класс Поле для поиска"""

    def __init__(self):
        QLineEdit.__init__(self)
        self.search()

    def search(self):
        global scr
        scr = self.text()

class MyLineEdit1(QLineEdit):
    """Класс Поле для ввода дебита"""

    def __init__(self):
        QLineEdit.__init__(self)
        self.setText(u'0')
        self.set_data()

    def set_data(self):
        global qn
        qn = self.text()

class MyButton1(QPushButton):
    """Кнопка приближения выбранной бригады"""

    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.zomming)

    def zomming(self):
        """Процедура приближение"""

        global select
        if select != None:
            data = select.split(u', ')
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('SELECT well_id FROM wells WHERE gm = :gm AND ceh = :ceh AND ms = :ms AND well_num = :well_num',
                {'gm':  (data[0]), 'ceh':  (data[1]), \
                       'ms':  (data[2]), 'well_num': str(data[3])})

                zoom_id = str(c.fetchone()[0])
                c.execute('DELETE FROM zoom'),
                conn.commit()
                c.execute('INSERT INTO zoom (gm, well) VALUES (:gm, :wid)', {'gm': (data[0]), 'wid': zoom_id})
                conn.commit()

class MyButton2(QPushButton):
    """Кнопка Показать общий вид"""

    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.zomming)

    def zomming(self):
        """Процедура Показать общий вид"""

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM zoom')
            conn.commit()

class MyButton3(QPushButton):
    """Кнопка Показать данные скважины"""

    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.show)

    def show(self):
        """Процедура Показать данные скважины"""

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('UPDATE window_status SET on_top = :status', {'status': True})
            conn.commit()

class MyButton4(QPushButton):
    """Кнопка Скрыть данные скважины"""

    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.clicked.connect(self.hide)

    def hide(self):
        """Процедура Скрыть данные скважины"""
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('UPDATE window_status SET on_top = :status', {'status': False})
            conn.commit()

class MyTreeView(QTreeView):
    """Класс Дерево скважин"""

    def __init__(self):
        QTreeView.__init__(self)
        self.setAnimated(True)
        self.init()
        self.activated.connect(self.printCell)
        #self.connect(self, QtCore.SIGNAL("activated(const QModelIndex &)"), self.printCell)

        self.model1 = QtGui.QStandardItemModel()

    def init(self):
        rows = self.get_wells()

        self.model = QtGui.QStandardItemModel()
        #self.model.reset()
        self.model.setHorizontalHeaderLabels ( [u'Скважины'])
        #self.model.setColumnCount(1)

        for row in rows:
            if len(self.model.findItems(row[0], Qt.MatchFlag.MatchRecursive, 0)) > 0:
                parentItem = self.model.findItems(row[0], Qt.MatchFlag.MatchRecursive, 0)[0]
                if len(self.model.findItems(row[1], Qt.MatchFlag.MatchRecursive, 0)) > 0:
                    parentItem = self.model.findItems(row[1], Qt.MatchFlag.MatchRecursive, 0)[0]
                    if len(self.model.findItems(row[2], Qt.MatchFlag.MatchRecursive, 0)) > 0:
                        parentItem = self.model.findItems(row[2], Qt.MatchFlag.MatchRecursive, 0)[0]
                        item = QtGui.QStandardItem(row[3])
                        item.setEditable(False)
                        parentItem.appendRow(item)
                    else:
                        item = QtGui.QStandardItem(row[2])
                        item.setEditable(False)
                        parentItem.appendRow(item)
                        parentItem = item
                        item = QtGui.QStandardItem(row[3])
                        item.setEditable(False)
                        parentItem.appendRow(item)

                else:
                    item = QtGui.QStandardItem(row[1])
                    item.setEditable(False)
                    parentItem.appendRow(item)
                    parentItem = item
                    item = QtGui.QStandardItem(row[2])
                    item.setEditable(False)
                    parentItem.appendRow(item)
                    parentItem = item
                    item = QtGui.QStandardItem(row[3])
                    item.setEditable(False)
                    parentItem.appendRow(item)

            else:
                parentItem = self.model.invisibleRootItem()
                item = QtGui.QStandardItem(row[0])
                item.setEditable(False)
                parentItem.appendRow(item)
                parentItem = item
                item = QtGui.QStandardItem(row[1])
                item.setEditable(False)
                parentItem.appendRow(item)
                parentItem = item
                item = QtGui.QStandardItem(row[2])
                item.setEditable(False)
                parentItem.appendRow(item)
                parentItem = item
                item = QtGui.QStandardItem(row[3])
                item.setEditable(False)
                parentItem.appendRow(item)

        self.setModel(self.model)
        #self.sortModel = MyFilterProxyModel()
        #self.sortModel.setDynamicSortFilter(True)

        #search = QtCore.QRegExp(u".*(10).*",
        #                        QtCore.Qt.CaseInsensitive,
        #                        QtCore.QRegExp.RegExp
        #                        )
        #self.sortModel.setFilterRegExp(search)
        #self.sortModel.setFilterKeyColumn(0)
        #self.sortModel.setSourceModel(self.model)
        #self.setModel(self.sortModel)
        #self.expandAll()


    def filter(self, txt):
        if txt == u'':
            self.setModel(self.model)
        else:
            self.model1.clear()
            self.model1.setHorizontalHeaderLabels ( ['Скважины'])
            for item1 in self.model.findItems(txt, Qt.MatchFlag.MatchRecursive):
               #print  (item1.parent().parent().parent().text()), \
               #    (item1.parent().parent().text()), \
               #    (item1.parent().text()), \
               #   item1.text()

                parentItem = self.model1.invisibleRootItem()
                if len(self.model1.findItems(item1.parent().parent().parent().text(), Qt.MatchFlag.MatchRecursive)) > 0:
                    item = self.model1.findItems(item1.parent().parent().parent().text(), Qt.MatchFlag.MatchRecursive)[0]
                    parentItem = item
                    if len(self.model1.findItems(item1.parent().parent().text(), Qt.MatchFlag.MatchRecursive)) > 0:
                        item = self.model1.findItems(item1.parent().parent().text(), Qt.MatchFlag.MatchRecursive)[0]
                        parentItem = item
                        if len(self.model1.findItems(item1.parent().text(), Qt.MatchFlag.MatchRecursive)) > 0:
                            item = self.model1.findItems(item1.parent().text(), Qt.MatchFlag.MatchRecursive)[0]
                            parentItem = item

                            item = QtGui.QStandardItem(item1.text())
                            item.setEditable(False)
                            parentItem.appendRow(item)

                        else:
                            item = QtGui.QStandardItem(item1.parent().text())
                            item.setEditable(False)
                            parentItem.appendRow(item)
                            parentItem = item

                            item = QtGui.QStandardItem(item1.text())
                            item.setEditable(False)
                            parentItem.appendRow(item)

                    else:
                        item = QtGui.QStandardItem(item1.parent().parent().text())
                        item.setEditable(False)
                        parentItem.appendRow(item)
                        parentItem = item

                        item = QtGui.QStandardItem(item1.parent().text())
                        item.setEditable(False)
                        parentItem.appendRow(item)
                        parentItem = item

                        item = QtGui.QStandardItem(item1.text())
                        item.setEditable(False)
                        parentItem.appendRow(item)

                else:
                    item = QtGui.QStandardItem(item1.parent().parent().parent().text())
                    item.setEditable(False)
                    parentItem.appendRow(item)
                    parentItem = item

                    item = QtGui.QStandardItem(item1.parent().parent().text())
                    item.setEditable(False)
                    parentItem.appendRow(item)
                    parentItem = item

                    item = QtGui.QStandardItem(item1.parent().text())
                    item.setEditable(False)
                    parentItem.appendRow(item)
                    parentItem = item

                    item = QtGui.QStandardItem(item1.text())
                    item.setEditable(False)
                    parentItem.appendRow(item)

            self.setModel(self.model1)
            self.expandAll()

    def get_wells(self):
        """Процедура Получить список скважин"""

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT gm, ceh, ms, well_num FROM wells ORDER BY gm, ceh, ms, well_num ')
            wells = []
            for rows in c.fetchall():
                wells.append([])
                for row in rows:
                    try:
                        wells[len(wells)-1].append(str(row))
                    except AttributeError:
                        wells[len(wells)-1].append(str(row))
            return wells


    def printCell(self, item, column = 0):
        """Проверить на существование и добавить"""

        try:
            self.well = item #.text(3)
            self.ms = self.well.parent()
            self.ceh = self.ms.parent()
            self.gm = self.ceh.parent()

            qry = self.gm.data().toString() + ', ' + self.ceh.data().toString() \
             + ', ' + self.ms.data().toString() + ', ' + self.well.data().toString()
            global g_lbv
            global g_br
            global qn
            g_lbv = qry + ', ' + g_br + ', ' + qn
            reply = QMessageBox.question(self, u'Добавить на карту?', g_lbv, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.add_item(g_lbv)
        except AttributeError:
            pass

    def add_item(self, arg):
        """Процедура добавдения скважины"""

        qry_arg = arg.split(', ')
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT well_id FROM wells WHERE gm = :gm1 \
                       AND ceh = :ceh1 and ms = :ms1 and well_num = :well_num1', \
                       {'gm1':  (qry_arg[0]), 'ceh1':  (qry_arg[1]), \
                       'ms1':  (qry_arg[2]), 'well_num1': str(qry_arg[3])})
            wid = str(c.fetchone()[0])

            c.execute('SELECT COUNT(*) FROM on_map WHERE well = :wid', {'wid': wid})

            exist1 = str(c.fetchone()[0])

            if exist1 == u'0':
                print('не найдено на карте!')

                c.execute('INSERT INTO on_map (well, brigade, gm, qoil) VALUES (:well1, :brig1, :gm1, :qoil)', \
                {'well1': wid, 'brig1':  (qry_arg[4] + u' ' + qry_arg[5]), 'gm1':  (qry_arg[0])
                , 'qoil':  (qry_arg[6])})

                conn.commit()

            else:
                QMessageBox.about(self, u'Скважина уже на карте!',\
                qry_arg[0] + u', ' + \
                qry_arg[1] + u', ' + \
                qry_arg[2] + u', ' + \
                qry_arg[3] + u' уже добавлена.')


class ApplicationWindow(QMainWindow):
    """Класс определения окна приложения"""

    def __init__(self):
        super().__init__()
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.setGeometry(100, 100, 1000, 800)

        self.main_widget = QWidget(self)

            # Определение виджетов
        self.l = QGridLayout(self.main_widget)
        self.l.setSpacing(2)

        self.lw2 = MySQLlist()
        self.label1 = QLabel('Бригады')
        self.label2 = QLabel('Поиск скважины')
        self.label3 = QLabel('  На карте:')
        self.label4 = QLabel('  В базе данных:')
        self.label5 = QLabel('Q нефти:')
        self.cb1 = MyComboBox()
        self.tree1 = MyTreeView()
        self.lw1 = MyListWidget()
        self.le1 = MyLineEdit()
        self.le2 = MyLineEdit1()
        self.lw1.setMinimumWidth(500)
        self.lw1.setMinimumHeight(300)

        self.bt1 = MyButton1("Скважина")
        self.bt2 = MyButton2("Общий")

        self.bt3 = QRadioButton("Север")
        #self.bt3.setChecked(True)
        self.bt4 = QRadioButton("Центр")
        self.bt5 = QRadioButton("Юг")

        self.bt6 = MyButton3('Показать')
        self.bt7 = MyButton4('Скрыть')

            # Добавление виджетов
        self.l.addWidget(self.bt6, 0, 4)
        self.l.addWidget(self.bt7, 0, 5)

        self.l.addWidget(self.label1, 1, 1)
        self.l.addWidget(self.cb1, 1, 2)
        self.l.addWidget(self.label2, 2, 1)
        self.l.addWidget(self.le1, 2, 2)
        self.l.addWidget(self.label5, 0, 1)
        self.l.addWidget(self.le2, 0, 2)
        self.l.addWidget(self.tree1, 3, 1, 6, 2)
        #self.l.addWidget(self.button1, 4, 1)
        self.l.addWidget(self.label3, 1, 3)

        self.l.addWidget(self.bt1, 1, 4)
        self.l.addWidget(self.bt2, 1, 5)

        self.l.addWidget(self.lw1, 2, 3, 3, 3)
        self.l.addWidget(self.label4, 6, 3)
        self.l.addWidget(self.lw2, 7, 3, 1, 3)

        self.l.addWidget(self.bt3, 1, 8)
        self.l.addWidget(self.bt4, 2, 8)
        self.l.addWidget(self.bt5, 3, 8)

        self.set_map()

        """Сигналы"""
        self.bt3.toggled.connect(self.change_map)
        self.bt4.toggled.connect(self.change_map)
        self.bt5.toggled.connect(self.change_map)

        '''
        self.connect(self.tree1, QtCore.SIGNAL("activated(const QModelIndex &)"), self.cb1.selectBrig)
        self.connect(self.tree1, QtCore.SIGNAL("activated(const QModelIndex &)"), self.lw1.addCell)
        self.connect(self.cb1, QtCore.SIGNAL("currentIndexChanged(QString)"), self.cb1.selectBrig)
        self.connect(self.lw1, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.lw1.deleteItem)
        self.connect(self.lw1, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.lw1.selectItem)
        self.connect(self.le1, QtCore.SIGNAL("textChanged(QString)"), self.tree1.filter)
        self.connect(self.le2, QtCore.SIGNAL("textChanged(QString)"), self.le2.set_data)
        # self.connect(self.button1, QtCore.SIGNAL("clicked()"), self.tree1.filter)
        self.connect(self.lw2, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.lw2.set_on_map)
        self.connect(self.lw2, QtCore.SIGNAL("activated(const QModelIndex &)"), self.lw1.addCell)
        '''


        #self.main_widget.setFocus()
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.FramelessWindowHint)
        self.setCentralWidget(self.main_widget)

    def set_map(self):
        """Процедура получения активной карты"""

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT gm FROM current_map')
            gm = str(c.fetchone()[0])

        if gm == 'Север':
            self.bt3.setChecked(True)
        if gm == 'Центр':
            self.bt4.setChecked(True)
        if gm == 'Юг':
            self.bt5.setChecked(True)

    def change_map(self):
        """Процедура замены активной карты"""

        gm = 0
        if self.bt3.isChecked():
            gm = 'Север'
        if self.bt4.isChecked():
            gm = 'Центр'
        if self.bt5.isChecked():
            gm = 'Юг'

        if gm != 0:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM current_map')
                c.execute('INSERT INTO current_map (gm) VALUES (:gm1)', \
                        {'gm1': gm})
                conn.commit()


    # MAIN
qApp = QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle(u"Карта Клиент")
aw.setWindowIcon(QtGui.QIcon('map_app.png'))
#aw.showMaximized()
aw.show()
sys.exit(qApp.exec())
qApp.exec()

"""

def set_map(self, gm):
        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('DELETE FROM current_map')
        c.execute('INSERT INTO current_map (gm) VALUES (:gm1)', \
                    {'gm1':  (gm)})
        conn.close()

"""