import sys
from PyQt6.QtCore import *
#from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPainterPath, QPen, QBrush, QIcon
#from PyQt6.QtOpenGL import *
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QGridLayout, QGraphicsView, QGraphicsScene
import sqlite3
#import cx_Oracle

rects = []

info1 = None

DB_PATH = 'tkrs.db'


def get_new_well_info(well_id):
    """Получение информации по скважине"""

    qry = []
    '''
        # подключение Oracle
    try:
        my_connection=cx_Oracle.connect('****/******')
    except cx_Oracle.DatabaseError,info:
        print "Logon  Error:",info
        exit(0)
    my_cursor=my_connection.cursor()
    try:
        my_cursor.execute("******")

    except cx_Oracle.DatabaseError,info:
        my_cursor.close()
        my_connection.close()
        return 0
    for row in my_cursor.fetchall():
        for d in row:
            qry.append(d)

    my_cursor.close()
    my_connection.close()
    '''
    return qry

def get_coord():
    coord = []
    brig = []
    well = []
    ms = []
    x = []
    y = []
    wid = []
    qoil = []

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT gm FROM current_map')
        map1 = c.fetchone()[0]
        c.execute('SELECT w.coor_x, w.coor_y, w.ms, w.well_num, m.brigade, w.well_id, m.qoil \
                   FROM wells as w INNER JOIN on_map as m ON w.well_id = m.well \
                   WHERE m.gm = :gm1 \
                   ', \
                   {'gm1': map1})

        for i in c.fetchall():
            x.append(i[0])
            y.append(i[1])
            ms.append(i[2])
            well.append(i[3])
            brig.append(i[4])
            wid.append(i[5])
            qoil.append(i[6])

    index = 0
    if map1 == 'Север':
        for i in range(0, len(x)):
            x_px = int(2990 * (float(y[index]) - 49.8966) / (52.5597 - 49.8967))
            y_px = int(2760 * (54.6730 - float(x[index])) / (54.6730 - 53.3070)) - 100
            coord.append([x_px, y_px, brig[index], well[index], ms[index], wid[index], qoil[index]])
            index = index + 1

    if map1 == 'Центр':
        for i in range(0, len(x)):

             #x_px = int(4570 * (float(y[index]) - 47.924263) / (52.185585 - 47.924263))
             #y_px = int(1734 * (53.927004 - float(x[index])) / (53.927044 - 52.84999)) + 100
            x_px = int(4570 * (float(y[index]) - 47.924263) / (52.1699 - 47.9196))
            y_px = int(1734 * (53.881 - float(x[index])) / (53.881 - 52.8957))
            coord.append([x_px, y_px, brig[index], well[index], ms[index], wid[index], qoil[index]])
            index = index + 1

    if map1 == 'Юг':
        for i in range(0, len(x)):

            #x_px = int(2907 * (float(y[index]) - 48.17927) / (51.862592 - 48.17927))
            #y_px = int(1934 * (53.241817 - float(x[index])) / (53.241817 - 51.765835))
            x_px = int(3182 * (float(y[index]) - 48.3018) / (51.8626 - 48.3108))
            y_px = int(2178 * (53.2161 - float(x[index])) / (53.2161 - 51.7576))
            coord.append([x_px, y_px, brig[index], well[index], ms[index], wid[index], qoil[index]])
            index = index + 1

    return coord

class MyMap(QPixmap):
    """Класс формирование карты"""

    def __init__(self, *args):
        QPixmap.__init__(self, *args)
        self.current_map = self.get_map()
        self.set_map(self.current_map)

    def set_map(self, gm):
        """Процедура установки подложки"""

        if gm == 'Север':
            self.load('media/sever.png')
        if gm == 'Центр':
            self.load('media/centr.png')
        if gm == 'Юг':
            self.load('media/ug.png')

    def get_map(self):
        """Процедура получения текущей карты из БД"""

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT gm FROM current_map')
            current_map = c.fetchone()[0]
            return current_map

    def get_transfer(self, x, y):
        """Процедура переноса координат"""

        map1 = self.get_map()
        if map1 == 'Север':
            x_px = int(2990 * (y - 49.8966) / (52.5597 - 49.8967))
            y_px = int(2760 * (54.6730 - x) / (54.6736 - 53.3070)) - 100

        if map1 == 'Центр':
            x_px = int(4570 * (y - 47.924263) / (52.1699 - 47.9196))
            y_px = int(1734 * (53.881 - x) / (53.881 - 52.8957))

        if map1 == 'Юг':
             #x_px = int(2907 * (y - 48.17927) / (51.862592 - 48.17927))
             #y_px = int(1934 * (53.241817 - x) / (53.241817 - 51.765835))
            x_px = int(3182 * (y - 48.3018) / (51.8626 - 48.3108))
            y_px = int(2178 * (53.2161 - x) / (53.2161 - 51.7576))

        return x_px, y_px

    def change_map(self):
        """Процедура смены карты"""

        self.current_map = self.get_map()
        self.set_map(self.current_map)

class MyView(QGraphicsView):
    """Класс отображения карты"""

    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self.zoom = False

        self.well_info = QLabel(u'', self)
        self.well_info.hide()
        self.well_info.setStyleSheet("QLabel { background-color: white;}")

        #self.well_info1 = QLabel(u'', self)
        #self.well_info1.hide()
        #self.well_info1.setStyleSheet("QLabel { background-color: white;}")

        self.map = None
        self.init()
        self.text = u'ТЕСТ'
        self.i = 0
        self.d = 0
        f = 1.41 ** ( - 1460 / 480.0)
        self.scale(f, f)

        timer1 = QTimer(self)
        timer1.timeout.connect(self.update)
        #self.connect(timer1, PyQt4.QtCore.SIGNAL("timeout()"), self.update)
        timer1.start(3000)

    def update(self):
        """***"""

        b = get_coord()
        new_map = self.px.get_map()

        if self.map != new_map or self.a != b:

            #self.setViewport(QGLWidget())
            try:
                self.scene.removeItem(self.scene.items()[0])
            except IndexError:
                pass

            for i in self.scene.items():
                self.scene.removeItem(i)

            self.px = MyMap()
            self.scene = QGraphicsScene(self)
            global rects
            rects = []

            all_coord = []
            for points in b:
                all_coord.append([points[0], points[1]])

            for point in b:
                self.set_point(point, all_coord)
            self.set_sities(new_map)

            self.a = b
            self.map = new_map

            self.scene.addPixmap(self.px)
            self.setScene(self.scene)

        else:
            pass

        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM zoom')

        zoom_count = str(c.fetchone()[0])
        conn.close()
        if zoom_count == '0':
            if self.zoom == True:
                f = 1.41 ** ( - 1300/ 480.0)
                self.scale(f, f)
                self.zoom = False
                self.px = MyMap()
                self.well_info.hide()
                #self.well_info1.hide()
        else:

             conn = sqlite3.connect(DB_PATH)
             conn.text_factory = str
             c = conn.cursor()
             c.execute('SELECT gm FROM zoom')
             zoom_map = c.fetchone()[0].decode('UTF-8')
             if zoom_map == self.map:
                c.execute('SELECT well FROM zoom')
                try:
                    well_id = str(c.fetchone()[0])
                    c.execute('SELECT coor_x, coor_y FROM wells WHERE well_id = :wid',
                    {'wid': well_id})

                    xy = []
                    for item in c.fetchone():
                        xy.append(item)

                    x = float(xy[0])
                    y = float(xy[1])

                    conn.close()
                except TypeError:
                    x, y = 0
                x_px, y_px = self.px.get_transfer(x, y)
             #x_px = int(3038 * (y - 49.8966) / (52.5597 - 49.8967))
             #y_px = int(2796 * (54.6730 - x) / (54.6736 - 53.3070)) - 100

                if self.zoom == False:
                    f = 1.41 ** (  1280 / 480.0)

                    self.scale(f, f)

                    self.centerOn(x_px, y_px)
                    pnt = QPainter()
                    pnt.begin(self.px)
                    pen = QPen(Qt.GlobalColor.green, 7)
                    pnt.setPen(pen)
                    pnt.drawEllipse(x_px - 50,y_px - 50 ,100,100)
                    pnt.end()
                    self.zoom = True
                    self.well_info.show()
                    self.well_info.setGeometry(20, 920, 1800, 90)

                    #self.well_info1.show()
                    #self.well_info1.setGeometry(1200, 20, 600, 90)

                    for i in b:

                        if str(i[5]) == well_id:

                            try:
                                self.scene.removeItem(self.scene.items()[0])
                            except IndexError:
                                pass

                            for i in self.scene.items():
                                self.scene.removeItem(i)

                            all_coord = []
                            for points in b:
                                all_coord.append([points[0], points[1]])

                            for point in b:
                                self.set_point(point, all_coord)
                            self.set_sities(new_map)

                            self.scene.addPixmap(self.px)
                            self.setScene(self.scene)

                            """
                            self.well_info.setFont(QFont('Decorative', 48))
                            self.well_info.setText(u' ' + i[4] + u', ' + unicode(i[3]) + u', ' + i[2])

                            self.well_info1.setFont(QFont('Decorative', 48))
                            self.well_info1.setText(u' Qн: ' + str(i[6]) + u' т/сут. ' )
                            """

                            new_info = get_new_well_info(well_id)

                            self.well_info.setFont(QFont('Decorative', 24))
                            self.well_info.setText(u' ' + i[3] + u', ' + i[4] + u', ' + i[2] + u', ' + new_info[0].decode('cp1251') +
                            u', '    +  str(new_info[1]) + u' / '
                                                          +str(new_info[2]) + u' / '
                                                            + str(new_info[3]) + u'%')

                            #self.well_info1.setFont(QFont('Decorative', 24))
                            #self.well_info1.setText( u' '    +  str(new_info[1]) + u' / '
                            #                              +str(new_info[2]) + u' / '
                            #                                + str(new_info[3]) + u'%'
                            #                             )

                            conn.close()
                        else:
                            pass

        conn.close()


    def init(self):

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM zoom')
            conn.commit()

        self.px = MyMap()       #('sgm02.png')
        self.map = self.px.get_map()
                                #self.px.set_map('ugm')
                                #self.setViewport(QGLWidget())
        self.scene = QGraphicsScene(self)

        self.a = get_coord()
        all_coord = []
        for points in self.a:
            all_coord.append([points[0], points[1]])

        for point in self.a:
            self.set_point(point, all_coord)
        self.set_sities(self.map)
        self.scene.addPixmap(self.px)
        self.setScene(self.scene)


    def set_sities(self, gm):
        """Отобразить города"""

        pnt = QPainter()
        pnt.begin(self.px)
        path = QPainterPath()
        pen = QPen()

        if gm == u'Север':
            dx, dy = 10, 20
            pnt.setFont(QFont('Decorative', 32))
            #pnt.drawText(1430 - 25 + dx, 1455 + dy, u'Суходол')
            pen.setWidth(3)
            pnt.setPen(pen)
            pnt.setBrush(Qt.GlobalColor.white)
            path.addText(1430 - 25 + dx, 1455 + dy, QFont('Decorative', 32), u"Суходол")
            pnt.drawPath(path)
            pnt.drawText(2461 - 50 + dx, 1904 + dy, u'Похвистнево')
            pnt.drawText(370 - 25 + dx, 1477 + dy, u'Елховка')
            pnt.drawText(1757 + dx + dx, 990 + dy, u'Исаклы')
            pnt.drawText(579 + dx, 850 + dy, u'Кошки')
            pnt.drawText(1252 - 50 + dx, 436 + 10 + dy, u'Челно-Вершины')
            pnt.drawText(2449 + dx, 994 + 10 + dy, u'Камышла')
            pnt.drawText(2321 - 10 + dx, 716 + 10 + dy, u'Клявлино')

            #малые населенные пункты:
            pnt.setFont(QFont('Decorative', 26))
            pnt.drawText(655, 1395, u'Никитинка')
            pnt.drawText(1080, 1514, u'Чекалино')
            pnt.drawText(1655, 1805, u'Сидоровка')
            pnt.drawText(1485, 1915, u'Кабановка')
            pnt.drawText(1180, 1800, u'Верхняя Орлянка')
            pnt.drawText(1794, 1646, u'Мордово-Аделяково')
            pnt.drawText(2223, 2261, u'Большой Толкай')
            pnt.drawText(2494, 627, u'Петровка')
            pnt.drawText(2465, 1540, u'Кротково')
            pnt.drawText(1980, 1165, u'Черная Речка')
            pnt.drawText(1383, 370, u'Покровка')
            pnt.drawText(343, 528, u'Старое Юреево')
            pnt.drawText(1761, 1375, u'Новое Якушкино')
            pnt.drawText(1663, 1468, u'Старое Якушкино')
            pnt.drawText(1280, 993, u'Красный Городок')
            pnt.drawText(1136, 910, u'Покровка')
            pnt.drawText(1735, 434, u'Черная Речка')

        if gm == u'Центр':
            pnt.setFont(QFont('Decorative', 32))
            pnt.drawText(1603, 847, u'Жигулевск')
            pnt.drawText(1442, 602, u'Тольятти')
            pnt.drawText(466, 1184, u'Сызрань')
            #pnt.drawText(2402, 1225, u'Самара')
            pen.setWidth(3)
            pnt.setPen(pen)
            pnt.setBrush(Qt.GlobalColor.white)
            path.addText(2402, 1225, QFont('Decorative', 32), u"Самара")
            pnt.drawPath(path)
            pnt.drawText(3566, 874, u'Отрадный')
            pnt.drawText(3700, 713, u'Кинель-Черкассы')
            pnt.drawText(2825, 1325, u'Кинель')

            #малые населенные пункты:
            pnt.setFont(QFont('Decorative', 26))
            pnt.drawText(1964, 777, u'Зольное')
            pnt.drawText(916, 459, u'Новодевичье')
            pnt.drawText(722, 844, u'Шигоны')
            pnt.drawText(753, 1220, u'Октябрьск')
            pnt.drawText(2107, 1083, u'Торновое')
            pnt.drawText(2466, 671, u'Мирный')
            pnt.drawText(2588, 440, u'Малая\nКаменка')
            pnt.drawText(2686, 337,u'Большая\nКаменка')
            pnt.drawText(3583, 1029, u'Кротовка')
            pnt.drawText(3617, 1541, u'Богатое')
            pnt.drawText(3890, 951, u'Первомайский')
            pnt.drawText(4052, 1568, u'Новоборский')

        if gm == u'Юг':
            pnt.setFont(QFont('Decorative', 32))
            #pnt.drawText(1332, 252, u'Новокуйбышевск')
            pen.setWidth(3)
            pnt.setPen(pen)
            pnt.setBrush(Qt.GlobalColor.white)
            path.addText(1332, 252, QFont('Decorative', 32), u"Новокуйбышевск")
            pnt.drawPath(path)
            pnt.drawText(1175, 414, u'Чапаевск')
            pnt.drawText(954, 365, u'Безенчук')

            #малые населенные пункты:
            pnt.setFont(QFont('Decorative', 26))
            pnt.drawText(2496, 650, u'Нефтегорск')
            pnt.drawText(2282, 494, u'Утевка')
            pnt.drawText(2575, 962, u'Алексеевка')
            pnt.drawText(2777, 451, u'Покровка')
            pnt.drawText(2934, 505, u'Алексеевка')
            pnt.drawText(2356, 1316, u'Малороссийский')
            pnt.drawText(1874, 1214, u'Большая Глушица')
            pnt.drawText(2128, 1450, u'Августовка')
            pnt.drawText(2216, 1678, u'Большая Черниговка')
            pnt.drawText(2440, 1881, u'Восточный')
            pnt.drawText(1841, 1576, u'Глушицкий')
            pnt.drawText(1910, 622, u'Подъем-Михайловка')
            pnt.drawText(1805, 499, u'Ровно-Владимировка')
            pnt.drawText(2183, 453, u'Бариновка')
            pnt.drawText(954, 962, u'Марьевка')
            pnt.drawText(1027, 1122, u'Падовка')
            pnt.drawText(1421, 1199, u'Пестравка')
            pnt.drawText(543, 878, u'Хворостянка')
            pnt.drawText(519, 737, u'Владимировка')
            pnt.drawText(632, 421, u'Натальино')
            pnt.drawText(450, 158, u'Обшаровка')
            pnt.drawText(1000, 213, u'Екатириновка')
            pnt.drawText(905, 159, u'Владимировка')
            pnt.drawText(1480, 856, u'Красноармейское')

        else:
            pass

        pnt.end()


    def set_point(self, point, coord):
        """Отобразить скважины"""

        pnt = QPainter()
        pnt.begin(self.px)
        pen = QPen(Qt.GlobalColor.red, 30)
        pnt.setPen(pen)

        if len(rects) == 0:
            rects.append([point[0], point[1]])

        x_px = point[0]
        y_px = point[1]

        x_rect = x_px
        y_rect = y_px

        #for rect in rects:
        #    if rect[0] != x_px and rect[1] != y_px:
        #прямугольники ABCD и WXYZ
        """
                Ax = rect[0]
                Ay = rect[1]
                Bx = rect[0]
                By = rect[1] - 45
                Cx = rect[0] + 450
                Cy = rect[1] - 45
                Dx = rect[0] + 450
                Dy = rect[0]
                Wx = x_px
                Wy = y_px
                Xx = x_px
                Xy = y_px - 45
                Yx = x_px + 450
                Yy = y_px - 45
                Zx = x_px + 450
                Zy = y_px
"""
            #проверка пересечений:
                #diff = intersect(Ax, Ay, Bx, By, Cx, Cy, Dx, Dy, Wx, Wy, Xx, Xy, Yx, Yy, Zx, Zy)
            #    if diff:
    #x_px = int(3000 * (y - 49.8966) / (52.5597 - 49.8967))
    #y_px = int(2761 * (54.6730 - x) / (54.6736 - 53.3070))  - 100
             #       x_rect = diff[0]
              #      y_rect = diff[1]

        pnt.setFont(QFont('Decorative', 30))


        brush = QBrush(Qt.GlobalColor.white)
        if point[2] != u'0':
            pnt.setBrush(brush)
            if point[2][0] == u'Т':

                pen = QPen(Qt.GlobalColor.blue, 2)
            else:

                pen = QPen(Qt.GlobalColor.red, 2)
            pnt.setPen(pen)

            #d_x = -170
            #d_y = 70

            #pnt.drawEllipse(x_rect - 40 + d_x, y_rect + d_y + 45 + 35, 400+ 20, -45 - 100)
            #pnt.drawRect(x_rect+10, y_rect, 500, -45)
            #pen = QPen(Qt.red, 30, Qt.SolidLine, Qt.RoundCap)

            #rect1 = QRectF(x_rect, y_rect, 200, 100)
            #pnt.drawText(rect1, point[4] + u'' + unicode(point[3]) + u', ' + point[2])
            if point[2][0] == 'Т':

                pen = QPen(Qt.GlobalColor.blue, 5)
                brush = QBrush(Qt.GlobalColor.blue)
                pnt.setBrush(brush)
               # pnt.drawRect(x_rect - 4, y_rect, 10, -80)
               # pnt.drawRect(x_rect - 4, y_rect - 80, 80, -30)
            else:
                brush = QBrush(Qt.GlobalColor.blue)
                pnt.setBrush(Qt.GlobalColor.red)
                pen = QPen(Qt.GlobalColor.red, 5)
               # pnt.drawRect(x_rect - 4, y_rect, 10, -80)
               # pnt.drawRect(x_rect - 4, y_rect - 80, 80, -30)
            pnt.setPen(pen)
            #pnt.drawText(x_rect + d_x, y_rect + d_y, point[4]) #+ u', ' + unicode(point[3]) + u', ' + point[2])
            #pnt.drawText(x_rect + d_x, y_rect+50 + d_y, unicode(point[3]) + u', ' + point[2])

            if point[2][0] == 'Т':
                pen = QPen(Qt.GlobalColor.blue, 30)
            else:
                pen = QPen(Qt.GlobalColor.red, 30)
            pnt.setPen(pen)
            pnt.drawPoint(x_px, y_px)
        pnt.end()

        if rects[0][0] != x_px and rects[0][1] != y_px:
            rects.append([x_px, y_px])

    def wheelEvent(self, event):

        self.d = event.delta()
        self.i = self.d + self.i
        factor = 1.41 ** (self.d /  480.0)
        self.scale(factor, factor)
        print ('f:' + str(factor) + ' i:' + str(self.i) + ' d:' + str(self.d))

"""
class MyLegend(QLabel):
    def __init__(self, *args):
        QLabel.__init__(self, *args)
        self.setText(u"")
        self.raise_()
        self.setFont(QFont('Decorative', 18))
        self.setStyleSheet("QLabel { background-color : #EFFED1;}");
        self.setGeometry(20, 20, 20, 20)
"""

class WellInfo(object):
    """Класс отображения информации о скважине"""

    def __init__(self, object, text):

        self.object = object

        self.info_label1 = QLabel(text, self.object)
        self.info_label1.setGeometry(20, 950, 1880, 90)
        self.info_label1.setStyleSheet("QLabel { background-color: white;}")

        self.info_label2 = QLabel(text, self.object)
        self.info_label2.setGeometry(20, 900, 1800, 90)
        self.info_label2.setStyleSheet("QLabel { background-color: white;}")

    def setText(self, text):

        self.info_label1.setText(text)
        self.info_label2.setText(text)

class MyLegend(object):
    def __init__(self, object):
        self.object = object
        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "ТРС%" AND gm = "Север"')
        self.sgm_trs_count = str(c.fetchone()[0])
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "КРС%" AND gm = "Север"')
        self.sgm_krs_count = str(c.fetchone()[0])
        conn.close()

        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "ТРС%" AND gm = "Центр"')
        self.cgm_trs_count = str(c.fetchone()[0])
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "КРС%" AND gm = "Центр"')
        self.cgm_krs_count = str(c.fetchone()[0])
        conn.close()

        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "ТРС%" AND gm = "Юг"')
        self.ugm_trs_count = str(c.fetchone()[0])
        c.execute('SELECT count(*) FROM on_map WHERE brigade LIKE "КРС%" AND gm = "Юг"')
        self.ugm_krs_count = str(c.fetchone()[0])
        conn.close()
                # ------------------------------------------
        self.sgm_lb1 = QLabel(u"", self.object)
        self.sgm_lb1.setStyleSheet("QLabel { background-color : #EFFED1;}")
        self.sgm_lb1.setGeometry(40, 40, 35, 35)
        self.sgm_lb11 = QLabel(u"ЦДНГ-1", self.object)
        self.sgm_lb11.setFont(QFont('Decorative', 16))
        self.sgm_lb11.setGeometry(85, 40, 80, 35)

        self.sgm_lb2 = QLabel(u"", self.object)
        self.sgm_lb2.setStyleSheet("QLabel { background-color : #CEF0FF;}")
        self.sgm_lb2.setGeometry(40, 78, 35, 35)
        self.sgm_lb22 = QLabel(u"ЦДНГ-7", self.object)
        self.sgm_lb22.setFont(QFont('Decorative', 16))
        self.sgm_lb22.setGeometry(85, 78, 80, 35)

        self.sgm_lb3 = QLabel(u"", self.object)
        self.sgm_lb3.setStyleSheet("QLabel { background-color : #FFDBBC;}")
        self.sgm_lb3.setGeometry(40, 116, 35, 35)
        self.sgm_lb33 = QLabel(u"ЦДНГ-2", self.object)
        self.sgm_lb33.setFont(QFont('Decorative', 16))
        self.sgm_lb33.setGeometry(85, 116, 80, 35)

        self.sgm_lb4 = QLabel(u"", self.object)
        self.sgm_lb4.setStyleSheet("QLabel { background-image : url(flag-blue.png);}")
        self.sgm_lb4.setGeometry(40, 116 + 38, 35, 35)
        self.sgm_lb44 = QLabel(u"ТРС" + u": " + self.sgm_trs_count, self.object)
        self.sgm_lb44.setFont(QFont('Decorative', 16))
        self.sgm_lb44.setGeometry(85, 116 + 38, 80, 35)

        self.sgm_lb5 = QLabel(u"", self.object)
        self.sgm_lb5.setStyleSheet("QLabel { background-image : url(flag-red.png);}")
        self.sgm_lb5.setGeometry(40, 116 + 38*2, 35, 35)
        self.sgm_lb55 = QLabel(u"КРС" + u": " + self.sgm_krs_count, self.object)
        self.sgm_lb55.setFont(QFont('Decorative', 16))
        self.sgm_lb55.setGeometry(85, 116 + 38*2, 80, 35)

        self.sgm_lb6 = QLabel(u"", self.object)
        self.sgm_lb6.setStyleSheet("QLabel { background-image : url(road.png);}")
        self.sgm_lb6.setGeometry(40, 116 + 38*3, 35, 35)
        self.sgm_lb66 = QLabel(u"Асфальтовая\nдорога", self.object)
        self.sgm_lb66.setFont(QFont('Decorative', 12))
        self.sgm_lb66.setGeometry(85, 116 + 38*3, 140, 40)

        self.cgm_lb1 = QLabel(u"", self.object)
        self.cgm_lb1.setStyleSheet("QLabel { background-color : #FDDCCB;}")
        self.cgm_lb1.setGeometry(40, 40, 35, 35)
        self.cgm_lb11 = QLabel(u"ЦДНГ-3", self.object)
        self.cgm_lb11.setFont(QFont('Decorative', 16))
        self.cgm_lb11.setGeometry(85, 40, 80, 35)

        self.cgm_lb2 = QLabel(u"", self.object)
        self.cgm_lb2.setStyleSheet("QLabel { background-color : #EFFED1;}")
        self.cgm_lb2.setGeometry(40, 78, 35, 35)
        self.cgm_lb22 = QLabel(u"ЦДНГ-4", self.object)
        self.cgm_lb22.setFont(QFont('Decorative', 16))
        self.cgm_lb22.setGeometry(85, 78, 80, 35)

        self.cgm_lb3 = QLabel(u"", self.object)
        self.cgm_lb3.setStyleSheet("QLabel { background-image : url(flag-blue.png);}")
        self.cgm_lb3.setGeometry(40, 116, 35, 35)
        self.cgm_lb33 = QLabel(u"ТРС" + u": " + self.cgm_trs_count, self.object)
        self.cgm_lb33.setFont(QFont('Decorative', 16))
        self.cgm_lb33.setGeometry(85, 116, 80, 35)

        self.cgm_lb4 = QLabel(u"", self.object)
        self.cgm_lb4.setStyleSheet("QLabel { background-image : url(flag-red.png);}")
        self.cgm_lb4.setGeometry(40, 116 + 38, 35, 35)
        self.cgm_lb44 = QLabel(u"КРС" + u": " + self.cgm_krs_count, self.object)
        self.cgm_lb44.setFont(QFont('Decorative', 16))
        self.cgm_lb44.setGeometry(85, 116 + 38, 80, 35)

        self.cgm_lb5 = QLabel(u"", self.object)
        self.cgm_lb5.setStyleSheet("QLabel { background-image : url(road.png);}")
        self.cgm_lb5.setGeometry(40, 116 + 38*2, 35, 35)
        self.cgm_lb55 = QLabel(u"Асфальтовая\nдорога", self.object)
        self.cgm_lb55.setFont(QFont('Decorative', 12))
        self.cgm_lb55.setGeometry(85, 116 + 38*2, 140, 40)

        self.ugm_lb1 = QLabel(u"", self.object)
        self.ugm_lb1.setStyleSheet("QLabel { background-color : #D8FFF4;}")
        self.ugm_lb1.setGeometry(40, 40, 35, 35)
        self.ugm_lb11 = QLabel(u"ЦДНГ-5", self.object)
        self.ugm_lb11.setFont(QFont('Decorative', 16))
        self.ugm_lb11.setGeometry(85, 40, 80, 35)

        self.ugm_lb2 = QLabel(u"", self.object)
        self.ugm_lb2.setStyleSheet("QLabel { background-color : #E8E0FE;}")
        self.ugm_lb2.setGeometry(40, 78, 35, 35)
        self.ugm_lb22 = QLabel(u"ЦДНГ-6", self.object)
        self.ugm_lb22.setFont(QFont('Decorative', 16))
        self.ugm_lb22.setGeometry(85, 78, 80, 35)

        self.ugm_lb3 = QLabel(u"", self.object)
        self.ugm_lb3.setStyleSheet("QLabel { background-color : #FEE1C0;}")
        self.ugm_lb3.setGeometry(40, 116, 35, 35)
        self.ugm_lb33 = QLabel(u"ЦДНГ-9", self.object)
        self.ugm_lb33.setFont(QFont('Decorative', 16))
        self.ugm_lb33.setGeometry(85, 116, 80, 35)

        self.ugm_lb4 = QLabel(u"", self.object)
        self.ugm_lb4.setStyleSheet("QLabel { background-color : #E4FCE0;}")
        self.ugm_lb4.setGeometry(40, 116 + 38, 35, 35)
        self.ugm_lb44 = QLabel(u"ЦДНГ-10", self.object)
        self.ugm_lb44.setFont(QFont('Decorative', 16))
        self.ugm_lb44.setGeometry(85, 116 + 38, 85, 35)

        self.ugm_lb5 = QLabel(u"", self.object)
        self.ugm_lb5.setStyleSheet("QLabel { background-image : url(flag-blue.png);}")
        self.ugm_lb5.setGeometry(40, 116 + 38*2, 35, 35)
        self.ugm_lb55 = QLabel(u"ТРС" + u": " + self.ugm_trs_count, self.object)
        self.ugm_lb55.setFont(QFont('Decorative', 16))
        self.ugm_lb55.setGeometry(85, 116 + 38*2, 80, 35)

        self.ugm_lb6 = QLabel(u"", self.object)
        self.ugm_lb6.setStyleSheet("QLabel { background-image : url(flag-red.png);}")
        self.ugm_lb6.setGeometry(40, 116 + 38*3, 35, 35)
        self.ugm_lb66 = QLabel(u"КРС" + u": " + self.ugm_krs_count, self.object)
        self.ugm_lb66.setFont(QFont('Decorative', 16))
        self.ugm_lb66.setGeometry(85, 116 + 38*3, 80, 35)

        self.ugm_lb7 = QLabel(u"", self.object)
        self.ugm_lb7.setStyleSheet("QLabel { background-image : url(road.png);}")
        self.ugm_lb7.setGeometry(40, 116 + 38*4, 35, 35)
        self.ugm_lb77 = QLabel(u"Асфальтовая\nдорога", self.object)
        self.ugm_lb77.setFont(QFont('Decorative', 12))
        self.ugm_lb77.setGeometry(85, 116 + 38*4, 140, 40)

        self.check_gm()

    def check_gm(self):
        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('SELECT gm FROM current_map')
        gm = c.fetchone()[0]
        conn.close()

        if gm == 'Север':
            self.sgm_lb1.show()
            self.sgm_lb11.show()

            self.sgm_lb2.show()
            self.sgm_lb22.show()

            self.sgm_lb3.show()
            self.sgm_lb33.show()

            self.sgm_lb4.show()
            self.sgm_lb44.show()

            self.sgm_lb5.show()
            self.sgm_lb55.show()

            self.sgm_lb6.show()
            self.sgm_lb66.show()

            self.cgm_lb1.hide()
            self.cgm_lb11.hide()

            self.cgm_lb2.hide()
            self.cgm_lb22.hide()

            self.cgm_lb3.hide()
            self.cgm_lb33.hide()

            self.cgm_lb4.hide()
            self.cgm_lb44.hide()

            self.cgm_lb5.hide()
            self.cgm_lb55.hide()

            self.ugm_lb1.hide()
            self.ugm_lb11.hide()

            self.ugm_lb2.hide()
            self.ugm_lb22.hide()

            self.ugm_lb3.hide()
            self.ugm_lb33.hide()

            self.ugm_lb4.hide()
            self.ugm_lb44.hide()

            self.ugm_lb5.hide()
            self.ugm_lb55.hide()

            self.ugm_lb6.hide()
            self.ugm_lb66.hide()

            self.ugm_lb7.hide()
            self.ugm_lb77.hide()

        if gm == 'Центр':
            self.sgm_lb1.hide()
            self.sgm_lb11.hide()

            self.sgm_lb2.hide()
            self.sgm_lb22.hide()

            self.sgm_lb3.hide()
            self.sgm_lb33.hide()

            self.sgm_lb4.hide()
            self.sgm_lb44.hide()

            self.sgm_lb5.hide()
            self.sgm_lb55.hide()

            self.sgm_lb6.hide()
            self.sgm_lb66.hide()

            self.cgm_lb1.show()
            self.cgm_lb11.show()

            self.cgm_lb2.show()
            self.cgm_lb22.show()

            self.cgm_lb3.show()
            self.cgm_lb33.show()

            self.cgm_lb4.show()
            self.cgm_lb44.show()

            self.cgm_lb5.show()
            self.cgm_lb55.show()

            self.ugm_lb1.hide()
            self.ugm_lb11.hide()

            self.ugm_lb2.hide()
            self.ugm_lb22.hide()

            self.ugm_lb3.hide()
            self.ugm_lb33.hide()

            self.ugm_lb4.hide()
            self.ugm_lb44.hide()

            self.ugm_lb5.hide()
            self.ugm_lb55.hide()

            self.ugm_lb6.hide()
            self.ugm_lb66.hide()

            self.ugm_lb7.hide()
            self.ugm_lb77.hide()

        if gm == 'Юг':
            self.sgm_lb1.hide()
            self.sgm_lb11.hide()

            self.sgm_lb2.hide()
            self.sgm_lb22.hide()

            self.sgm_lb3.hide()
            self.sgm_lb33.hide()

            self.sgm_lb4.hide()
            self.sgm_lb44.hide()

            self.sgm_lb5.hide()
            self.sgm_lb55.hide()

            self.sgm_lb6.hide()
            self.sgm_lb66.hide()

            self.cgm_lb1.hide()
            self.cgm_lb11.hide()

            self.cgm_lb2.hide()
            self.cgm_lb22.hide()

            self.cgm_lb3.hide()
            self.cgm_lb33.hide()

            self.cgm_lb4.hide()
            self.cgm_lb44.hide()

            self.cgm_lb5.hide()
            self.cgm_lb55.hide()

            self.ugm_lb1.show()
            self.ugm_lb11.show()

            self.ugm_lb2.show()
            self.ugm_lb22.show()

            self.ugm_lb3.show()
            self.ugm_lb33.show()

            self.ugm_lb4.show()
            self.ugm_lb44.show()

            self.ugm_lb5.show()
            self.ugm_lb55.show()

            self.ugm_lb6.show()
            self.ugm_lb66.show()

            self.ugm_lb7.show()
            self.ugm_lb77.show()


class ApplicationWindow(QMainWindow):
    """Класс определения окна приложения"""

    def __init__(self):
        QMainWindow.__init__(self)
        #self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(u"Карта")
        self.setWindowIcon(QIcon('map_app.png'))
        self.main_widget = QWidget(self)
        self.l = QGridLayout(self.main_widget)
        self.l.setSpacing(0)

        self.map1 = MyView()

        self.l.addWidget(self.map1)
        #self.main_widget.setFocus()
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint | Qt.FramelessWindowHint)
        self.setCentralWidget(self.main_widget)


        self.lb1 = MyLegend(self)

        timer2 = QTimer(self)
        timer2.timeout.connect(self.set_window_status)
        #self.connect(timer2, PyQt4.QtCore.SIGNAL("timeout()"), self.set_window_status)
        timer2.start(3000)

        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.showMinimized)
        #self.connect(self.timer3, PyQt4.QtCore.SIGNAL("timeout()"), self.showMinimized)
        self.timer3.stop()

        self.timer4 = QTimer(self)
        self.timer4.timeout.connect(self.showMaximized)
        #self.connect(self.timer4, PyQt4.QtCore.SIGNAL("timeout()"), self.showMaximized)
        self.timer4.stop()

        timer5 = QTimer(self)
        timer5.timeout.connect(self.lb1.check_gm)
        #self.connect(timer5, PyQt4.QtCore.SIGNAL("timeout()"), self.lb1.check_gm)
        timer5.start(6000)

        #timer2 = QTimer(self)
        #timer2.timeout.connect(self.map1.px.change_map)
        #self.connect(timer2, PyQt4.QtCore.SIGNAL("timeout()"), self.map1.px.change_map)
        #timer2.start(3000)

    def set_window_status(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT on_top FROM window_status')
            status = str(c.fetchone()[0])

        #if status == '0':
        #    self.timer3.start(3000)
        #    self.timer4.stop()
        #else:
        #    self.timer3.stop()
        #    self.timer4.start(3000)


    # MAIN
qApp = QApplication(sys.argv)
aw = ApplicationWindow()
aw.showMaximized()
#print(aw.windowState() == Qt.WindowMaximized)
sys.exit(qApp.exec())
qApp.exec()