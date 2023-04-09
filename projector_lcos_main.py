import csv
import re
import string
import threading

import cv2
from PyQt5.QtGui import QPixmap, QTextCharFormat

from log_utils import Logger

# import serial
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
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
import shutil


class SerialThread(QThread):
    data_arrive_signal = pyqtSignal(name='serial_data')

    def __init__(self, ser=None):
        super().__init__()
        self.ser = ser
        self.current_data = b''

    def run(self):
        time.sleep(1)  # 防止直接进循环, 阻塞主ui
        while True:
            try:
                if self.ser is not None and self.ser.inWaiting():
                    self.current_data = self.ser.read(self.ser.inWaiting())
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
        self.circle = circle
        self.exitFlag = False

    def run(self):
        # time.sleep(1)  # 防止直接进循环, 阻塞主ui
        print('AutoTestThread init circle', self.circle)
        data = [1, 0, 0]
        while self.count < int(self.circle):
            preTime = time.time()
            if self.exitFlag:
                self.exitFlag = False
                print(">>>>>>>>>> AutoTestThread Exit ", self.count)
                break
            try:
                if self.ser is not None:
                    self.update_motor_signal.emit()
                    # set fan speed
                    self.win.ui.fan1SpinBox.setValue(100)
                    self.win.ui.fan2SpinBox.setValue(100)
                    self.win.ui.fan3SpinBox.setValue(100)
                    time.sleep(2)
                    # get ntc
                    self.win.update_data()
                    time.sleep(2)
                    # get fan statue
                    strHex = asu_pdu_build_one_frame('CMD_GET_FANS', 0, None)
                    self.ser.write(strHex)
                    time.sleep(2)
                    # set motor
                    # # 步数用两个字节表示，低字节在前，高字节在后
                    data[1] = int(self.roundSteps) & 0x00FF
                    data[2] = int(self.roundSteps) >> 8
                    print('AutoTestThread', data, self.count)
                    strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
                    self.ser.write(strHex)
                    time.sleep(6)

                    if data[0] == 1:
                        data[0] = 0
                    else:
                        data[0] = 1
                    print('>>>>>>>>>> 自动化测试结束 ', self.count)
                    self.count += 1
            except:
                print('串口错误')
        self.win.ui.autoTestFinishLabel.setStyleSheet("color:green")
        self.win.ui.autoTestFinishLabel.setText('测试完成')
        nowTime = time.time()
        totalTime = nowTime - preTime
        print('累计时间：', totalTime)
        print(self.count, self.circle)
        if self.count != self.circle:
            print('测试完成!!!')


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    update_temp_flag = False
    mPguLedFlag = False

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('调试工具')
        self.initialize_ui()

        self.ui.adminPasswordButton.clicked.connect(self.admin_password_logon)
        self.ui.getSwVerButton.clicked.connect(self.get_sw_version)
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
        self.serial_thread.start()
        self.serial_thread.data_arrive_signal.connect(self.receive_data)
        self.autoTestThread = None

        pix = QPixmap('op01_char.jpg')
        self.ui.imageCharLabel.setStyleSheet("border: 3px solid red")
        self.ui.imageCharLabel.setScaledContents(True)
        self.ui.imageCharLabel.setPixmap(pix)
        self.ui.imageCharLabel.mousePressEvent = self.show_char_img

        pix_white = QPixmap('op02_white.png')
        self.ui.imageWhiteLabel.setStyleSheet("border: 3px solid red")
        self.ui.imageWhiteLabel.setScaledContents(True)
        self.ui.imageWhiteLabel.setPixmap(pix_white)
        self.ui.imageWhiteLabel.mousePressEvent = self.show_white_img

        pix_black = QPixmap('op03_black.png')
        self.ui.imageBlackLabel.setStyleSheet("border: 3px solid red")
        self.ui.imageBlackLabel.setScaledContents(True)
        self.ui.imageBlackLabel.setPixmap(pix_black)
        self.ui.imageBlackLabel.mousePressEvent = self.show_black_img

        self.sn = '1234567890'

        # self.ui.g.etSwVerButton.setEnabled(False)
        # self.ui.redSpinBox.setEnabled(False)
        # self.ui.redHorizontalSlider.setEnabled(False)
        # self.ui.greenSpinBox.setEnabled(False)
        # self.ui.greenHorizontalSlider.setEnabled(False)
        # self.ui.blueSpinBox.setEnabled(False)
        # self.ui.blueHorizontalSlider.setEnabled(False)

    def mouseDoubleClickEvent(self, event):
        print(event.button)

    def show_char_img(self, v):
        img_bgr = cv2.imread("op01_char.jpg")
        cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow("myImage", 0, 0)
        cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("myImage", img_bgr)
        val = cv2.waitKey(0)
        print(v, val)
        cv2.destroyAllWindows()

    def show_white_img(self, v):
        img_bgr = cv2.imread("op02_white_test.png")
        val = img_bgr.shape

        print(img_bgr.shape)
        print(img_bgr[0, 0])
        cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow("myImage", 0, 0)
        cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("myImage", img_bgr)
        val = cv2.waitKey(0)
        print(v, val)
        cv2.destroyAllWindows()

    def show_black_img(self, v):
        img_bgr = cv2.imread("op03_black.png")
        cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow("myImage", 0, 0)
        cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("myImage", img_bgr)
        val = cv2.waitKey(0)
        print(v, val)
        cv2.destroyAllWindows()

    def auto_test_pdu(self):
        text, ok = QInputDialog().getInt(QWidget(), '光机序列号', '输入光机序列号:')
        if ok and text:
            self.auto_test_ui_switch(False)
            self.ui.autoTestFinishLabel.setText('测试中...')
            self.sn = str(text)
            # self.ui.motorTestCycleEdit.setText(str(2))
            self.ui.snLabel.setText("SN: " + str(text))
            data = ['', '']
            data[0] = 'SN'
            data[1] = str(text)
            if self.write_result_csv('w', data):
                self.auto_test_motor_open()
            else:
                return
            # self.ui.receive_data_area.clear()
            # self.ui.testResultTextEdit.insertPlainText("SN: " + str(text) + "\r\n")

    def write_result_csv(self, mode='w', data=[]):

        file_name = self.sn + '.csv'
        dir_name = 'result'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        else:
            print("目录已经存在")
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
        if switch is False:
            failPix = QPixmap('pic/fail.png')
            self.ui.testTemp3Label.setPixmap(failPix)
            self.ui.testTemp2Label.setPixmap(failPix)
            self.ui.testTemp1Label.setPixmap(failPix)
            self.ui.testFan3Label.setPixmap(failPix)
            self.ui.testFan2Label.setPixmap(failPix)
            self.ui.testFan1Label.setPixmap(failPix)
            self.ui.testMotorLabel.setPixmap(failPix)
        else:
            passPix = QPixmap('pic/pass.png')
            self.ui.testTemp3Label.setPixmap(passPix)
            self.ui.testTemp2Label.setPixmap(passPix)
            self.ui.testTemp1Label.setPixmap(passPix)
            self.ui.testFan3Label.setPixmap(passPix)
            self.ui.testFan2Label.setPixmap(passPix)
            self.ui.testFan1Label.setPixmap(passPix)

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
        self.current_port.write(strHex)

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
        self.ui.motorStatuslabel.setStyleSheet("color:black")
        self.ui.motorStatuslabel.setText("马达运行中")
        self.ui.totalRoundLabel.setText(str(self.autoTestThread.count))

    def motor_back(self):
        data = [1, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.current_port.write(strHex)

    def motor_forward(self):
        data = [0, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.current_port.write(strHex)

    def save_pdu_data(self):
        # PARA_CURRENT 0
        # typedef
        # enum
        # {
        #     PARA_CURRENT = 0,
        #                    PARA_FLIP,
        #                    PARA_KST,
        #                    PARA_COLOR_TEMP,
        #                    PARA_WP,
        #                    PARA_241,
        #                    PARA_LED,
        #                    PARA_FRC,
        #                    PARA_MISC,
        #                    PARA_BCHSCE,
        #                    PARA_BCHS,
        #                    PARA_CE1D,
        #                    PARA_CEBC,
        #                    PARA_CEACC,
        #                    PARA_MAX
        # }PARA_Type;
        data = [0]
        strHex = asu_pdu_build_one_frame('CMD_SAVE_PARAMRTER', len(data), data)
        self.current_port.write(strHex)

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
        strHex = asu_pdu_build_one_frame('CMD_SET_FANS', len(data), data)
        self.current_port.write(strHex)
        time.sleep(0.05)

    def set_current(self):
        data = [0, 0, 0]
        data[0] = int(self.ui.redHorizontalSlider.value())
        data[1] = int(self.ui.greenHorizontalSlider.value())
        data[2] = int(self.ui.blueHorizontalSlider.value())
        strHex = asu_pdu_build_one_frame('CMD_SET_CURRENTS', len(data), data)
        self.current_port.write(strHex)
        time.sleep(0.05)

    def set_panel_brightness(self):
        data = [0]
        data[0] = int(self.ui.panelPwmHorizontalSlider.value())
        strHex = asu_pdu_build_one_frame('CMD_SET_PANEL_PWM', len(data), data)
        self.current_port.write(strHex)
        time.sleep(0.05)

    def set_max_current(self):
        data = [0, 0, 0, 0, 0, 0]
        data[0] = int(self.ui.redMaxHorizontalSlider.value()) & 0x00FF
        data[1] = (int(self.ui.redMaxHorizontalSlider.value()) & 0xFF00) >> 8
        data[2] = int(self.ui.greenMaxHorizontalSlider.value()) & 0x00FF
        data[3] = (int(self.ui.greenMaxHorizontalSlider.value()) & 0xFF00) >> 8
        data[4] = int(self.ui.blueMaxHorizontalSlider.value()) & 0x00FF
        data[5] = (int(self.ui.blueMaxHorizontalSlider.value()) & 0xFF00) >> 8
        print(data)
        # strHex = asu_pdu_build_one_frame('CMD_SET_MAX_CURRENTS', len(data), data)
        # self.current_port.write(strHex)
        # time.sleep(0.05)

    def update_data(self):
        print('update ntc data')
        data = [0, 0]
        strHex = asu_pdu_build_one_frame('CMD_GET_TEMPS', 2, data)
        self.current_port.write(strHex)

        # self.ui.posValueLabel.setText(position)
        # self.ui.stepsValueLabel.setText(steps)
        # self.ui.redSpinBox.setValue(20)
        # red_current_value = self.ui.redSpinBox.value()
        # print(red_current_value)

    def initialize_ui(self):
        self.ui.frame1.setEnabled(False)
        self.ui.send_data.setEnabled(False)
        self.ui.input_data.setEnabled(False)
        self.ui.close_port.setEnabled(False)
        available_ports = get_ports()
        self.ui.serial_selection.addItems(available_ports)
        self.ui.baud_rate.setEditable(True)
        self.ui.baud_rate.setCurrentText("921600")
        self.auto_test_ui_switch(False)
        self.ui.panelPwmHorizontalSlider.setEnabled(False)
        self.ui.panelPwmSpinBox.setEnabled(False)

    def open_port(self):
        # print(self.mPduCmdDict)
        # print(self.mPduCmdDict['CMD_SET_CURRENTS'])
        #
        # mPduCmdDict2 = dict(zip(self.mPduCmdDict.values(), self.mPduCmdDict.keys()))
        # print(mPduCmdDict2)
        # print(mPduCmdDict2[30])
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
            self.ui.port_status.setText(current_port_name + ' 打开成功')
            self.ui.open_port.setEnabled(False)
            self.ui.close_port.setEnabled(True)
            self.ui.send_data.setEnabled(True)
            self.ui.refresh_port.setEnabled(False)
            self.serial_thread.ser = self.current_port

            self.update_data_timer = QTimer()
            self.update_data_timer.timeout.connect(self.update_data)

            self.ui.frame1.setEnabled(True)
            # self.ui.getSwVerButton.setEnabled(True)
            # self.ui.redSpinBox.setEnabled(True)
            # self.ui.redHorizontalSlider.setEnabled(True)
            # self.ui.greenSpinBox.setEnabled(True)
            # self.ui.greenHorizontalSlider.setEnabled(True)
            # self.ui.blueSpinBox.setEnabled(True)
            # self.ui.blueHorizontalSlider.setEnabled(True)
        else:
            self.ui.port_status.setText(current_port_name + ' 打开失败')

    def close_port(self):
        if self.current_port is not None:
            self.serial_thread.ser = None
            # self.repeat_send_timer.stop()
            self.current_port.close()
            self.ui.port_status.setText(self.current_port.port + ' 关闭成功')
            self.ui.open_port.setEnabled(True)
            self.ui.send_data.setEnabled(False)
            self.ui.close_port.setEnabled(False)
            # self.ui.stop_send.setEnabled(False)
            # self.ui.send_interval.setEnabled(True)
            # self.ui.repeat_send.setEnabled(True)
            self.ui.refresh_port.setEnabled(True)
            self.current_port = None
            self.update_data_timer.stop()
            self.ui.frame1.setEnabled(False)
            # self.ui.getSwVerButton.setEnabled(False)
            # self.ui.redSpinBox.setEnabled(False)
            # self.ui.redHorizontalSlider.setEnabled(False)
            # self.ui.greenSpinBox.setEnabled(False)
            # self.ui.greenHorizontalSlider.setEnabled(False)
            # self.ui.blueSpinBox.setEnabled(False)
            # self.ui.blueHorizontalSlider.setEnabled(False)
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
        reverseCount = 0
        passPix = QPixmap('pic/pass.png')
        failPix = QPixmap('pic/fail.png')
        data = ['', '']
        limitCount = 0
        actualSteps = 0
        self.ui.receive_data_area.clear()
        receive_ascii_format = False
        raw_data_list = self.serial_thread.current_data
        # cmd_data = ()  # 如果下面不分开，通过元祖接收
        cmd, length, dataList = asu_pdu_parse_one_frame(raw_data_list)
        print("uart receive data : ", cmd, length, dataList)
        if cmd in mPduCmdDict2Rev.keys():
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_VERSION':
                sw_version = str(dataList[0]) + "." \
                             + str(dataList[1]) + "." \
                             + str(dataList[2])
                self.ui.label_sw_version.setText(sw_version)
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_TEMPS':
                self.ui.temp1Label.setText(str(dataList[0]))  # EVR
                self.ui.temp2Label.setText(str(dataList[1]))  # LED
                self.ui.temp3Label.setText(str(dataList[2]))  # LCD
                temp1 = int(hex(dataList[4] << 8), 16) + int(hex(dataList[3]), 16)
                temp2 = int(hex(dataList[6] << 8), 16) + int(hex(dataList[5]), 16)
                temp3 = int(hex(dataList[8] << 8), 16) + int(hex(dataList[7]), 16)
                data[0] = 'NTC-LCD'
                if temp3 < 2000:
                    data[1] = 'pass'
                    self.ui.testTemp3Label.setPixmap(passPix)
                else:
                    data[1] = 'fail'
                    self.ui.testTemp3Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                data[0] = 'NTC-LED'
                if temp2 < 2000:
                    self.ui.testTemp2Label.setPixmap(passPix)
                    data[1] = 'pass'
                else:
                    data[1] = 'fail'
                    self.ui.testTemp2Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                data[0] = 'NTC-EVR'
                if temp1 < 2000:
                    self.ui.testTemp1Label.setPixmap(passPix)
                    data[1] = 'pass'
                    self.write_result_csv('a', data)
                else:
                    data[1] = 'fail'
                    self.ui.testTemp1Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                self.ui.temp1VoltageLabel.setText(str(temp1 / 1000))
                self.ui.temp2VoltageLabel.setText(str(temp2 / 1000))
                self.ui.temp3VoltageLabel.setText(str(temp3 / 1000))
            if mPduCmdDict2Rev[cmd] == 'CMD_SET_FOCUSMOTOR':
                print("motor callback data : ", cmd, dataList)
                limitCount = 0
                data[0] = 'MOTOR'
                if dataList[0] == 1:
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达限位")
                    data[1] = 'pass'
                    self.write_result_csv('a', data)
                    self.ui.testMotorLabel.setPixmap(passPix)
                    limitCount = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                elif dataList[0] == 2:
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达回转结束")
                    reverseCount = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                    actualSteps = limitCount - reverseCount
                elif dataList[0] == 0:
                    data[1] = 'fail'
                    self.ui.motorStatuslabel.setStyleSheet("color:black")
                    self.ui.motorStatuslabel.setText("马达步进结束")
                    actualSteps = int(hex(dataList[2] << 8), 16) + int(hex(dataList[1]), 16)
                else:
                    data[1] = 'fail'
                    self.ui.testMotorLabel.setPixmap(failPix)
                    self.ui.motorStatuslabel.setStyleSheet("color:red")
                    self.ui.motorStatuslabel.setText("马达异常", dataList[0])
                    print("返回错误")
                self.write_result_csv('a', data)
                self.ui.actualStepsLabel.setText(str(actualSteps))
                print('actualSteps', actualSteps)
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_FANS':
                data[0] = 'FAN1'
                if dataList[0] == 1:
                    data[1] = 'pass'
                    self.ui.testFan1Label.setPixmap(passPix)
                else:
                    data[1] = 'fail'
                    self.ui.testFan1Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                data[0] = 'FAN2'
                if dataList[1] == 1:
                    data[1] = 'pass'
                    self.ui.testFan2Label.setPixmap(passPix)
                else:
                    data[1] = 'fail'
                    self.ui.testFan2Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                data[0] = 'FAN3'
                if dataList[2] == 1:
                    data[1] = 'pass'
                    self.ui.testFan3Label.setPixmap(passPix)
                else:
                    data[1] = 'fail'
                    self.ui.testFan3Label.setPixmap(failPix)
                self.write_result_csv('a', data)
                print('CMD_GET_FANS')
            self.ui.port_status.setText('数据设置状态: 成功')
        else:
            print('cmd %d is not found' % cmd)
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
                self.current_port.write(input_data.encode('utf-8'))
            else:
                list1 = ["FC FC 01 04 0D 02 02 FF 15 FB FB", "00 02 00 06 00 01 09", "00 02 00 06 00 01 10"]
                list2 = "01 02 03 04 05 06"
                Hex_str = bytes.fromhex(input_data)
                print("Hex_str : ", Hex_str)
                # count = count + 1
                # print("count : %d", count)
                # if count > 2:
                #     count = 0
                self.current_port.write(Hex_str)
                self.ui.port_status.setText('数据发送状态: 成功')
        except:
            self.ui.port_status.setText('数据发送状态: 失败')

    def admin_password_logon(self):
        if self.ui.adminPasswordEdit.text() == '123qwe':
            print('check ok')
            self.ui.panelPwmHorizontalSlider.setEnabled(True)
            self.ui.panelPwmSpinBox.setEnabled(True)

    def get_sw_version(self):
        data = []
        strHex = asu_pdu_build_one_frame('CMD_GET_VERSION', 0, data)
        self.current_port.write(strHex)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ProjectorWindow()
    # w.resize(800,500)
    w.show()
    mylog = Logger('motor.log', level='debug')
    mylog.logger.debug("-------------重新启动应用-------------")
    sys.exit(app.exec_())
