import csv
import re
import string
import threading
import traceback
from tkinter.tix import Form

import numpy as np
import xlrd
import cv2
import qdarkstyle
from PyQt5.QtGui import QPixmap, QTextCharFormat, QRegExpValidator
from qdarkstyle import DarkPalette
from PyQt5 import QtCore
from log_utils import Logger

# import serial
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTextEdit, QMessageBox, QLabel, QInputDialog, QWidget
import os, sys

from utils import check_hex
from projector_pdu import Ui_MainWindow
import subprocess
import datetime  # 导入datetime模块
import threading  # 导入threading模块
import time
from serial_utils import get_ports, open_port, parse_one_frame, str2hex, asu_pdu_parse_one_frame, \
    asu_pdu_build_one_frame, mPduCmdDict2Rev
import csv
import shutil
from combocheckbox import ComboCheckBox
# 下拉复选框测试/下拉复选框test.py
from PyQt5 import QtCore, QtGui, QtWidgets

cols_temp = []  # 获取第三列内容
cols_voltage = []  # 获取第三列内容

SW_VERSION = 'SW: 2023042100'
FILE_PARA = 'pic/param.csv'
NTC_VOLTAGE_TEMP = 'pic/ntc_vol_temp_list.xls'
imageList = ["pic/op01_char.jpg", "pic/op02_white.png", "pic/op03_black.png"]
g_img_num = -1


def cvCallBack(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('left button down')
    elif event == cv2.EVENT_LBUTTONUP:
        print('left button up', x, y, flags)
        global g_img_num
        g_img_num += 1
        if g_img_num > 2:
            g_img_num = 0
        show_img(g_img_num)
    elif event == cv2.EVENT_RBUTTONDOWN:
        print('right button down')
    elif event == cv2.EVENT_RBUTTONUP:
        cv2.destroyAllWindows()
        print('right button up')
    if event == cv2.EVENT_MOUSEMOVE:
        pass
        # cv2.circle(param, (x, y), 2, (255, 126, 0), -1)


# def testResult(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         print('left button down')
#     elif event == cv2.EVENT_LBUTTONUP:
#         pass
#     elif event == cv2.EVENT_RBUTTONDOWN:
#         print('right button down')
#     elif event == cv2.EVENT_RBUTTONUP:
#         cv2.destroyAllWindows()
#         print('right button up')
#     if event == cv2.EVENT_MOUSEMOVE:
#         pass
# cv2.circle(param, (x, y), 2, (255, 126, 0), -1)

def show_img(num):
    global g_img_num
    g_img_num = num
    img_bgr = cv2.imread(imageList[g_img_num])
    cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow("myImage", 0, 0)
    cv2.setMouseCallback('myImage', cvCallBack, img_bgr)
    cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("myImage", img_bgr)


class SerialThread(QThread):
    data_arrive_signal = pyqtSignal(name='serial_data')

    def __init__(self, ser=None):
        super().__init__()
        self.ser = ser
        self.current_data = b''
        self.exitFlag = False
        self.num = 0

    def run(self):
        time.sleep(1)  # 防止直接进循环, 阻塞主ui
        while True:
            print('============================================')
            try:
                if self.ser is not None and self.ser.inWaiting():
                    self.current_data = self.ser.read(self.ser.inWaiting())
                    self.num += 1
                    self.data_arrive_signal.emit()
            except:
                return


class AutoTestThread(QThread):
    update_motor_signal = pyqtSignal(name='update_motor_info')

    def __init__(self, win=None, ser=None, roundSteps=2900, circle=6):
        super().__init__()
        self.win = win
        self.ser = ser
        self.count = 0
        self.roundSteps = roundSteps
        self.circle = int(circle)
        self.exitFlag = False

    def run(self):
        for key in self.win.dictAutoTestResult:
            self.win.dictAutoTestResult[key] = 0
        if self.win.dictAutoTest['FAN1-LED'] or self.win.dictAutoTest['FAN2-LCD'] or self.win.dictAutoTest['FAN3-EVR']:
            # set fan speed
            self.win.ui.fan1SpinBox.setValue(100)
            self.win.ui.fan2SpinBox.setValue(100)
            self.win.ui.fan3SpinBox.setValue(100)
            time.sleep(1)
        motorData = [1, 0, 0]
        self.win.totalSteps = 0
        print('>>>>>>>>>> 自动化测试开始 ', motorData[0], self.roundSteps, self.count, self.circle)
        preTime = time.time()
        while self.count < self.circle:
            if self.exitFlag:
                self.exitFlag = False
                print(">>>>>>>>>> AutoTestThread Exit ", self.count)
                break
            try:
                if self.ser is not None:
                    # self.update_motor_signal.emit()
                    # get ntc
                    if self.win.dictAutoTest['NTC-LED'] or self.win.dictAutoTest['NTC-LCD'] or self.win.dictAutoTest[
                        'NTC-EVR']:
                        self.win.update_data()
                        lastTime = time.time()
                        while not self.win.mNtcFinished:
                            nowTime = time.time()
                            # print(nowTime-lastTime)
                            if (nowTime - lastTime) > 2:
                                break
                        self.win.mNtcFinished = False
                        time.sleep(1)

                    # get fan
                    if self.win.dictAutoTest['FAN1-LED'] or self.win.dictAutoTest['FAN2-LCD'] or self.win.dictAutoTest[
                        'FAN3-EVR']:
                        strHex = asu_pdu_build_one_frame('CMD_GET_FANS', 0, None)
                        self.win.serial_write(strHex)
                        lastTime = time.time()
                        while not self.win.mFanFinished:
                            nowTime = time.time()
                            if (nowTime - lastTime) > 3:
                                break
                        self.win.mFanFinished = False
                        time.sleep(1)
                    # set motor
                    if self.win.dictAutoTest['MOTOR']:
                        self.win.ui.motorStatuslabel.setStyleSheet("color:white")
                        self.win.ui.motorStatuslabel.setText("马达运行中")
                        # # 步数用两个字节表示，低字节在前，高字节在后
                        motorData[1] = int(self.roundSteps) & 0x00FF
                        motorData[2] = int(self.roundSteps) >> 8
                        print('>>>>>>>>>> 自动化测马达 ', self.roundSteps, self.count, self.circle)
                        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(motorData), motorData)
                        self.win.serial_write(strHex)
                        lastTime = time.time()
                        while not self.win.mMotorFinished:
                            currentTime = time.time()
                            # time.sleep(1)
                            if (currentTime - lastTime) > 6:
                                print('马达超时返回 ', currentTime - lastTime)
                                break
                        nowTime = time.time()
                        if (nowTime - lastTime) < 0.1:
                            time.sleep(5)  # 这个地方有个bug，0秒就返回True
                            print('>>>>>>>>>>>>>>>> 马达返回异常，做规避处理 ', nowTime - lastTime)
                        else:
                            print('马达测试完成，延时2秒 ', nowTime - lastTime)
                            time.sleep(2)
                        print('motor ++++++++++++++++++++++++++++++++++++', self.win.mMotorFinished,
                              (nowTime - lastTime))
                        self.win.mMotorFinished = False
                        if motorData[0] == 1:
                            motorData[0] = 0
                        else:
                            motorData[0] = 1

            except:
                print('串口错误')
            self.count += 1
            self.win.ui.totalRoundLabel.setText(str(self.count))
        self.win.ui.autoTestFinishLabel.setStyleSheet("color:green")
        self.win.ui.autoTestFinishLabel.setText('测试完成')
        nowTime = time.time()
        totalTime = nowTime - preTime
        print(self.win.dictAutoTestResult)

        print('------------------------------------- totalSteps ', self.win.totalSteps)
        result = [0, 0]
        allRight = True
        passPix = QPixmap('pic/pass.png')
        failPix = QPixmap('pic/fail.png')
        for key in self.win.dictAutoTestResult:
            # if self.win.dictAutoTestResult[key] == 0:
            #     continue
            result[0] = key
            result[1] = 'fail'
            if self.win.dictAutoTestResult[key] > 0 and self.win.dictAutoTestResult[key] == self.circle:
                if key == 'MOTOR':
                    if self.win.totalSteps > 2000:  # circle 必须大于1
                        self.win.ui.testMotorLabel.setPixmap(passPix)
                        result[1] = 'pass'
                    else:
                        self.win.ui.testMotorLabel.setPixmap(failPix)
                elif key == 'NTC-LED':
                    self.win.ui.testTemp1Label.setPixmap(passPix)
                    result[1] = 'pass'
                elif key == 'NTC-LCD':
                    self.win.ui.testTemp2Label.setPixmap(passPix)
                    result[1] = 'pass'
                elif key == 'NTC-EVR':
                    self.win.ui.testTemp3Label.setPixmap(passPix)
                    result[1] = 'pass'
                elif key == 'FAN1-LED':
                    self.win.ui.testFan1Label.setPixmap(passPix)
                    result[1] = 'pass'
                elif key == 'FAN2-LCD':
                    self.win.ui.testFan2Label.setPixmap(passPix)
                    result[1] = 'pass'
                elif key == 'FAN3-EVR':
                    self.win.ui.testFan3Label.setPixmap(passPix)
                    result[1] = 'pass'
                else:
                    pass
            self.win.write_result_csv('a', result)
            print(result)
        # if allRight:
        #     img_bgr = cv2.imread('pic/pass.png')
        # else:
        #     img_bgr = cv2.imread('pic/fail.png')
        # cv2.namedWindow("Test Result")
        # cv2.moveWindow("Test Result", 1600, 260)
        # cv2.resizeWindow("Test Result", 1000, 1000)  # 设置图片显示窗口大小
        # cv2.imshow("Test Result", img_bgr)

        # cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
        # cv2.moveWindow("myImage", 0, 0)
        # cv2.setMouseCallback('myImage', testResult, img_bgr)
        # cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # cv2.imshow("myImage", img_bgr)
        # cv2.waitKey(0)

        print('>>>>>>>>>> 测试完成，耗时：', totalTime)
        self.win.ui.autoTestButton.setEnabled(True)


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    update_temp_flag = False
    mPguLedFlag = False

    def __init__(self):
        super().__init__()
        self.mNtcFinished = False
        self.mMotorFinished = False
        self.mFanFinished = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('调试工具')
        self.mLoginOn = False
        self.switch_windows_ui(False)
        available_ports = get_ports()
        self.ui.serial_selection.addItems(available_ports)
        self.ui.baud_rate.setCurrentText("921600")

        self.ui.adminPasswordButton.clicked.connect(self.admin_password_logon)
        self.ui.saveThresholdButton.clicked.connect(self.save_para)
        self.ui.savePduDataButton.clicked.connect(self.save_pdu_data)
        self.ui.autoTestButton.clicked.connect(self.auto_test_pdu)
        self.ui.fan1HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.fan2HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.fan3HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.redHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.greenHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.blueHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.redMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)
        self.ui.greenMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)
        self.ui.blueMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)
        self.ui.panelPwmHorizontalSlider.valueChanged['int'].connect(self.set_panel_brightness)

        self.ui.autoTestMotorOpenButton.clicked.connect(self.auto_test_motor_open)
        self.ui.autoTestMotorCloseButton.clicked.connect(self.auto_test_motor_close)
        self.ui.motorBackButton.clicked.connect(self.motor_back)
        self.ui.motorForwardButton.clicked.connect(self.motor_forward)
        self.ui.updateTempButton.clicked.connect(self.update_temperature)
        self.ui.openLedButton.clicked.connect(self.open_pgu_led)

        self.ui.open_port.clicked.connect(self.open_port)
        self.ui.close_port.clicked.connect(self.close_port)
        self.ui.refresh_port.clicked.connect(self.refresh_port)
        self.ui.send_data.clicked.connect(self.send_data)

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        self.serial_thread.data_arrive_signal.connect(self.receive_data)  # 不要每次打开时都关联signal，会导致每次接收数据时signal多次
        self.autoTestThread = None

        pix = QPixmap(imageList[0])
        self.ui.imageCharLabel.setStyleSheet("border: 3px solid gray")
        self.ui.imageCharLabel.setScaledContents(True)
        self.ui.imageCharLabel.setPixmap(pix)
        self.ui.imageCharLabel.mousePressEvent = self.show_char_img

        pix_white = QPixmap(imageList[1])
        self.ui.imageWhiteLabel.setStyleSheet("border: 3px solid gray")
        self.ui.imageWhiteLabel.setScaledContents(True)
        self.ui.imageWhiteLabel.setPixmap(pix_white)
        self.ui.imageWhiteLabel.mousePressEvent = self.show_white_img

        pix_black = QPixmap(imageList[2])
        self.ui.imageBlackLabel.setStyleSheet("border: 3px solid gray")
        self.ui.imageBlackLabel.setScaledContents(True)
        self.ui.imageBlackLabel.setPixmap(pix_black)
        self.ui.imageBlackLabel.mousePressEvent = self.show_black_img
        # for i in range(len(imageList)):
        #     pix = QPixmap(imageList[i])
        #     self.ui.imageBlackLabel.setStyleSheet("border: 3px solid gray")
        #     self.ui.imageBlackLabel.setScaledContents(True)
        #     if i == 0:
        #         self.ui.imageCharLabel.setPixmap(pix)
        #     elif i == 1:
        #         self.ui.imageWhiteLabel.setPixmap(pix)
        #     elif i == 2:
        #         self.ui.imageBlackLabel.setPixmap(pix)
        # self.ui.imageBlackLabel.mousePressEvent = self.show_black_img
        # self.ui.imageWhiteLabel.mousePressEvent = self.show_white_img
        # self.ui.imageCharLabel.mousePressEvent = self.show_char_img

        self.sn = '1234567890'
        lcd_items = ["正常", "上下", "左右", "上下左右"]
        self.ui.mirrorComboBox.addItems(lcd_items)
        self.ui.mirrorComboBox.activated.connect(self.slot_lcd_mirror)
        self.ui.swLabel = QLabel()
        self.ui.swLabel.setText(SW_VERSION)
        self.ui.statusbar.addPermanentWidget(self.ui.swLabel, stretch=0)
        self.ui.hwLabel = QLabel()

        # 温度补偿
        self.cols_temp = []
        self.cols_voltage = []
        # 温度标定数据
        self.read_ntc_excel()
        # 阈值参数
        self.read_para()

        self.totalRounds = 0
        self.limitSteps = 0
        # 限定文本框输入的数据类型
        reg = QRegExp('[0-9]+$')
        # reg = QRegExp('[a-zA-Z0-9]+$') #数字和字母
        validator = QRegExpValidator()
        validator.setRegExp(reg)
        self.ui.ntcThresholdUpperEdit.setValidator(validator)
        self.ui.ntcThresholdLowerEdit.setValidator(validator)
        self.dictAutoTest = {'MOTOR': False,
                             'FAN1-LED': False, 'FAN2-LCD': False,
                             'NTC-LED': False, 'NTC-LCD': False,
                             'FAN3-EVR': False, 'NTC-EVR': False}
        self.dictAutoTestResult = {'MOTOR': 0,
                                   'FAN1-LED': 0, 'FAN2-LCD': 0,
                                   'NTC-LED': 0, 'NTC-LCD': 0,
                                   'FAN3-EVR': 0, 'NTC-EVR': 0}
        for key in self.dictAutoTestResult:
            self.dictAutoTestResult[key] = 0
        self.autoTestItems = [*self.dictAutoTest]
        print(self.autoTestItems)
        self.ui.testItemsComboBox.myadditems(self.autoTestItems)
        self.ui.testItemsComboBox.editTextChanged.connect(self.show_autotest_items)
        for i in range(1, len(self.autoTestItems) - 1):
            self.ui.testItemsComboBox.addQCheckBox(i)
        self.autoTestFanFlag = False
        self.autoTestNtcFlag = False
        self.autoTestMotorFlag = False
        self.totalSteps = 0

    def show_autotest_items(self, index):
        select_items = self.ui.testItemsComboBox.get_selected()
        # print('>>>>>>>>>>>>>>>>>', select_items)
        for i in range(0, len(self.autoTestItems)):
            if self.autoTestItems[i] in select_items:
                if i == 0:
                    self.ui.testMotorLabel.show()
                    self.ui.testMotorLabel1.show()
                    self.dictAutoTest['MOTOR'] = True
                    self.dictAutoTestResult['MOTOR'] = 0
                elif i == 1:
                    self.ui.testFan1Label.show()
                    self.ui.testFan1Label1.show()
                    self.dictAutoTest['FAN1-LED'] = True
                    self.dictAutoTestResult['FAN1-LED'] = 0
                elif i == 2:
                    self.ui.testFan2Label.show()
                    self.ui.testFan2Label1.show()
                    self.dictAutoTest['FAN2-LCD'] = True
                    self.dictAutoTestResult['FAN2-LCD'] = 0
                elif i == 3:
                    self.ui.testTemp1Label.show()
                    self.ui.testTemp1Label1.show()
                    self.dictAutoTest['NTC-LED'] = True
                    self.dictAutoTestResult['NTC-LED'] = 0
                elif i == 4:
                    self.ui.testTemp2Label.show()
                    self.ui.testTemp2Label1.show()
                    self.dictAutoTest['NTC-LCD'] = True
                    self.dictAutoTestResult['NTC-LCD'] = 0
                elif i == 5:
                    self.ui.testFan3Label.show()
                    self.ui.testFan3Label1.show()
                    self.dictAutoTest['FAN3-EVR'] = True
                    self.dictAutoTestResult['FAN3-EVR'] = 0
                elif i == 6:
                    self.ui.testTemp3Label.show()
                    self.ui.testTemp3Label1.show()
                    self.dictAutoTest['NTC-EVR'] = True
                    self.dictAutoTestResult['NTC-EVR'] = 0
            else:
                if i == 0:
                    self.ui.testMotorLabel.hide()
                    self.ui.testMotorLabel1.hide()
                    self.dictAutoTest['MOTOR'] = False
                    if 'MOTOR' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['MOTOR']
                elif i == 1:
                    self.ui.testFan1Label.hide()
                    self.ui.testFan1Label1.hide()
                    self.dictAutoTest['FAN1-LED'] = False
                    if 'FAN1-LED' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['FAN1-LED']
                elif i == 2:
                    self.ui.testFan2Label.hide()
                    self.ui.testFan2Label1.hide()
                    self.dictAutoTest['FAN2-LCD'] = False
                    if 'FAN2-LCD' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['FAN2-LCD']
                elif i == 3:
                    self.ui.testTemp1Label.hide()
                    self.ui.testTemp1Label1.hide()
                    self.dictAutoTest['NTC-LED'] = False
                    if 'NTC-LED' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['NTC-LED']
                elif i == 4:
                    self.ui.testTemp2Label.hide()
                    self.ui.testTemp2Label1.hide()
                    self.dictAutoTest['NTC-LCD'] = False
                    if 'NTC-LCD' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['NTC-LCD']
                elif i == 5:
                    self.ui.testFan3Label.hide()
                    self.ui.testFan3Label1.hide()
                    self.dictAutoTest['FAN3-EVR'] = False
                    if 'FAN3-EVR' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['FAN3-EVR']
                elif i == 6:
                    self.ui.testTemp3Label.hide()
                    self.ui.testTemp3Label1.hide()
                    self.dictAutoTest['NTC-EVR'] = False
                    if 'NTC-EVR' in self.dictAutoTestResult:
                        del self.dictAutoTestResult['NTC-EVR']
        print('selected items ', self.dictAutoTestResult)

    def read_para(self):
        if os.path.exists(FILE_PARA):
            with open(FILE_PARA, mode='r', encoding='utf-8-sig', newline='') as file:
                # 使用csv.reader()将文件中的每行数据读入到一个列表中
                reader = csv.reader(file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
                # csv.DictWriter() #以字典的形式读写数据
                # 遍历列表将数据按行输出
                result = list(reader)
                if len(result[0]) > 0:
                    self.ui.ntcThresholdLowerEdit.setText(str(result[0][0]))
                    self.ui.ntcThresholdUpperEdit.setText(str(result[0][1]))
            file.close()
            return result

    def save_para(self):
        data = [[0, 0]]
        error = True
        data[0][0] = int(self.ui.ntcThresholdLowerEdit.text())
        data[0][1] = int(self.ui.ntcThresholdUpperEdit.text())

        with open(FILE_PARA, 'w') as file:
            writer = csv.writer(file)
            for i in range(len(data)):
                writer.writerow(data[i])
        file.close()
        result = self.read_para()
        for i in range(0, len(data)):
            for j in range(0, len(data[0])):
                if int(result[i][j]) != data[i][j]:
                    error = False
        if error:
            QMessageBox.warning(self, "提示", "保存成功")
        else:
            QMessageBox.warning(self, "提示", "保存失败")

    def slot_lcd_mirror(self, index):
        print("lcd mirror ", index)
        data = [2]
        if index == 0:
            data[0] = 2
        elif index == 1:
            data[0] = 10
        elif index == 2:
            data[0] = 18
        else:
            data[0] = 26
        strHex = asu_pdu_build_one_frame('CMD_SET_LCD_MIRROR', len(data), data)
        self.serial_write(strHex)

    def mouseDoubleClickEvent(self, event):
        print(event.button)

    def show_char_img(self, v):
        show_img(0)

    def show_white_img(self, v):
        show_img(1)

    def show_black_img(self, v):
        show_img(2)

    def auto_test_pdu(self):
        text, ok = QInputDialog().getText(QWidget(), '光机序列号', '输入光机序列号:')
        if ok and text:
            print(self.ui.testItemsComboBox.get_selected())
            self.totalRounds = 0
            self.auto_test_ui_switch(False)
            self.ui.autoTestFinishLabel.setText('测试中...')
            self.sn = str(text)
            # self.ui.motorTestCycleEdit.setText(str(2))
            self.ui.snLabel.setText("SN: " + str(text))
            data = ['', '']
            data[0] = 'SN'
            data[1] = str(text)
            if self.write_result_csv('w', data):
                self.ui.autoTestButton.setEnabled(False)
                self.auto_test_motor_open()
            else:
                self.ui.autoTestButton.setEnabled(True)
                return

    def write_result_csv(self, mode='w', data=[]):

        file_name = self.sn + '.csv'
        dir_name = 'result'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        else:
            pass
        file_name = dir_name + "/" + file_name
        try:
            with open(file_name, mode=mode, newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data)
                csvfile.close()
            return True
        except:
            print('文件打开异常')
            res = QMessageBox.warning(self, "警告", "必须先关闭已打开的文件！",
                                      QMessageBox.Yes | QMessageBox.No)
            if QMessageBox.Yes == res:
                print("[warn] you clicked yes button!")
            elif QMessageBox.No == res:
                print("[warn] you clicked no button!")
            return False

    def auto_test_ui_switch(self, switch=False):
        if switch:
            passPix = QPixmap('pic/pass.png')
            self.ui.testTemp3Label.setPixmap(passPix)
            self.ui.testTemp2Label.setPixmap(passPix)
            self.ui.testTemp1Label.setPixmap(passPix)
            self.ui.testFan3Label.setPixmap(passPix)
            self.ui.testFan2Label.setPixmap(passPix)
            self.ui.testFan1Label.setPixmap(passPix)
        else:
            failPix = QPixmap('pic/fail.png')
            self.ui.testTemp3Label.setPixmap(failPix)
            self.ui.testTemp2Label.setPixmap(failPix)
            self.ui.testTemp1Label.setPixmap(failPix)
            self.ui.testFan3Label.setPixmap(failPix)
            self.ui.testFan2Label.setPixmap(failPix)
            self.ui.testFan1Label.setPixmap(failPix)
            self.ui.testMotorLabel.setPixmap(failPix)

    def open_pgu_led(self):
        if self.mPguLedFlag:
            data = [0]
            self.mPguLedFlag = False
            self.ui.openLedButton.setText('打开光机')
        else:
            data = [1]
            self.mPguLedFlag = True
            self.ui.openLedButton.setText('关闭光机')
        print("PGU LED ", self.mPguLedFlag)
        # 步数用两个字节表示，低字节在前，高字节在后
        strHex = asu_pdu_build_one_frame('CMD_SET_DISPLAY', len(data), data)
        self.serial_write(strHex)

    def auto_test_motor_open(self):
        print('auto test motor open')
        self.autoTestThread = AutoTestThread(self, self.current_port,
                                             self.ui.motorStepsRoundEdit.text(),
                                             self.ui.motorTestCycleEdit.text())
        self.autoTestThread.start()
        self.autoTestThread.update_motor_signal.connect(self.update_motor_info)

    def auto_test_motor_close(self):
        self.autoTestThread.exitFlag = True
        self.autoTestThread.exit(0)

    def update_motor_info(self):
        self.ui.motorStatuslabel.setStyleSheet("color:white")
        self.ui.motorStatuslabel.setText("马达运行中")
        self.ui.totalRoundLabel.setText(str(self.autoTestThread.count))

    def motor_back(self):
        data = [1, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.serial_write(strHex)

    def motor_forward(self):
        data = [0, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.serial_write(strHex)

    def save_pdu_data(self):
        data = [0]
        strHex = asu_pdu_build_one_frame('CMD_SAVE_PARAMRTER', len(data), data)
        self.serial_write(strHex)

    def update_temperature(self):
        if self.current_port is not None:
            if self.update_temp_flag:
                self.update_temp_flag = False
                self.update_data_timer.stop()
                self.ui.updateTempButton.setText('启动定时')
                self.ui.tempFlagLabel.setText('关闭')

            else:
                self.update_temp_flag = True
                self.update_data_timer.start(int(self.ui.updateTempEdit.text()))
                self.ui.updateTempButton.setText('关闭定时')
                self.ui.tempFlagLabel.setText('打开')
        else:
            print('请先打开串口！！！')

    def set_fan_speed(self):
        # data = list()
        data = [0, 0, 0, 1]
        data[0] = 100 - int(self.ui.fan1HorizontalSlider.value())
        data[1] = 100 - int(self.ui.fan2HorizontalSlider.value())
        data[2] = 100 - int(self.ui.fan3HorizontalSlider.value())
        print(">>>>>>>>>> set fan speed ", data)
        strHex = asu_pdu_build_one_frame('CMD_SET_FANS', len(data), data)
        self.serial_write(strHex)
        time.sleep(0.05)

    def set_current(self):
        data = [0, 0, 0]
        data[0] = int(self.ui.redHorizontalSlider.value())
        data[1] = int(self.ui.greenHorizontalSlider.value())
        data[2] = int(self.ui.blueHorizontalSlider.value())
        strHex = asu_pdu_build_one_frame('CMD_SET_CURRENTS', len(data), data)
        self.serial_write(strHex)
        time.sleep(0.05)

    def set_panel_brightness(self):
        data = [0]
        data[0] = int(self.ui.panelPwmHorizontalSlider.value())
        strHex = asu_pdu_build_one_frame('CMD_SET_PANEL_PWM', len(data), data)
        self.serial_write(strHex)
        time.sleep(0.05)

    def set_max_current(self):
        data = [0, 0, 0, 0, 0, 0]
        data[0] = int(self.ui.redMaxHorizontalSlider.value()) & 0x00FF
        data[1] = (int(self.ui.redMaxHorizontalSlider.value()) & 0xFF00) >> 8
        data[2] = int(self.ui.greenMaxHorizontalSlider.value()) & 0x00FF
        data[3] = (int(self.ui.greenMaxHorizontalSlider.value()) & 0xFF00) >> 8
        data[4] = int(self.ui.blueMaxHorizontalSlider.value()) & 0x00FF
        data[5] = (int(self.ui.blueMaxHorizontalSlider.value()) & 0xFF00) >> 8
        strHex = asu_pdu_build_one_frame('CMD_SET_MAX_CURRENTS', len(data), data)
        self.serial_write(strHex)
        time.sleep(0.05)

    def update_data(self):
        print('>>>>>>>>>> get ntc data')
        data = [0, 0]
        strHex = asu_pdu_build_one_frame('CMD_GET_TEMPS', 2, data)
        self.serial_write(strHex)
        # self.ui.posValueLabel.setText(position)
        # self.ui.stepsValueLabel.setText(steps)
        # self.ui.redSpinBox.setValue(20)
        # red_current_value = self.ui.redSpinBox.value()
        # print(red_current_value)

    def switch_windows_ui(self, switch):
        self.ui.frame1.setEnabled(switch)
        self.ui.frame_5.setEnabled(switch)
        self.ui.frame_9.setEnabled(switch)
        self.ui.send_data.setEnabled(switch)
        self.ui.input_data.setEnabled(switch)
        self.ui.close_port.setEnabled(switch)
        # self.ui.baud_rate.setEditable(switch)
        self.ui.panelPwmHorizontalSlider.setEnabled(switch)
        self.ui.panelPwmSpinBox.setEnabled(switch)
        self.ui.openLedButton.setEnabled(switch)
        self.auto_test_ui_switch(switch)
        if switch:
            if self.mLoginOn:
                self.ui.lcdGroupBox.setEnabled(switch)
        else:
            print(switch)
            self.ui.lcdGroupBox.setEnabled(switch)

    def open_port(self):
        # print(self.mPduCmdDict)
        # print(self.mPduCmdDict['CMD_SET_CURRENTS'])
        #
        # mPduCmdDict2 = dict(zip(self.mPduCmdDict.values(), self.mPduCmdDict.keys()))
        # print(mPduCmdDict2)
        # print(mPduCmdDict2[30])
        print('>>>>>>>>>> >>>>>>>>>> 打开串口')
        current_port_name = self.ui.serial_selection.currentText()
        baud_rate = int(self.ui.baud_rate.currentText())
        bytesize = 8
        check_bit = "N"
        stop_bit = 1.0
        try:
            self.current_port = open_port(current_port_name,
                                          baudrate=baud_rate,
                                          bytesize=bytesize,
                                          parity=check_bit,
                                          stopbits=stop_bit)
        except:
            self.ui.port_status.setText(current_port_name + ' 打开失败')
            return
        if self.current_port and self.current_port.isOpen():
            self.serial_thread.start()
            # print('------------- 线程', threading.active_count())
            self.ui.port_status.setText(current_port_name + ' 打开成功')
            self.serial_thread.ser = self.current_port

            self.update_data_timer = QTimer()
            self.update_data_timer.timeout.connect(self.update_data)

            self.switch_windows_ui(True)
            self.auto_test_ui_switch(False)
            self.ui.open_port.setEnabled(False)
            self.ui.refresh_port.setEnabled(False)
            self.slot_lcd_mirror(2)
            self.ui.hwLabel.setText('')
            self.ui.statusbar.addPermanentWidget(self.ui.hwLabel, stretch=1)
            time.sleep(1)
            self.get_hw_version()
        else:
            self.ui.port_status.setText(current_port_name + ' 打开失败')

    def close_port(self):
        if self.current_port is not None:
            # self.serial_thread.quit()
            # self.serial_thread.wait()
            self.serial_thread.ser = None  # 没有正常退出，不可以，后面继续研究
            # self.repeat_send_timer.stop()
            self.current_port.flushInput()
            self.current_port.flushOutput()
            self.current_port.close()
            self.ui.port_status.setText(self.current_port.port + ' 关闭成功')
            self.update_data_timer.stop()
            self.switch_windows_ui(False)
            self.ui.open_port.setEnabled(True)
            self.ui.refresh_port.setEnabled(True)
            self.ui.hwLabel.setText('')
            self.ui.statusbar.addPermanentWidget(self.ui.hwLabel, stretch=1)
            self.current_port = None
        else:
            self.ui.port_status.setText('无串口可关闭')

    def refresh_port(self):
        """
        刷新串口
        :return:
        """
        available_ports = get_ports()
        self.ui.serial_selection.clear()
        self.ui.serial_selection.addItems(available_ports)

    def receive_data(self):
        # receive_ascii_format = self.ui.receive_ascii_format.isChecked()
        reverseSteps = 0

        data = ['', '']
        actualSteps = 0
        self.ui.receive_data_area.clear()
        receive_ascii_format = False
        raw_data_list = self.serial_thread.current_data
        self.current_port.flushInput()
        # cmd_data = ()  # 如果下面不分开，通过元祖接收
        cmd, length, dataList = asu_pdu_parse_one_frame(raw_data_list)
        print("uart receive data : ", cmd, length, dataList)
        if cmd in mPduCmdDict2Rev.keys():
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_VERSION':
                hw_version = str(dataList[0]) + "." \
                             + str(dataList[1]) + "." \
                             + str(dataList[2]) + " "
                del dataList[0:3]
                dataList.insert(12, 32)
                dataList.insert(12, 32)
                for i in range(0, len(dataList)):
                    hw_version = hw_version + chr(dataList[i])
                hw_version = 'HW: ' + hw_version
                self.ui.hwLabel.setText(hw_version)
                self.ui.statusbar.addPermanentWidget(self.ui.hwLabel, stretch=1)
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_TEMPS':
                print('>>>>>>>>>> Uart receive CMD_GET_TEMPS')
                # 根据电压检索对应的温度值
                temp1 = int(hex(dataList[4] << 8), 16) + int(hex(dataList[3]), 16)
                temp2 = int(hex(dataList[6] << 8), 16) + int(hex(dataList[5]), 16)
                temp3 = int(hex(dataList[8] << 8), 16) + int(hex(dataList[7]), 16)
                val1, val2, val3 = 0, 0, 0
                for i in range(1, len(self.cols_voltage)):
                    if temp1 < int(self.cols_voltage[i] * 1000):
                        val1 = i
                    if temp2 < int(self.cols_voltage[i] * 1000):
                        val2 = i
                    if temp3 < int(self.cols_voltage[i] * 1000):
                        val3 = i
                if self.dictAutoTest['NTC-LED']:
                    data[0] = 'NTC-LED'
                    if int(self.ui.ntcThresholdLowerEdit.text()) < val2 < int(self.ui.ntcThresholdUpperEdit.text()):
                        data[1] = 'pass'
                        self.dictAutoTestResult['NTC-LED'] += 1
                    else:
                        data[1] = 'fail'
                        self.dictAutoTestResult['NTC-LED'] -= 1
                if self.dictAutoTest['NTC-LCD']:
                    data[0] = 'NTC-LCD'
                    if int(self.ui.ntcThresholdLowerEdit.text()) < val3 < int(self.ui.ntcThresholdUpperEdit.text()):
                        self.dictAutoTestResult['NTC-LCD'] += 1
                        data[1] = 'pass'
                    else:
                        data[1] = 'fail'
                        self.dictAutoTestResult['NTC-LCD'] -= 1
                    # self.write_result_csv('a', data)
                if self.dictAutoTest['NTC-EVR']:
                    if int(self.ui.ntcThresholdLowerEdit.text()) < val1 < int(self.ui.ntcThresholdUpperEdit.text()):
                        # self.ui.testTemp3Label.setPixmap(passPix)
                        data[1] = 'pass'
                        self.write_result_csv('a', data)
                        self.dictAutoTestResult['NTC-EVR'] += 1
                    else:
                        data[1] = 'fail'
                        # self.ui.testTemp3Label.setPixmap(failPix)
                        self.dictAutoTestResult['NTC-EVR'] -= 1
                    # self.write_result_csv('a', data)
                self.ui.temp1VoltageLabel.setText(str(temp1 / 1000))
                self.ui.temp2VoltageLabel.setText(str(temp2 / 1000))
                self.ui.temp3VoltageLabel.setText(str(temp3 / 1000))
                self.ui.temp1Label.setText(str(int(val1 + 1)))  # EVR
                self.ui.temp2Label.setText(str(int(val2 + 1)))  # LED
                self.ui.temp3Label.setText(str(int(val3 + 1)))  # LCD
                self.mNtcFinished = True
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_FANS':
                print('>>>>>>>>>> Uart receive CMD_GET_FANS')
                if self.dictAutoTest['FAN1-LED']:
                    data[0] = 'FAN1-LED'
                    if dataList[1] == 1:
                        data[1] = 'pass'
                        # self.ui.testFan1Label.setPixmap(passPix)
                        self.dictAutoTestResult['FAN1-LED'] += 1
                    else:
                        data[1] = 'fail'
                        # self.ui.testFan1Label.setPixmap(failPix)
                        self.dictAutoTestResult['FAN1-LED'] -= 1
                    # self.write_result_csv('a', data)
                if self.dictAutoTest['FAN2-LCD']:
                    data[0] = 'FAN2-LCD'
                    if dataList[0] == 1:
                        data[1] = 'pass'
                        # self.ui.testFan2Label.setPixmap(passPix)
                        self.dictAutoTestResult['FAN2-LCD'] += 1
                    else:
                        data[1] = 'fail'
                        # self.ui.testFan2Label.setPixmap(failPix)
                        self.dictAutoTestResult['FAN2-LCD'] -= 1
                    # self.write_result_csv('a', data)
                if self.dictAutoTest['FAN3-EVR']:
                    data[0] = 'FAN3-EVR'
                    if dataList[2] == 1:
                        data[1] = 'pass'
                        # self.ui.testFan3Label.setPixmap(passPix)
                        self.dictAutoTestResult['FAN3-EVR'] += 1
                    else:
                        data[1] = 'fail'
                        # self.ui.testFan3Label.setPixmap(failPix)
                        self.dictAutoTestResult['FAN3-EVR'] -= 1
                    # self.write_result_csv('a', data)
                self.mFanFinished = True
            if mPduCmdDict2Rev[cmd] == 'CMD_SET_FOCUSMOTOR':
                print('>>>>>>>>>> Uart receive CMD_SET_FOCUSMOTOR')
                print(">>>>>>>>>> motor callback data : ", cmd, dataList)
                if dataList[0] == 1:
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达限位")
                    self.dictAutoTestResult['MOTOR'] += 1
                    self.limitSteps = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                    print('马达限位 limitSteps ', self.limitSteps)
                elif dataList[0] == 2:
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达回转结束")
                    reverseSteps = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                    actualSteps = self.limitSteps - reverseSteps
                    self.totalSteps = self.totalSteps + actualSteps
                    print('马达回转结束 limitSteps ', self.limitSteps, reverseSteps, actualSteps)
                    self.mMotorFinished = True
                elif dataList[0] == 0:
                    self.ui.motorStatuslabel.setStyleSheet("color:black")
                    self.ui.motorStatuslabel.setText("马达步进结束")
                    actualSteps = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                    # self.mMotorFinished = True
                else:
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达异常")
                    print("返回错误", dataList[0])
                self.ui.actualStepsLabel.setText(str(actualSteps))
            self.ui.port_status.setText('数据设置状态: 成功')
        else:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! cmd %d is not found' % cmd)
            self.ui.port_status.setText('数据设置失败')

        try:
            if receive_ascii_format:
                current_data = self.serial_thread.current_data.decode('utf-8')
            else:
                current_data = self.serial_thread.current_data.hex()
                # print("receive data hex : ", self.serial_thread.current_data)
                # print("receive data hex ", current_data[2])

                # asu_parse_one_frame(current_data)
                data_list = re.findall('.{2}', current_data)
                # print("receive data data_list len : ", str2hex(data_list[2]))
                # result = map(hex(), data_list)
                # print("receive data len ", result[2])
                # print("receive data data_list ", int(data_list[2]) + int(data_list[3]) + int(data_list[4]))
                # print("receive data data_list : ", int(data_list[3]))
                # print(len(data_list), data_list[0], data_list[1], data_list[2])
                current_data = ' '.join(data_list) + ' '
                # print("receive data X : ", current_data)
            # if self.ui.auto_new_line.checkState() == Qt.Checked and self.ui.show_time.checkState() == Qt.Checked:
            #     current_data = datetime.datetime.now().strftime('%H:%M:%S') + ' ' + current_data
            # if self.ui.auto_new_line.checkState() == Qt.Checked:
            #     current_data += '\n'
            self.ui.receive_data_area.insertPlainText(current_data)
            # if self.ui.scroll_show.isChecked():
            #     self.ui.receive_data_area.verticalScrollBar().setValue(
            #         self.ui.receive_data_area.verticalScrollBar().maximum())
            # self.ui.receive_data_status.setText('数据接收状态: 成功')
            # self.ui.port_status.setText('数据接收状态: 成功')
        except:
            pass
            # self.ui.port_status.setText('数据接收状态: 失败')

    def send_data(self):
        """
        数据发送
        :return:
        """
        global count
        input_data = self.ui.input_data.toPlainText()
        if not check_hex(input_data):
            print("非法字符")
            QMessageBox.information(self, "输入错误",
                                    "必输输入16进制：{}\n\ntype: {}".format(input_data, type(input_data)),
                                    QMessageBox.Yes | QMessageBox.No)
            return
        # send_ascii_format = self.ui.send_ascii_format.isChecked()
        send_ascii_format = False
        print(input_data, send_ascii_format)
        try:
            if send_ascii_format:
                self.serial_write(input_data.encode('utf-8'))
            else:
                list1 = ["FC FC 01 04 0D 02 02 FF 15 FB FB", "00 02 00 06 00 01 09", "00 02 00 06 00 01 10"]
                list2 = "01 02 03 04 05 06"
                Hex_str = bytes.fromhex(input_data)
                print("Hex_str : ", Hex_str)
                # count = count + 1
                # print("count : %d", count)
                # if count > 2:
                #     count = 0
                self.serial_write(Hex_str)
                self.ui.port_status.setText('数据发送状态: 成功')
        except:
            self.ui.port_status.setText('数据发送状态: 失败')

    def admin_password_logon(self):
        if self.current_port is not None:
            self.mLoginOn = True
            if self.ui.adminPasswordEdit.text() == '123qwe':
                self.ui.lcdGroupBox.setEnabled(True)
                self.ui.frame_9.setEnabled(True)
            else:
                QMessageBox.warning(self, "警告", "输入密码错误")
        else:
            QMessageBox.warning(self, "警告", "请先打开串口！")

    def serial_write(self, strHex):
        try:
            self.current_port.write(strHex)
            return True
        except Exception as result:
            if str(result).find('PermissionError') >= 0 and str(result).find('WriteFile failed') >= 0:
                QMessageBox.warning(self, "串口异常", "请先确定硬件串口是否连接，关闭串口后重新打开串口")
                # print(traceback.format_exc())
            else:
                print('不存在')
            return False

    def get_hw_version(self):
        strHex = asu_pdu_build_one_frame('CMD_GET_VERSION', 0, None)
        self.serial_write(strHex)

    def read_ntc_excel(self):
        # 打开文件，xlrd.open_workbook()，函数中参数为文件路径，分为相对路径和绝对路径
        workBook = xlrd.open_workbook(NTC_VOLTAGE_TEMP)  # r''
        # 获取所有sheet的名字(list类型)
        allSheetNames = workBook.sheet_names()
        print(allSheetNames)
        # 按索引号获取单个sheet的名字（string类型）
        sheet1Name = workBook.sheet_names()[0]
        print(sheet1Name)

        # 获取sheet内容
        ## 按索引号获取sheet内容
        # sheet1_content1 = workBook.sheet_by_index(0);  # sheet索引从0开始
        ## 按sheet名字获取sheet内容，workBook.sheet_by_name()括号内的参数是sheet的真实名字
        sheet1_content1 = workBook.sheet_by_name('Table2')

        # 获取sheet的名称，行数，列数
        print(sheet1_content1.name, sheet1_content1.nrows, sheet1_content1.ncols)

        # 获取整行和整列的值（数组）
        # rows = sheet1_content1.row_values(3)  # 获取第四行内容
        self.cols_temp = sheet1_content1.col_values(2)  # 获取第三列内容
        self.cols_voltage = sheet1_content1.col_values(5)  # 获取第三列内容
        # print(type(cols_temp), cols_temp)
        # print('\n\r')
        # print(cols_voltage)
        # 使用循环获得多行的数据并保存到table中，获得多列数据是同样的方法
        table = []  # 定义一个空列表，将读取的每一行数据保存到该列表中
        for i in range(sheet1_content1.nrows):
            rows = sheet1_content1.row_values(i)
            table.append(rows)
        print(rows)

        # 获取单元格内容(三种方式)
        print(sheet1_content1.cell(1, 0).value)
        print(sheet1_content1.cell_value(2, 2))
        print(sheet1_content1.row(2)[2].value)

        # 获取单元格内容的数据类型
        # Tips: python读取excel中单元格的内容返回的有5种类型 [0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error]
        print(sheet1_content1.cell(1, 0).ctype)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下
            # self.setText("单击鼠标左键的事件: 自己定义")
            print("单击鼠标左键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.RightButton:  # 右键按下
            # self.setText("单击鼠标右键的事件: 自己定义")
            cv2.destroyAllWindows
            print("单击鼠标右键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.MidButton:  # 中键按下
            # self.setText("单击鼠标中键的事件: 自己定义")
            print("单击鼠标中键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.RightButton:  # 左右键同时按下
            # self.setText("同时单击鼠标左右键的事件: 自己定义")
            print("单击鼠标左右键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.MidButton:  # 左中键同时按下
            # self.setText("同时单击鼠标左中键的事件: 自己定义")
            print("单击鼠标左中键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.MidButton | QtCore.Qt.RightButton:  # 右中键同时按下
            # self.setText("同时单击鼠标右中键的事件: 自己定义")
            print("单击鼠标右中键")  # 响应测试语句
        elif event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.MidButton \
                | QtCore.Qt.RightButton:  # 左中右键同时按下
            # self.setText("同时单击鼠标左中右键的事件: 自己定义")
            print("单击鼠标左中右键")  # 响应测试语句


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=DarkPalette()))
    w = ProjectorWindow()
    w.resize(1239, 900)
    w.show()
    sys.exit(app.exec_())
