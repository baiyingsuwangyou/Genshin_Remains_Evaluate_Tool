# -*- coding: utf-8 -*-
import sys
import pyautogui
import cv2
import numpy as np
import easyocr
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import json

from myutils import utils


class ScreenMonitor(QThread):
    strsin = pyqtSignal(str)
    flag = True

    def __init__(self):
        super(ScreenMonitor, self).__init__()
        self.is_continue = True

    def run(self):
        self.Run(True)

    def Run(self, is_circle=False):
        """
        监控屏幕并处理图像
        :param is_circle:bool
        :return:None
        """

        while self.flag:
            if not is_circle:
                self.flag = False
            if self.is_continue:

                img = pyautogui.screenshot()  # 屏幕截屏
                img = np.array(img)  # 转化为数组
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # 转通道

                img_need = self._img_needed_acquire(img)
                # print(img_need)
                if len(img_need) == 0:
                    self.strsin.emit('')
                    cv2.waitKey(100)
                    self.strsin.emit('未识别到圣遗物图像，请重试')
                    cv2.waitKey(1000)
                    continue
                # cv2.imshow('1', img_need)  # 显示图像
                # cv2.waitKey()

                img_place, img_attr, img_level, img_attrs = self._img_separated(img_need)
                _place, _main_attr, _level, *_attrs, _name = self._img_text_recognition(img_place, img_attr, img_level,
                                                                                        img_attrs)
                _name = _name[:-1]
                te = utils.check_and_specialize(_name, _level, _place, _main_attr, _attrs)

                if not te:
                    self.strsin.emit('')
                    cv2.waitKey(100)
                    self.strsin.emit('等级不为0级！')
                    cv2.waitKey(1000)
                    continue
                if len(te) == 1:
                    self.strsin.emit('')
                    cv2.waitKey(100)
                    self.strsin.emit(te[0])
                    cv2.waitKey(1000)
                    continue
                te = utils.check_statify(*te)
                self.strsin.emit('')
                cv2.waitKey(100)
                self.strsin.emit(te)

                cv2.waitKey(1000)
            else:
                break

    def _img_needed_acquire(self, img):
        """
        找到需要的部分并取出图像
        :param img: array(BGR)
        :return: array(BGR) or None
        """

        # imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转灰度
        # imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 0)  # 高斯模糊
        imgCanny = cv2.Canny(img, 50, 100)  # Canny算子边缘检测
        # cv2.imshow('1', imgCanny)
        # cv2.waitKey()
        lines = cv2.HoughLinesP(imgCanny, 1, np.pi / 180, 100, minLineLength=300, maxLineGap=10)  # 霍夫直线检测

        # for line in lines:
        #     x1, y1, x2, y2 = line[0]
        #     cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # cv2.imshow('1', img)
        # cv2.waitKey()

        # 提取所有直线中的竖直线和指定长度的横直线
        x = []
        y_loc = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if -10 < x1 - x2 < 10:
                x.append(x1)
            elif -10 < y1 - y2 < 10 and 450 < x2 - x1 < 600:
                y_loc.append((y1, x1, x2))

        # 获得所需图像的x坐标
        x1 = x2 = 0
        x = sorted(x)
        for i in range(len(x) - 1):
            if 450 < x[i + 1] - x[i] < 600:
                x1 = x[i]
                x2 = x[i + 1]
                break

        # 获得所需图像的y坐标
        y1 = y2 = 0
        y_loc = sorted(y_loc, key=lambda x: x[0])
        for tuple_ in y_loc:
            y = tuple_[0]
            if x1 - 10 < tuple_[1] < x2 + 10 and x1 - 10 < tuple_[2] < x2 + 10:
                if y1 == 0:
                    y1 = y
                y2 = y

        img_needed = img[y1:y2, x1:x2]  # 切割图片

        # cv2.imshow('1', img_needed)
        # cv2.waitKey()
        return img_needed

    def _img_separated(self, img):
        """
        从完整图像中分割已经取出的图像(带有文字的图像)
        :param img: array(BGR)
        :return: array(BGR)
        """
        # 从完整图像中分割出需要的已知位置的四部分
        img_place = img[70:105, 25:105]
        img_attr = img[155:190, 25:200]
        img_level = img[330:355, 35:90]
        img_attrs = img[380:580, 25:295]

        # cv2.imwrite('./1234.png', img)
        # cv2.imwrite('./1.png', img_name)
        # cv2.imwrite('./2.png', img_attr)
        # cv2.imwrite('./3.png', img_level)
        # cv2.imwrite('./4.png', img_attrs)
        return img_place, img_attr, img_level, img_attrs

    def _img_text_recognition(self, *imgs):
        """
        识别图像文字，返回文字列表
        :param imgs: tuple(array(BGR), ...)
        :return: List
        """
        reader = easyocr.Reader(['ch_sim'])  # 识别简体中文
        texts = []
        for img in imgs:
            text_list = reader.readtext(img)  # 识别文字

            # 挨个识别
            for text in text_list:
                # print(text[1])
                texts.append(text[1])

        # 除去多余项
        if '2件套' in texts[-1]:
            texts.pop()
        return texts

    def stop(self):
        self.is_continue = False


class MainWindow(QWidget):
    """
    主窗体
    """
    flag = True
    sin = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedSize(self.minimumSize())
        self.move(10, 10)
        self.setWindowTitle('app')

        self.sm = ScreenMonitor()
        self.sin.connect(self.sm.stop)
        self.sm.strsin.connect(self.accept_signal_string)
        self._main_ui()

    def _main_ui(self):
        """
        主窗体UI布局
        :return: None
        """
        w = QWidget()
        layouth = QHBoxLayout()  # (3个按钮)水平布局
        w.setLayout(layouth)

        layoutv = QVBoxLayout()  # (按钮和提示)垂直布局
        self.setLayout(layoutv)  # 设置主窗体为垂直平布局
        layoutv.addWidget(w)

        # 单次按钮
        self.btn_single = QPushButton('单次')
        layouth.addWidget(self.btn_single)
        self.btn_single.setEnabled(False)
        self.btn_single.clicked.connect(self.btn_single_fun)

        # 循环按钮
        self.btn_circle = QPushButton('循环开始')
        layouth.addWidget(self.btn_circle)
        self.btn_circle.setEnabled(False)
        self.btn_circle.clicked.connect(self.btn_circle_fun)

        # 设置按钮
        self.btn_setting = QPushButton('设置')
        layouth.addWidget(self.btn_setting)
        self.btn_setting.clicked.connect(self._create_dialog)  # 连接创建对话框函数

        # 设置提示
        self.tip = QLabel('请设置圣遗物标准后再开始。。')
        layoutv.addWidget(self.tip)

    def btn_circle_fun(self):
        """
        循环按钮点击函数
        :return: None
        """
        sm = ScreenMonitor()
        self.sin.connect(sm.stop)
        if self.flag:
            self.sm.is_continue = True
            self.sm.start()
            self.flag = False
            self.btn_circle.setText('停止循环')
        else:
            self.sin.emit()
            self.flag = True
            self.btn_circle.setText('开始循环')

    def btn_single_fun(self):
        """
        单次按钮点击函数
        :return: None
        """
        self.sm.is_continue = True
        self.sm.Run()
        self.sm.flag = True

    def accept_signal_string(self, text):
        """
        接受信号信息，并把文本加入到提示中
        :param text:
        :return:
        """
        self.tip.setText(text)

    def _create_dialog(self):
        """
        创建对话框
        :return: None
        """
        dw = DialogWindow()
        dw.exec()
        self.btn_single.setEnabled(True)
        self.btn_circle.setEnabled(True)


class DialogWindow(QDialog):
    """
    对话框：用于设置词条
    """
    n = 28
    num = 14
    s = 's1,cb1,cb2,cb3,s21,s22,s23,s24,s25,s31,s32,s33,s34,s35'
    info = {}
    tempdict = {}
    relic_initialized = {}
    relic = {'0': '角斗士的终幕礼', '1': '流浪大地的乐团', '2': '昔日宗室之仪', '3': '染血的骑士道',
             '4': '被怜爱的少女', '5': '翠绿之影', '6': '悠古的磐岩', '7': '逆飞的流星', '8': '平息雷鸣的尊者',
             '9': '如雷的盛怒', '10': '渡过烈火的贤人', '11': '炽烈的炎之魔女', '12': '冰风迷途的勇士',
             '13': '沉沦之心', '14': '千岩牢固', '15': '苍白之火', '16': '追忆之注连', '17': '绝缘之旗印',
             '18': '华馆梦醒形骸记', '19': '海染砗磲', '20': '辰砂往生录', '21': '来歆余响', '22': '深林的记忆',
             '23': '饰金之梦', '24': '沙上楼阁史话', '25': '乐园遗落之花', '26': '水仙之梦', '27': '花海甘露之光'}
    relic_ = {1: '暴击率              ', 2: '暴击伤害           ', 3: '元素精通           ', 4: '元素充能效率     ',
              5: '%攻/%生/%防   '}
    relic1 = {0: '2.7%', 1: '3.1%', 2: '3.5%', 3: '3.9%'}
    relic2 = {0: '5.4%', 1: '6.2%', 2: '7.0%', 3: '7.8%'}
    relic3 = {0: '16', 1: '19', 2: '21', 3: '23'}
    relic4 = {0: '4.5%', 1: '5.2%', 2: '5.8%', 3: '6.5%'}
    relic5 = {0: '攻4.1%/生4.1%/防5.1%', 1: '攻4.7%/生4.7%/防5.8%', 2: '攻5.3%/生5.3%/防6.6%',
              3: '攻5.8%/生5.8%/防7.3%'}

    def __init__(self):
        super(DialogWindow, self).__init__()
        self.move(20, 20)
        self.setWindowTitle('setting')
        f = open('./info.json', 'a+')
        f.seek(0)
        try:
            self.info = json.loads(f.read())
        except ValueError:
            pass
        f.close()
        # print(self.info)
        self.info, self.relic_initialized = utils.check_information(self.info, self.n, self.num, self.s)
        # print(self.info)
        # print(self.relic_initialized)
        if len(self.relic_initialized) != 0:
            templist = self.relic_initialized.keys()
            templist = map(lambda x: self.relic[x], templist)
            s = '\n\t'.join(templist)
            msg = QMessageBox.warning(self, 'initialized', '有缺漏，已恢复默认，以下为具体名称：\n\t' + s)
        self._ui()

    def _ui(self):
        """
        对话框UI布局
        :return: None
        """
        # 总
        l_main = QVBoxLayout()  # 主布局(垂直)
        self.setLayout(l_main)  # 对话框设置垂直布局

        # 上部分(滚动条)
        l_s = QHBoxLayout()  # 滚动条内(水平)
        w_s = QWidget()  # 滚动条内，水平放置图片
        w_s.setLayout(l_s)
        # 滚动条中按钮添加
        for index in range(28):
            btn = QPushButton(w_s)
            btn.setIcon(QIcon('./DataImg/{}.png'.format(index)))
            btn.setIconSize(QSize(75, 75))
            btn.setObjectName(str(index))
            btn.clicked.connect(lambda: self._show_bottom(self.sender()))
            l_s.addWidget(btn)
        # 添加滚动条
        scroll = QScrollArea()
        scroll.setWidget(w_s)
        l_main.addWidget(scroll)

        # 下部分(总)
        l_bottom = QHBoxLayout()
        self.w_bottom = QWidget()
        self.w_bottom.hide()
        self.w_bottom.setLayout(l_bottom)
        l_main.addWidget(self.w_bottom)
        # 下左部分
        l_bot_left = QVBoxLayout()
        w_bot_left = QWidget()
        w_bot_left.setLayout(l_bot_left)
        l_bottom.addWidget(w_bot_left)
        # 下左部分组件
        # 图片
        self.label_bot_left = QLabel()
        l_bot_left.addWidget(self.label_bot_left)
        # [部位3的主词条算有效词条，攻生防不共存且(主词条不为攻生防)攻 > 生 > 防，(主词条为攻生防)主词条优先，
        # 防御与精通共存时，有效词条个数减1]
        l = QLabel('有效词条：[副词条：\n双暴 精通 充能 %攻 %生 %防]\n' +
                   '沙漏、杯及冠的主词条算有效词条\n' +
                   '(有效词条 %攻 %生 %防 不共存：\n' +
                   '主词条为 %攻 %生 %防 时，\n' +
                   '忽略副词条%攻/%生/%防；其他，\n' +
                   '优先级为 %攻>%生>%防)')
        l_bot_left.addWidget(l)
        # 按钮
        btn_bot_left = QPushButton('保存')
        btn_bot_left.clicked.connect(self._save_information)
        l_bot_left.addWidget(btn_bot_left)
        # 下右部分(Tap容器)
        w_tab = QTabWidget()
        self.tap1 = QWidget()
        self._setTabComponent1()
        self.tap2 = QWidget()
        self._setTabComponent2()
        self.tap3 = QWidget()
        self._setTabComponent3()
        w_tab.addTab(self.tap1, '有效词条个数及其他')
        w_tab.addTab(self.tap2, '花及羽毛有效副词条最小值')
        w_tab.addTab(self.tap3, '沙漏、杯及冠有效副词条最小值')
        l_bottom.addWidget(w_tab)

    def _setTabComponent1(self):
        """
        设置容器(QTabWidget) tap1页面组件
        :return: None
        """
        layoutv = QVBoxLayout()  # 整体垂直布局
        self.tap1.setLayout(layoutv)
        # 标签，设置有效词条个数，与滑动条配合
        l = QLabel('有效词条最小个数')
        layoutv.addWidget(l)
        # 滑动条+警告QLabel
        w_sl = QWidget()
        l_sl = QHBoxLayout()
        w_sl.setLayout(l_sl)
        ##滑动条显示
        self.l1 = QLabel()
        l_sl.addWidget(self.l1)
        ## 滑动条，设置有效词条个数
        self.s1 = QSlider(Qt.Orientation.Horizontal)
        self._slider_setting(self.s1, 2, 4, 1)
        self.s1.setObjectName('s1')
        self.s1.valueChanged.connect(lambda: self._update_information_slider(self.s1))
        l_sl.addWidget(self.s1, 1, Qt.AlignmentFlag.AlignJustify)
        ## 警告
        self.ls1 = QLabel()
        l_sl.addWidget(self.ls1)
        layoutv.addWidget(w_sl)
        # 多选框+警告QLabel
        w_cl1 = QWidget()
        l_cl1 = QHBoxLayout()
        w_cl1.setLayout(l_cl1)
        ## 多选框1
        self.cb1 = QCheckBox('不保留主属性与套装属性(2件套效果为%攻/%生/%防)不符的圣遗物')
        self.cb1.setObjectName('cb1')
        self.cb1.stateChanged.connect(lambda: self._update_information_check(self.cb1))
        l_cl1.addWidget(self.cb1)
        ## 警告1
        self.lcb1 = QLabel()
        l_cl1.addWidget(self.lcb1)
        layoutv.addWidget(w_cl1, 1, Qt.AlignmentFlag.AlignTop)

        w_cl2 = QWidget()
        l_cl2 = QHBoxLayout()
        w_cl2.setLayout(l_cl2)
        ##多选框2
        self.cb2 = QCheckBox('不保留(%攻/%生+充能+精通)词条组(仅3个有效词条时生效)')
        self.cb2.setObjectName('cb2')
        self.cb2.stateChanged.connect(lambda: self._update_information_check(self.cb2))
        l_cl2.addWidget(self.cb2)
        ## 警告2
        self.lcb2 = QLabel()
        l_cl2.addWidget(self.lcb2)
        layoutv.addWidget(w_cl2, 1, Qt.AlignmentFlag.AlignTop)

        w_cl3 = QWidget()
        l_cl3 = QHBoxLayout()
        w_cl3.setLayout(l_cl3)
        ##多选框3
        self.cb3 = QCheckBox('保留双暴词条圣遗物')
        self.cb3.setObjectName('cb3')
        self.cb3.stateChanged.connect(lambda: self._update_information_check(self.cb3))
        l_cl3.addWidget(self.cb3)
        ## 警告3
        self.lcb3 = QLabel()
        l_cl3.addWidget(self.lcb3)
        layoutv.addWidget(w_cl3, 1, Qt.AlignmentFlag.AlignTop)

    def _setTabComponent2(self):
        """
        设置容器(QTabWidget) tap2页面组件
        :return: None
        """
        layoutv = QVBoxLayout()  # 整体垂直布局
        self.tap2.setLayout(layoutv)
        # 部分一
        w1 = QWidget()
        layoutv.addWidget(w1)
        layouth1 = QHBoxLayout()
        w1.setLayout(layouth1)
        self.l21 = QLabel()
        layouth1.addWidget(self.l21)
        self.s21 = QSlider(Qt.Orientation.Horizontal)
        layouth1.addWidget(self.s21, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls21 = QLabel()
        layouth1.addWidget(self.ls21)
        # 部分二
        w2 = QWidget()
        layoutv.addWidget(w2)
        layouth2 = QHBoxLayout()
        w2.setLayout(layouth2)
        self.l22 = QLabel()
        layouth2.addWidget(self.l22)
        self.s22 = QSlider(Qt.Orientation.Horizontal)
        layouth2.addWidget(self.s22, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls22 = QLabel()
        layouth2.addWidget(self.ls22)
        # 部分三
        w3 = QWidget()
        layoutv.addWidget(w3)
        layouth3 = QHBoxLayout()
        w3.setLayout(layouth3)
        self.l23 = QLabel()
        layouth3.addWidget(self.l23)
        self.s23 = QSlider(Qt.Orientation.Horizontal)
        layouth3.addWidget(self.s23, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls23 = QLabel()
        layouth3.addWidget(self.ls23)
        # 部分四
        w4 = QWidget()
        layoutv.addWidget(w4)
        layouth4 = QHBoxLayout()
        w4.setLayout(layouth4)
        self.l24 = QLabel()
        layouth4.addWidget(self.l24)
        self.s24 = QSlider(Qt.Orientation.Horizontal)
        layouth4.addWidget(self.s24, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls24 = QLabel()
        layouth4.addWidget(self.ls24)
        # 部分五
        w5 = QWidget()
        layoutv.addWidget(w5)
        layouth5 = QHBoxLayout()
        w5.setLayout(layouth5)
        self.l25 = QLabel()
        layouth5.addWidget(self.l25)
        self.s25 = QSlider(Qt.Orientation.Horizontal)
        layouth5.addWidget(self.s25, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls25 = QLabel()
        layouth5.addWidget(self.ls25)

        templist = [self.s21, self.s22, self.s23, self.s24, self.s25]
        for index in range(len(templist)):
            self._slider_setting(templist[index], 0, 3, 1)
            templist[index].setObjectName('s2{}'.format(index + 1))
            templist[index].valueChanged.connect(lambda: self._update_information_slider(self.sender()))

    def _setTabComponent3(self):
        """
        设置容器(QTabWidget) tap3页面组件
        :return: None
        """
        layoutv = QVBoxLayout()  # 整体垂直布局
        self.tap3.setLayout(layoutv)
        # 部分一
        w1 = QWidget()
        layoutv.addWidget(w1)
        layouth1 = QHBoxLayout()
        w1.setLayout(layouth1)
        self.l31 = QLabel()
        layouth1.addWidget(self.l31)
        self.s31 = QSlider(Qt.Orientation.Horizontal)
        layouth1.addWidget(self.s31, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls31 = QLabel()
        layouth1.addWidget(self.ls31)
        # 部分二
        w2 = QWidget()
        layoutv.addWidget(w2)
        layouth2 = QHBoxLayout()
        w2.setLayout(layouth2)
        self.l32 = QLabel()
        layouth2.addWidget(self.l32)
        self.s32 = QSlider(Qt.Orientation.Horizontal)
        layouth2.addWidget(self.s32, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls32 = QLabel()
        layouth2.addWidget(self.ls32)
        # 部分三
        w3 = QWidget()
        layoutv.addWidget(w3)
        layouth3 = QHBoxLayout()
        w3.setLayout(layouth3)
        self.l33 = QLabel()
        layouth3.addWidget(self.l33)
        self.s33 = QSlider(Qt.Orientation.Horizontal)
        layouth3.addWidget(self.s33, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls33 = QLabel()
        layouth3.addWidget(self.ls33)
        # 部分四
        w4 = QWidget()
        layoutv.addWidget(w4)
        layouth4 = QHBoxLayout()
        w4.setLayout(layouth4)
        self.l34 = QLabel()
        layouth4.addWidget(self.l34)
        self.s34 = QSlider(Qt.Orientation.Horizontal)
        layouth4.addWidget(self.s34, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls34 = QLabel()
        layouth4.addWidget(self.ls34)
        # 部分五
        w5 = QWidget()
        layoutv.addWidget(w5)
        layouth5 = QHBoxLayout()
        w5.setLayout(layouth5)
        self.l35 = QLabel()
        layouth5.addWidget(self.l35)
        self.s35 = QSlider(Qt.Orientation.Horizontal)
        layouth5.addWidget(self.s35, 1, Qt.AlignmentFlag.AlignJustify)
        self.ls35 = QLabel()
        layouth5.addWidget(self.ls35)

        templist = [self.s31, self.s32, self.s33, self.s34, self.s35]
        for index in range(len(templist)):
            self._slider_setting(templist[index], 0, 3, 1)
            templist[index].setObjectName('s3{}'.format(index + 1))
            templist[index].valueChanged.connect(lambda: self._update_information_slider(self.sender()))

    def _slider_setting(self, slider, smin, smax, step):
        """
        设置自定义PyQt中Slider滑动条
        :param slider: PyQt.Slider
        :param min: 滑动条最小值
        :param max: 滑动条最大值
        :param step: 滑动条步长
        :return: None
        """
        slider.setMinimum(smin)
        slider.setMaximum(smax)
        slider.setSingleStep(step)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)

    def _save_information(self):
        """
        (点击保存按钮后)保存信息到json
        :return:None
        """
        f = open('./info.json', 'w')
        f.write(json.dumps(self.info))
        f.close()

    def _update_information_slider(self, component):
        """
        更新类属性information(滑动条)
        :return: None
        """
        name = component.objectName()
        if name == 's1' and component.value() == 3:
            self.cb2.setEnabled(True)
        else:
            self.cb2.setEnabled(False)
            self.cb2.setChecked(False)
        self.tempdict[name] = component.value()
        self._setText_correspond(component)
        eval('self.l' + name + '.setText("")')  # 滑动后取消警告

    def _update_information_check(self, component):
        """
        更新类属性information(多选框)
        :return: None
        """
        name = component.objectName()
        self.tempdict[name] = component.isChecked()
        eval('self.l' + name + '.setText("")')  # 改变后取消警告

    def _show_bottom(self, component):
        imgname = component.objectName()

        self.label_bot_left.setPixmap(QPixmap('./DataImg/{}.png'.format(imgname)))

        self.tempdict = self.info[imgname]

        # 初始化
        self.s1.setValue(self.tempdict['s1'])
        self.s21.setValue(self.tempdict['s21'])
        self.s22.setValue(self.tempdict['s22'])
        self.s23.setValue(self.tempdict['s23'])
        self.s24.setValue(self.tempdict['s24'])
        self.s25.setValue(self.tempdict['s25'])
        self.s31.setValue(self.tempdict['s31'])
        self.s32.setValue(self.tempdict['s32'])
        self.s33.setValue(self.tempdict['s33'])
        self.s34.setValue(self.tempdict['s34'])
        self.s35.setValue(self.tempdict['s35'])
        self.cb1.setChecked(self.tempdict['cb1'])
        if self.tempdict['s1'] == 3:
            self.cb2.setChecked(self.tempdict['cb2'])
        else:
            self.cb2.setEnabled(False)
            self.cb2.setChecked(False)
            self.tempdict['cb2'] = False
        self.cb3.setChecked(self.tempdict['cb3'])
        self._setText_correspond(self.s1)
        self._setText_correspond(self.s21)
        self._setText_correspond(self.s22)
        self._setText_correspond(self.s23)
        self._setText_correspond(self.s24)
        self._setText_correspond(self.s25)
        self._setText_correspond(self.s31)
        self._setText_correspond(self.s32)
        self._setText_correspond(self.s33)
        self._setText_correspond(self.s34)
        self._setText_correspond(self.s35)

        # 添加警告(Qlabel(红色感叹号))
        if imgname in self.relic_initialized:
            for item in self.relic_initialized[imgname]:
                eval('self.l' + item + '.setText("<h1 style='"color:red"'>!</h1>")')
        else:
            self.ls1.setText('')
            self.lcb1.setText('')
            self.lcb2.setText('')
            self.lcb3.setText('')
            self.ls21.setText('')
            self.ls22.setText('')
            self.ls23.setText('')
            self.ls24.setText('')
            self.ls25.setText('')
            self.ls31.setText('')
            self.ls32.setText('')
            self.ls33.setText('')
            self.ls34.setText('')
            self.ls35.setText('')

        self.w_bottom.show()

    def _setText_correspond(self, component):
        """
        设置对应滑动条组件的QLabel文本
        :param component:组件(滑动条组件)
        :return:None
        """
        name = component.objectName()
        if name == 's1':
            self.l1.setText(str(self.tempdict['s1']) + '条')
        else:
            eval('self.l' + name[-2:] + '.setText(self.relic_[' + name[-1:] + ']+self.relic' + name[
                                                                                               -1:] + '[self.tempdict["' + name + '"]])')

    def closeEvent(self, even):
        self._save_information()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
