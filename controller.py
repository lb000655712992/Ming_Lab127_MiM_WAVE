import cv2
import json
import time
import threading
import datetime
import matplotlib.pyplot as plt
import numpy as np

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QImage, QPixmap, QIcon
from numpy import arange
from UI import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import cm, colors
from math import radians


class MyFigureCanvas_3D(FigureCanvas):
    '''
    通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键
    '''

    def __init__(self, parent=None, width=1, height=1, dpi=100):
        # 创建一个Figure
        fig = plt.Figure(figsize=(width, height), dpi=dpi,
                         tight_layout=True)  # tight_layout: 用于去除画图时两边的空白

        FigureCanvas.__init__(self, fig)  # 初始化父类
        self.setParent(parent)

        self.axes = fig.add_subplot(
            111, projection='3d'
        )  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        self.axes.spines['top'].set_visible(False)  # 去掉上面的横线
        self.axes.spines['right'].set_visible(False)

class MyFigureCanvas_2D(FigureCanvas):
    '''
    通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键
    '''

    def __init__(self, parent=None, width=1, height=1, dpi=100,xlim=(0, 2500),ylim=(-2, 2)):
        # 创建一个Figure
        fig = plt.Figure(figsize=(width, height), dpi=dpi,
                         tight_layout=True)  # tight_layout: 用于去除画图时两边的空白

        FigureCanvas.__init__(self, fig)  # 初始化父类
        self.setParent(parent)

        self.axes = fig.add_subplot(111)  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        self.axes.spines['top'].set_visible(False)  # 去掉上面的横线
        self.axes.spines['right'].set_visible(False)
        #self.axes.set_xlim(xlim)
        #self.axes.set_ylim(ylim)


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        title = "MiM Wave CATR test system"
        self.setWindowTitle(title)
        self.setup_widget()
        self.setup_default_value()
        self.set_page_widget()

    def setup_widget(self):
        self.buttongroup = QtWidgets.QButtonGroup(self)
        self.buttongroup.addButton(self.ui.radioButton_2D, 1)
        self.buttongroup.addButton(self.ui.radioButton_3D, 2)
        self.buttongroup2 = QtWidgets.QButtonGroup(self)
        self.buttongroup2.addButton(self.ui.radioButton_continue, 1)
        self.buttongroup2.addButton(self.ui.radioButton_step, 2)
        self.img_path = 'P1.png'
        self.display_img()
        self.ui.toolButton_next.clicked.connect(self.next)
        self.ui.toolButton_back.clicked.connect(self.back)
        self.ui.toolButton_reset.clicked.connect(self.reset)
        self.ui.toolButton_start.clicked.connect(self.start)
        self.ui.toolButton_pause.clicked.connect(self.pause)
        for i in arange(20, 30.5, 0.5):
            self.ui.comboBox_F.addItem(str(i))
            self.ui.comboBox_F_2.addItem(str(i))
        for i in range(-20, 20, 5):
            self.ui.comboBox_stick_l.addItem(str(i))
            self.ui.comboBox_stick_u.addItem(str(i))
        self.ui.textBrowser.ensureCursorVisible()  # 游标可用
        self.cursor = self.ui.textBrowser.textCursor()  # 设置游标
        self.graphic_scene_3D = QtWidgets.QGraphicsScene()
        self.graphic_scene_2D = QtWidgets.QGraphicsScene()
        self.ui.tabWidget.currentChanged['int'].connect(self.resize_graph)

    def setup_default_value(self):
        self.left_style_1 = "color: rgb(43, 87, 154);background-color: rgb(243, 243, 243);border:10px solid rgb(241, 241, 241)"
        self.left_style_0 = "color: rgb(255, 255, 255);\nborder:10px solid rgb(43, 87, 154);"
        self.page_list = ["test_panel", "setting", "running", "view"]
        self.parmeter = {}
        self.page_now = "test_panel"
        self.ui.stackedWidget.setCurrentIndex(
            self.page_list.index(self.page_now))
        self.ui.radioButton_2D.setChecked(True)
        self.ui.radioButton_step.setChecked(True)
        self.ui.checkBox_Rawdata.setChecked(True)
        self.ui.toolButton_test_panel.setEnabled(True)
        self.ui.toolButton_setting.setEnabled(False)
        self.ui.toolButton_running.setEnabled(False)
        self.ui.toolButton_view.setEnabled(False)
        self.ui.comboBox_stick_u.setCurrentIndex(7)
        # self.ui.tabWidget.setTabVisible(1,False)

    def display_img(self):
        self.img = cv2.imread(self.img_path)
        height, width, channel = self.img.shape
        bytesPerline = 3 * width
        self.qimg = QImage(self.img, width, height,
                           bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ui.label_display.setPixmap(QPixmap.fromImage(self.qimg))

    def next(self):
        self.get_page_parmeter()
        self.page_now = self.page_list[self.page_list.index(self.page_now)+1]
        self.ui.stackedWidget.setCurrentIndex(
            self.page_list.index(self.page_now))
        print(self.page_now)
        print(self.parmeter)
        self.set_page_widget()

    def back(self):
        self.get_page_parmeter()
        self.page_now = self.page_list[self.page_list.index(self.page_now)-1]
        self.ui.stackedWidget.setCurrentIndex(
            self.page_list.index(self.page_now))
        print(self.page_now)
        self.set_page_widget()

    def reset(self):
        self.setup_default_value()
        self.set_page_widget()

    def get_page_parmeter(self):
        if self.page_now == "test_panel":
            self.parmeter["test_panel"] = {}
            self.parmeter["test_panel"]["passive_OTA"] = {}
            self.parmeter["test_panel"]["test_parmeter"] = {}
            self.parmeter["test_panel"]["test_parmeter"]["theta_angle"] = {}
            self.parmeter["test_panel"]["test_parmeter"]["phi_angle"] = {}
            self.parmeter["test_panel"]["test_parmeter"]["2D_plot_stick"] = {}
            self.parmeter["test_panel"]["test_parmeter"]["output"] = []
            for p, v in {
                    self.ui.radioButton_2D: "2D",
                    self.ui.radioButton_3D: "3D"}.items():
                if p.isChecked():
                    self.parmeter["test_panel"]["passive_OTA"]["passive_type"] = v
                    break
            for p, v in {
                    self.ui.radioButton_step: "Step",
                    self.ui.radioButton_continue: "Continue"}.items():
                if p.isChecked():
                    self.parmeter["test_panel"]["passive_OTA"]["rotation_mode"] = v
                    break
            self.parmeter["test_panel"]["test_parmeter"]["theta_angle"]["start_angle"] = self.ui.lineEdit_start_T.text()
            self.parmeter["test_panel"]["test_parmeter"]["theta_angle"]["stop_angle"] = self.ui.lineEdit_stop_T.text()
            self.parmeter["test_panel"]["test_parmeter"]["theta_angle"]["step_angle"] = self.ui.lineEdit_step_T.text()
            self.parmeter["test_panel"]["test_parmeter"]["phi_angle"]["start_angle"] = self.ui.lineEdit_start_P.text()
            self.parmeter["test_panel"]["test_parmeter"]["phi_angle"]["stop_angle"] = self.ui.lineEdit_stop_P.text()
            self.parmeter["test_panel"]["test_parmeter"]["phi_angle"]["step_angle"] = self.ui.lineEdit_step_P.text()
            self.parmeter["test_panel"]["test_parmeter"]["frequencies"] = self.ui.comboBox_F.currentText()
            self.parmeter["test_panel"]["test_parmeter"]["2D_plot_stick"]["upper"] = self.ui.comboBox_stick_u.currentText()
            self.parmeter["test_panel"]["test_parmeter"]["2D_plot_stick"]["lower"] = self.ui.comboBox_stick_l.currentText()
            if self.ui.checkBox_Rawdata.isChecked():
                self.parmeter["test_panel"]["test_parmeter"]["output"].append(
                    "rawdata")
            if self.ui.checkBox_2D.isChecked():
                self.parmeter["test_panel"]["test_parmeter"]["output"].append(
                    "2D")
            if self.ui.checkBox_3D.isChecked():
                self.parmeter["test_panel"]["test_parmeter"]["output"].append(
                    "3D")
        elif self.page_now == "setting":
            self.parmeter["setting"] = {}
            self.parmeter["setting"]["re-build"] = {}
            self.parmeter["setting"]["file"] = self.ui.lineEdit_file_2.text()
            self.parmeter["setting"]["re-build"]["theta_angle"] = {}
            self.parmeter["setting"]["re-build"]["phi_angle"] = {}
            self.parmeter["setting"]["re-build"]["theta_angle"]["start_angle"] = self.ui.lineEdit_start_T2.text()
            self.parmeter["setting"]["re-build"]["theta_angle"]["stop_angle"] = self.ui.lineEdit_stop_T2.text()
            self.parmeter["setting"]["re-build"]["theta_angle"]["step_angle"] = self.ui.lineEdit_step_T2.text()
            self.parmeter["setting"]["re-build"]["phi_angle"]["start_angle"] = self.ui.lineEdit_start_P2.text()
            self.parmeter["setting"]["re-build"]["phi_angle"]["stop_angle"] = self.ui.lineEdit_stop_P2.text()
            self.parmeter["setting"]["re-build"]["phi_angle"]["step_angle"] = self.ui.lineEdit_step_P2.text()
            self.parmeter["setting"]["re-build"]["frequencies"] = self.ui.comboBox_F_2.currentText()
        elif self.page_now == "running":
            print("running")
        elif self.page_now == "view":
            print("view")

    def _set_page_widget(self, setting: list):
        self.ui.toolButton_test_panel.setStyleSheet(setting[0])
        self.ui.toolButton_setting.setStyleSheet(setting[1])
        self.ui.toolButton_running.setStyleSheet(setting[2])
        self.ui.toolButton_view.setStyleSheet(setting[3])
        self.ui.toolButton_next.setEnabled(setting[4])
        self.ui.toolButton_back.setEnabled(setting[5])
        self.ui.toolButton_reset.setEnabled(setting[6])
        self.ui.toolButton_test_panel.setEnabled(setting[7])
        self.ui.toolButton_setting.setEnabled(setting[8])
        self.ui.toolButton_running.setEnabled(setting[9])
        self.ui.toolButton_view.setEnabled(setting[10])

    def setup_icon(self):
        icon = QIcon()
        # toolButton_test_panel
        icon_path = "./image/equalizer.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_test_panel.setIcon(icon)
        # toolButton_setting
        icon_path = "./image/settings.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_setting.setIcon(icon)
        # toolButton_running
        icon_path = "./image/jogging.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_running.setIcon(icon)
        # toolButton_view
        icon_path = "./image/research.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_view.setIcon(icon)
        # toolButton_next
        icon_path = "./image/next-button2.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_next.setIcon(icon)
        # toolButton_back
        icon_path = "./image/back2.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_back.setIcon(icon)
        # toolButton_reset
        icon_path = "./image/reset2.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_reset.setIcon(icon)
        # toolButton_start
        icon_path = "./image/play-button.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_start.setIcon(icon)
        # toolButton_pause
        icon_path = "./image/pause.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_pause.setIcon(icon)
        # toolButton_stop
        icon_path = "./image/stop.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_stop.setIcon(icon)
        # toolButton_setting_2
        icon_path = "./image/gear.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_setting_2.setIcon(icon)

        # toolButton_setting_3
        icon_path = "./image/gear.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_setting_3.setIcon(icon)
        # toolButton_save
        icon_path = "./image/diskette.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_save.setIcon(icon)

        # toolButton_setting_5
        icon_path = "./image/gear.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_setting_5.setIcon(icon)
        # toolButton_save_3
        icon_path = "./image/diskette.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_save_3.setIcon(icon)

        # toolButton_setting_4
        icon_path = "./image/gear.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_setting_4.setIcon(icon)
        # toolButton_save_2
        icon_path = "./image/diskette.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_save_2.setIcon(icon)
        
        # toolButton_file
        icon_path = "./image/files.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_file.setIcon(icon)
        # toolButton_help
        icon_path = "./image/question.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_help.setIcon(icon)
        # toolButton_file
        icon_path = "./image/question.png"
        icon.addPixmap(QPixmap(icon_path))
        self.ui.toolButton_help_2.setIcon(icon)

    def set_page_widget(self):
        self.setup_icon()
        ls1 = self.left_style_1
        ls0 = self.left_style_0
        self.flag_pause = False
        if self.page_now == "test_panel":
            self._set_page_widget([ls1, ls0, ls0, ls0, 1, 0, 0, 1, 0, 0, 0])
        elif self.page_now == "setting":
            self._set_page_widget([ls0, ls1, ls0, ls0, 1, 1, 1, 1, 1, 0, 0])
        elif self.page_now == "running":
            self._set_page_widget([ls0, ls0, ls1, ls0, 0, 1, 1, 1, 1, 1, 0])
            self.test_bar([1, 0, 0, 0, 1, 1])
            self.flag_pause = False
            self.ui.progressBar.setValue(0)
            self.ui.textBrowser.clear()
            self.ui.textBrowser.append(json.dumps(self.parmeter, indent=4))
        elif self.page_now == "view":
            self._set_page_widget([ls0, ls0, ls0, ls1, 0, 1, 1, 1, 1, 1, 1])

    def start(self):
        print("start test")
        self.test_bar([0, 1, 1, 0, 0, 0])
        if not self.flag_pause:
            t = threading.Thread(target=self.test_process)
            t.start()
            self.draw_3D()
            self.draw_2D()
        self.flag_pause = False

    def pause(self):
        print("pause")
        self.flag_pause = True
        self.test_bar([1, 0, 1, 0, 0, 0])

    def test_bar(self, partameter):
        self.ui.toolButton_start.setEnabled(partameter[0])
        self.ui.toolButton_pause.setEnabled(partameter[1])
        self.ui.toolButton_stop.setEnabled(partameter[2])
        self.ui.toolButton_next.setEnabled(partameter[3])
        self.ui.toolButton_back.setEnabled(partameter[4])
        self.ui.toolButton_reset.setEnabled(partameter[5])

    def test_process(self):
        '''
        for i in range(0,101):
            while self.flag_pause:
                print("pauseing")
                time.sleep(1)
            self.ui.progressBar.setValue(i)
            textBrowser_b = datetime.datetime.now().strftime("[%Y/%m/%d %H:%M:%S] ")+str(i)+"%"
            self.ui.textBrowser.append(textBrowser_b)
            pos = len(self.ui.textBrowser.toPlainText())  # 获取文本尾部的位置
            self.cursor.setPosition(pos)  # 游标位置设置为尾部
            self.ui.textBrowser.setTextCursor(self.cursor)  # 滚动到游标位置
            time.sleep(0.1)
        '''
        self.test_bar([0, 0, 0, 1, 1, 1])
        self.ui.toolButton_next.setEnabled(1)

    def draw_3D(self):
        default_size = 100
        w = 750
        h = 750
        print('3d',self.ui.graphicsView_3D.width(),
              self.ui.graphicsView_3D.height())
        self.gv_visual_data_content_3D = MyFigureCanvas_3D(
            width = w / default_size,
            height = h / default_size)  # 實例化一個FigureCanvas
        self.graphic_scene_3D = QtWidgets.QGraphicsScene()
        self.graphic_scene_3D.addWidget(self.gv_visual_data_content_3D)
        self.ui.graphicsView_3D.setScene(self.graphic_scene_3D)
        self.ui.graphicsView_3D.show()
        self.gv_visual_data_content_3D.axes.clear()
        u = np.linspace(0, np.pi, 360)
        v = np.linspace(0, 2*np.pi, 180)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        b = []
        pp = np.concatenate((np.linspace(0, 1, 180), np.linspace(1, 0, 180)))
        '''
        for x1 in range(len(x)):
            for x2 in range(len(x[x1])):
                # print(pp[x1])
                x[x1][x2] = x[x1][x2]*pp[x1]
                y[x1][x2] = y[x1][x2]*pp[x1]
                z[x1][x2] = z[x1][x2]*pp[x1]
        '''
        for x1 in range(len(x)):
            bb = []
            for x2 in range(len(x[x1])):
                d = float(
                    int(((x[x1][x2]**2+y[x1][x2]**2+z[x1][x2]**2)**0.5)*100))/100
                bb.append(np.array([d]))
            b.append(bb)
        colorfunction = np.array(b)
        # print(colorfunction)
        norm = colors.Normalize(vmin=np.min(
            colorfunction), vmax=np.max(colorfunction), clip=False)

        #gv_visual_data_content_3D.axes.plot_surface(x, y, z,norm=norm,cmap = 'RdYlBu',facecolors=colorfunction)
        self.gv_visual_data_content_3D.axes.plot_surface(
            x, y, z, norm=norm, facecolors=cm.seismic(colorfunction))
        self.gv_visual_data_content_3D.axes.set_title('3D plot')
        self.ui.graphicsView_3D.fitInView(self.graphic_scene_3D.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.gv_visual_data_content_3D.draw()  # 刷新画布显示图片，否则不刷新显示
    
    def draw_2D(self):
        default_size = 100
        w = 750
        h = 750
        print('2d',self.ui.graphicsView_2D.width(),
              self.ui.graphicsView_2D.height())
        self.gv_visual_data_content_2D = MyFigureCanvas_2D(
            width = w / default_size,
            height = h / default_size)
        self.graphic_scene_2D = QtWidgets.QGraphicsScene()
        self.graphic_scene_2D.addWidget(self.gv_visual_data_content_2D)
        self.ui.graphicsView_2D.setScene(self.graphic_scene_2D)
        self.ui.graphicsView_2D.show()
        upper = int(self.parmeter["test_panel"]["test_parmeter"]["2D_plot_stick"]["upper"])
        lower = int(self.parmeter["test_panel"]["test_parmeter"]["2D_plot_stick"]["lower"])
        data = [
            -3.55, -11.29, -7.75, -4.52, -2.96, 1.28, 1.91, 2.81, 0.48, -1.83,
            -4.14, -10.42, -12.59, -9.19, -6.55, -5.12, -2.24, -0.19, -0.64,
            2.13, 2.16, 1.1, -3.23, -3.47, -3.55
        ]
        tick = 15
        theta_data = []
        theta_data_radians = list(range(0, 360 + tick, tick))
        for r in range(len(theta_data_radians)):
            theta_data_radians[r] = theta_data_radians[r]%360
        #print(theta_data)
        for i in range(len(theta_data_radians)):
            theta_data.append(radians(theta_data_radians[i]))
            self.gv_visual_data_content_2D.axes.clear()  # 清除之前的繪圖
        theta = np.linspace(0, 2 * np.pi, 100)  # 背景的圓角度
        #theta_data = np.linspace(0, 2 * np.pi, len(data))      # 資料的圓角度
        radius = abs(upper) + abs(lower)  # 計算背景圓半徑長度
        # XY軸刻度
        axis1 = list(range(upper, lower, -5))
        axis2 = list(range(lower, upper + 5, 5))
        axis = axis1 + axis2

        # 依據不同角度畫出data的強度值
        dx, dy = [], []
        for i in range(len(theta_data)):
            dx.append((abs(lower) + data[i]) * np.cos(theta_data[i]))
            dy.append((abs(lower) + data[i]) * np.sin(theta_data[i]))
        self.gv_visual_data_content_2D.axes.plot(dx, dy, color='r')

        # 依據data的角度刻度畫出同心圓內刻度及角度
        for r in range(len(theta_data)):
            bx = [0, radius * np.cos(theta_data[r])]
            by = [0, radius * np.sin(theta_data[r])]
            self.gv_visual_data_content_2D.axes.plot(bx,
                                                     by,
                                                     color='g',
                                                     alpha=.3)
            text_x = radius * np.cos(theta_data[r])
            text_y = radius * np.sin(theta_data[r])
            length_font = 1.5
            self.gv_visual_data_content_2D.axes.text(text_x+np.cos(theta_data[r])*length_font,
                                                     text_y+np.sin(theta_data[r])*length_font-1.25,
                                                     str(theta_data_radians[r]),
                                                     ha='center',
                                                     va='bottom',
                                                     fontsize=8,
                                                     rotation=0)

        # 依據data的角度刻度畫出同心圓
        for i in range(0, radius + 5, 5):
            x = i * np.cos(theta)
            y = i * np.sin(theta)
            if i == abs(lower):
                self.gv_visual_data_content_2D.axes.plot(x, y, color='k', alpha=.3)
            else:
                self.gv_visual_data_content_2D.axes.plot(x, y, color='g', alpha=.3)
        set_ticks_list = range(-radius, radius + 5, 5)
        self.gv_visual_data_content_2D.axes.set_xticks(set_ticks_list)
        self.gv_visual_data_content_2D.axes.set_yticks(set_ticks_list)
        self.gv_visual_data_content_2D.axes.set_xticklabels(axis)
        self.gv_visual_data_content_2D.axes.set_yticklabels(axis)

        self.gv_visual_data_content_2D.axes.set_title('2D plot')
        self.gv_visual_data_content_2D.draw()
        self.ui.graphicsView_2D.fitInView(self.graphic_scene_2D.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        self.resize_graph()
    
    def resize_graph(self):
        r = self.graphic_scene_3D.sceneRect()
        r2 = self.graphic_scene_2D.sceneRect()
        self.ui.graphicsView_3D.fitInView(r, QtCore.Qt.KeepAspectRatio)
        self.ui.graphicsView_2D.fitInView(r2, QtCore.Qt.KeepAspectRatio)
