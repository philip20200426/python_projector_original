import binascii
import csv
import datetime
import json
import re
import struct

import serial
import yaml
from PyQt5.QtGui import QFont, QRegExpValidator, QPalette, QColor, QPixmap

import Fmc4030
import HuiYuanRotate
import ProjectorDev
import evaluate_correct_wrapper
import pro_correct_wrapper
from AutoFocusCalThread import AutoFocusCalThread
from ExCamAfThread import ExCamAfThread
from Fmc4030 import rail_forward, rail_position, init, rail_forward_pos, rail_stop
from math_utils import CRC
from pathlib import Path

import cv2
import qdarkstyle
from PyQt5.QtCore import Qt, QBasicTimer, QRegExp
from qdarkstyle import DarkPalette

from AutoCalThread import AutoCalThread
import globalVar
from pro_correct_wrapper import *
# from learn_serial.pro_correct_wrapper import keystone_correct_cam_libs
from CameraThread import CameraThread

from log_utils import Logger

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QStatusBar
import os, sys

from utils import check_hex, move_file
from projector_cal import Ui_MainWindow
import time
from serial_utils import get_ports, open_port, str2hex, asu_pdu_parse_one_frame, ser_send
import shutil
from ctypes import *

import os
import shutil
import socket
import matplotlib.pyplot as plt

# class AutoCalThread(QThread):
#
#     def __init__(self, win=None):
#         super().__init__()
#         self.win = win
#
#     def run(self):
#         time.sleep(1)  # 防止直接进循环, 阻塞主ui
#         while True:
#             # position 1
#             # self.win.save_data()
#             print('>>>>>>>>>>>>>>>>>>>>> AutoCalThread ')
VERSION = 'Version: 0.01 202311051350'

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
                print('>>>>>>>>> 串口异常')
                return


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    label_used_time_text = 0

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('全向梯形标定工具')
        self.initialize_ui()

        # 实例化状态栏
        self.statusBar = QStatusBar()
        self.statusBar_1 = QLabel('{:<40}'.format('状态1'))
        self.statusBar_2 = QLabel('{:^40}'.format('状态2'))
        self.statusBar_3 = QLabel('{:>40}'.format('状态3'))
        self.statusBar_4 = QLabel('{:<40}'.format('状态4'))
        self.statusBar.addWidget(self.statusBar_1, 1)
        self.statusBar.addWidget(self.statusBar_2, 1)
        self.statusBar.addWidget(self.statusBar_3, 1)
        self.statusBar.addWidget(self.statusBar_4, 1)
        # 设置状态栏，类似布局设置
        self.setStatusBar(self.statusBar)
        self.statusBar_1.setText(VERSION)

        self.ui.openTangSengButton.clicked.connect(self.start_mtf_test_activity)
        self.ui.writeDataNv.clicked.connect(self.write_to_nv)
        self.ui.saveLa.clicked.connect(self.save_laplace)
        self.ui.cleanLa.clicked.connect(self.clean_laplace)
        self.ui.openRotateButton.clicked.connect(self.open_rotate)
        self.ui.closeRotateButton.clicked.connect(self.close_rotate)
        self.ui.openRailButton.clicked.connect(self.open_rail)
        self.ui.closeRailButton.clicked.connect(self.close_rail)
        self.ui.currentPositionButton.clicked.connect(self.get_rail_position)
        self.ui.evalCorrectButton.clicked.connect(self.evaluate_kst_correct)

        self.ui.getMotorPosButton.clicked.connect(self.get_motor_position)
        self.ui.doMotorPosButton.clicked.connect(self.execute_motor_position)
        self.ui.resetRailButton.clicked.connect(self.reset_rail)
        self.ui.railForewardButton.clicked.connect(self.rail_forward)
        self.ui.railReversalButton.clicked.connect(self.rail_reversal)
        self.ui.railPositionButton.clicked.connect(self.rail_absolute_position)
        self.ui.exCamAfButton.clicked.connect(self.ex_cam_af)
        self.ui.autoFocusMotorButton.clicked.connect(self.auto_focus_motor)
        self.ui.autoFocusCalButton.clicked.connect(self.auto_focus_cal)
        self.ui.rotateButton.clicked.connect(self.rotating_platform_angle)
        self.ui.uninstallAppButton.clicked.connect(self.uninstall_app)
        self.ui.installAppButton.clicked.connect(self.install_app)
        self.ui.positionButton.clicked.connect(self.manual_position)
        self.ui.stopAutoCalButton.clicked.connect(self.stop_auto_cal)
        self.ui.kstResetButton.clicked.connect(self.kst_reset)
        self.ui.camInterCalButton.clicked.connect(self.cam_inter_cal)
        self.ui.camAfButton.clicked.connect(self.auto_focus_vision)
        self.ui.tofAfButton.clicked.connect(self.auto_focus_tof)
        self.ui.autoTofKsdButton.clicked.connect(self.auto_keystone_tof)
        self.ui.autoCamKstButton.clicked.connect(self.auto_keystone_cam)
        self.ui.kstCalButton.clicked.connect(self.kst_calibrate)
        self.ui.parceCalDataButton.clicked.connect(self.parce_cal_data)
        self.ui.kstAutoCalButton.clicked.connect(self.kst_auto_calibrate)
        self.ui.refreshKsdButton.clicked.connect(self.refresh_keystone)
        self.ui.motorForwardButton.clicked.connect(self.motorForward)
        self.ui.motorBackButton.clicked.connect(self.motorBack)
        self.ui.motorResetButton.clicked.connect(self.motorReset)
        self.ui.showWritePatternButton.clicked.connect(self.showWritePattern)
        self.ui.showCheckerPatternButton.clicked.connect(self.showCheckerPattern)
        self.ui.removePatternButton.clicked.connect(self.removePattern)
        self.ui.saveDataButton.clicked.connect(self.save_data)
        self.ui.startTestActivityButton.clicked.connect(self.start_test_activity)
        self.ui.startServiceButton.clicked.connect(self.start_service)
        self.ui.pullDataButton.clicked.connect(self.pull_data)
        self.ui.takePictureButton.clicked.connect(self.take_picture)
        self.ui.openCamButton.clicked.connect(self.open_camera)
        self.ui.closeCamButton.clicked.connect(self.close_camera)
        self.ui.cleanButton.clicked.connect(self.clean_data)
        self.ui.rootButton.clicked.connect(self.root_device)
        self.ui.open_port.clicked.connect(self.open_port)
        self.ui.close_port.clicked.connect(self.close_port)
        self.ui.refresh_port.clicked.connect(self.refresh_port)
        self.ui.send_data.clicked.connect(self.send_data)
        self.ui.eOpenCameraButton.clicked.connect(self.open_external_camera)
        self.ui.eCloseCameraButton.clicked.connect(self.close_external_camera)
        self.ui.eTakePictureButton.clicked.connect(self.external_take_picture)
        self.ui.exTimesHorizontalSlider.valueChanged['int'].connect(self.set_exposure_time)
        self.ui.delay1Edit.textChanged.connect(self.set_exposure_time)
        self.ui.delay2Edit.textChanged.connect(self.set_exposure_time)
        self.ui.delay3Edit.textChanged.connect(self.set_exposure_time)
        self.ui.snEdit.textChanged.connect(self.sn_changed)
        self.ui.frame_2.hide()
        self.hy_enable = True
        self.hui_yuan = HuiYuanRotate.open_hy_dev()
        # self.close_ui()
        # self.ui.frame.setEnabled(False)
        # self.ui.frame_left_up.setEnabled(False)
        # self.init_status_bar()

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        # self.serial_thread.start()
        # self.serial_thread.data_arrive_signal.connect(self.receive_data)

        self.auto_cal_thread = None
        self.auto_cal_thread = AutoCalThread(self.current_port, self)

        self.autofocus_cal_thread = None
        self.autofocus_cal_thread = AutoFocusCalThread(self.current_port, self)
        self.ex_cam_af_thread = ExCamAfThread(self.current_port, self)
        # self.ex_cam_af_thread.camera_arrive_signal.connect(self.image_callback)  # 设置任务线程发射信号触发的函数

        # self.update_data_timer = QTimer()
        # self.update_data_timer.timeout.connect(self.update_data)
        # self.update_data_timer.start(1000)
        self.ui.rootButton.setText("打开设备")

        self.count = 0

        # lbl = QLabel(self)
        # pixmap = QPixmap('out.jpeg')  # 按指定路径找到图片
        # self.ui.previewLabel.setPixmap(pixmap)
        self.exposureTime = 10000
        self.cameraThread = None
        self.cal = False
        self.ui.autoTofKsdButton.setEnabled(True)

        self.cameraThread = CameraThread(1, "CameraThread", float(self.ui.exTimeSpinBox.text()))
        self.cameraThread.camera_arrive_signal.connect(self.image_callback)  # 设置任务线程发射信号触发的函数

        self.mCount = 0

        self.CRC = CRC()
        self.ui.snEdit.setFocus()
        self.lst_degree = [-100, -100, -100]

        reg0 = QRegExp('[0-9-]+$')
        validator0 = QRegExpValidator()
        validator0.setRegExp(reg0)
        self.ui.xyEdit.setValidator(validator0)
        self.ui.yzEdit.setValidator(validator0)
        self.ui.xzEdit.setValidator(validator0)

        reg = QRegExp('[a-zA-Z0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)
        self.ui.snEdit.setValidator(validator)
        # 进度条设置
        # self.pgb = QProgressBar(self)
        # self.pgb.move(50, 50)
        # self.pgb.resize(250, 20)
        self.ui.autoCalProgressBar.setStyleSheet(
            "QProgressBar { border: 2px solid grey; border-radius: 5px; color: rgb(20,20,20);  background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background-color: rgb(100,200,200); border-radius: 10px; margin: 0.1px;  width: 1px;}")
        ## 其中 width 是设置进度条每一步的宽度
        ## margin 设置两步之间的间隔
        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setWeight(30)
        self.ui.autoCalProgressBar.setFont(font)
        # 设置一个值表示进度条的当前进度
        self.pv = 0
        # 申明一个时钟控件
        self.timer1 = QBasicTimer()
        # 设置进度条的范围
        self.ui.autoCalProgressBar.setMinimum(0)
        self.ui.autoCalProgressBar.setMaximum(100)
        self.ui.autoCalProgressBar.setValue(self.pv)
        ## 设置进度条文字格式
        self.ui.autoCalProgressBar.setFormat(
            'Loaded  %p%'.format(self.ui.autoCalProgressBar.value() - self.ui.autoCalProgressBar.minimum()))
        self.lap_list = []
        # 初始化外部相机曝光参数
        dir_exit = os.path.isdir('res')
        if not dir_exit:
            os.mkdir('res')
        else:
            if os.path.isfile('res/para.json'):
                file = open('res/para.json', )
                dic = json.load(file)
                if len(dic) > 0 and 'ExposureTime' in dic.keys():
                    self.ui.exTimeSpinBox.setValue(int(dic['ExposureTime']))
                if len(dic) > 0 and 'delay1' in dic.keys():
                    self.ui.delay1Edit.setText(str(dic['delay1']))
                if len(dic) > 0 and 'delay2' in dic.keys():
                    self.ui.delay2Edit.setText(str(dic['delay2']))
                if len(dic) > 0 and 'delay3' in dic.keys():
                    self.ui.delay3Edit.setText(str(dic['delay3']))
                print(dic)
                file.close()

    def image_callback(self, image):  # 这里的image就是任务线程传回的图像数据,类型必须是已经定义好的数据类型
        try:
            if self.cameraThread.mRunning or self.ex_cam_af_thread.mRunning:
                self.ui.previewCameraLabel.setPixmap(image)
            else:
                self.ui.previewCameraLabel.setPixmap(QPixmap(""))
                self.ui.previewCameraLabel.setText('CAM已关闭')
                print('关闭工业相机')
        except:
            print('图片显示异常', image)
        return None

    def close_ui(self):
        self.ui.camAfButton.setEnabled(False)
        self.ui.tofAfButton.setEnabled(False)
        self.ui.autoTofKsdButton.setEnabled(True)
        self.ui.refreshKsdButton.setEnabled(False)
        self.ui.motorForwardButton.setEnabled(False)
        self.ui.motorBackButton.setEnabled(False)
        self.ui.motorResetButton.setEnabled(False)
        self.ui.showWritePatternButton.setEnabled(False)
        self.ui.showCheckerPatternButton.setEnabled(False)
        self.ui.removePatternButton.setEnabled(False)
        self.ui.saveDataButton.setEnabled(False)
        self.ui.pullDataButton.setEnabled(False)
        self.ui.takePictureButton.setEnabled(False)
        self.ui.openCamButton.setEnabled(False)
        self.ui.closeCamButton.setEnabled(False)
        self.ui.cleanButton.setEnabled(False)
        self.ui.posValueLabel.setEnabled(False)
        self.ui.stepsValueLabel.setEnabled(False)
        self.ui.stepsTotalValueLabel.setEnabled(False)
        self.ui.motorPositionEdit.setEnabled(False)
        self.ui.positionLabel.setEnabled(False)
        self.ui.stepsLabel.setEnabled(False)
        self.ui.sumStepsLabel.setEnabled(False)
        self.ui.frame_9.setEnabled(False)
        self.ui.frame_6.setEnabled(False)

    def open_ui(self):
        self.ui.camAfButton.setEnabled(True)
        self.ui.tofAfButton.setEnabled(True)
        self.ui.refreshKsdButton.setEnabled(True)
        self.ui.motorForwardButton.setEnabled(True)
        self.ui.motorBackButton.setEnabled(True)
        self.ui.motorResetButton.setEnabled(True)
        self.ui.showWritePatternButton.setEnabled(True)
        self.ui.showCheckerPatternButton.setEnabled(True)
        self.ui.removePatternButton.setEnabled(True)
        self.ui.saveDataButton.setEnabled(True)
        self.ui.pullDataButton.setEnabled(True)
        self.ui.takePictureButton.setEnabled(True)
        self.ui.openCamButton.setEnabled(True)
        self.ui.closeCamButton.setEnabled(True)
        self.ui.cleanButton.setEnabled(True)
        self.ui.posValueLabel.setEnabled(True)
        self.ui.stepsValueLabel.setEnabled(True)
        self.ui.stepsTotalValueLabel.setEnabled(True)
        self.ui.motorPositionEdit.setEnabled(True)
        self.ui.positionLabel.setEnabled(True)
        self.ui.stepsLabel.setEnabled(True)
        self.ui.sumStepsLabel.setEnabled(True)

    def start_mtf_test_activity(self):
        ProjectorDev.pro_mtf_test_activity()

    def evaluate_kst_correct(self):
        if not self.cameraThread.mRunning:
            self.open_external_camera()
            time.sleep(1)
        img = self.cameraThread.get_img()
        dst = [0] * 12
        #img_size = (img.shape[0], img.shape[1])
        img_size = img.shape
        print('Load EvaluateCorrectionRst:', img_size, dst)
        rst = evaluate_correct_wrapper.evaluate_correction_rst(img_size, img, dst)
        print('返回参数:', dst)

    def get_rail_position(self):
        self.ui.currentPositionLabel.setText(str(Fmc4030.rail_position(self.current_port)))

    def reset_rail(self):
        init(self.current_port)

    def rail_forward(self):

        direction = 1
        if float(self.ui.railForewardEdit.text()) > 0:
            direction = 0
        Fmc4030.rail_forward(self.current_port, direction, abs(float(self.ui.railForewardEdit.text())))

    def rail_reversal(self):
        Fmc4030.rail_forward(self.current_port, 1, abs(float(self.ui.railForewardEdit.text())))

    def rail_absolute_position(self):
        Fmc4030.rail_forward_pos(self.current_port, float(self.ui.railPositionEdit.text()))

    def install_app(self):
        os.system('adb install -r app-debug.apk')

    def uninstall_app(self):
        os.system('adb uninstall com.nbd.tofmodule')

    def open_external_camera(self):
        if self.ui.enableMTF.isChecked():
            self.cameraThread.mEnLaplace = True
        else:
            self.cameraThread.mEnLaplace = False
        self.ui.eOpenCameraButton.setEnabled(False)
        if not self.cameraThread.mRunning:
            self.ui.previewCameraLabel.show()
            self.cameraThread.start()
            # time.sleep(1.5)
            # if not self.cameraThread.mRunning:
            #     QMessageBox.warning(self, "警告", "未识别到摄像头硬件")
        else:
            print("External camera already opened")
        self.ui.eOpenCameraButton.setEnabled(True)

    def close_external_camera(self):
        if self.cameraThread.mRunning:
            self.cameraThread.closeCamera()
            self.ui.previewCameraLabel.clear()
        else:
            print("External camera is not opened")

    def set_exposure_time(self):
        if self.cameraThread is not None:
            self.cameraThread.exposureTime = float(self.ui.exTimeSpinBox.text())
        dic_para = {'ExposureTime': self.cameraThread.exposureTime, 'delay1': float(self.ui.delay1Edit.text()),
                    'delay2': float(self.ui.delay2Edit.text()), 'delay3': float(self.ui.delay3Edit.text())}
        with open('res/para.json', 'w') as file:
            json.dump(dic_para, file)

    def external_take_picture(self, pos=0):
        if self.cameraThread.mRunning:
            create_dir_file()
            path = globalVar.get_value('DIR_NAME_REF')
            # inter_path = DIR_NAME_INTER_REF
            inter_path = globalVar.get_value('DIR_NAME_INTER_REF')
            internal_dirExists = os.path.isdir(inter_path)
            if not internal_dirExists:
                os.makedirs(inter_path)
            # if path is not None:
            #     dirExists = os.path.isdir(path)
            #     if not dirExists:
            #         os.makedirs(path)
            if self.cal:
                name = 'ref_n' + str(pos)
                filePath = path + '/' + name
                self.count += 1
            else:
                times = datetime.datetime.now(tz=None)
                filePath = inter_path + times.strftime("%Y-%m-%d %H:%M:%S").strip().replace(':', '_')
            print('external_take_picture:', filePath)
            self.cameraThread.takePicture(filePath)
        else:
            print("External camera is not opened")

    def rotating_platform_angle(self):
        if len(self.ui.xyEdit.text()) == 0 or len(self.ui.xzEdit.text()) == 0 or len(self.ui.yzEdit.text()) == 0:
            print('输入角度不能为空')
            return
        if self.hy_enable:
            HuiYuanRotate.hy_control(self.hui_yuan, int(self.ui.xyEdit.text()), int(self.ui.yzEdit.text()))
        else:
            # degree: yaw roll pitch
            # self.ui.rotateButton.setEnabled(False)
            self.open_rotate()
            polarity = True
            degree = [int(self.ui.xyEdit.text()) * 100, int(self.ui.xzEdit.text()) * 100,
                      int(self.ui.yzEdit.text()) * 100]
            print('调整转台角度：', degree)
            cmd_list = [['01', '06', '04', '72', '00', '00'], ['01', '06', '04', '70', '00', '00'],
                        ['01', '06', '04', 'ae', '00', '00']]
            # 位置0：cmd_list = [['01', '06', '04', '4c', '00', '00'], ['01', '06', '04', '4e', '00', '00'], ['01', '06', '04', '9c', '00', '00']]
            for i in range(len(degree)):
                if abs(degree[i]) > 9000:
                    print('角度参数异常,退出！！！')
                    return
                if degree[i] == self.lst_degree[i]:
                    continue
                self.lst_degree[i] = degree[i]

                if degree[i] < 0:
                    degree[i] = 65536 - abs(degree[i])
                    polarity = False
                else:
                    polarity = True
                angel = '{:04X}'.format(degree[i])
                cmd_list[i][4] = angel[0:2]
                cmd_list[i][5] = angel[2:4]
                # print(cmd_list[i])
                cmd_char = ' '.join(cmd_list[i])
                # print(cmd_char)
                crc, crc_h, crc_l = self.CRC.CRC16(cmd_char)
                cmd_char = cmd_char + ' ' + crc_l + ' ' + crc_h
                # print(cmd_char)
                cmd_hex = bytes.fromhex(cmd_char)
                if self.current_port is not None:
                    ser_send(self.current_port, cmd_hex)
                else:
                    print('>>>>>>>>>>>>>>>>>>>> 串口异常')

                time.sleep(1.3)
                if not polarity:
                    cmd_list[i][3] = str(hex(int(cmd_list[i][3], 16) + 1))[2:4]
                    cmd_list[i][4] = 'FF'
                    cmd_list[i][5] = 'FF'
                    cmd_char = ' '.join(cmd_list[i])
                    # print(cmd_char)
                    crc, crc_h, crc_l = self.CRC.CRC16(cmd_char)
                    cmd_char = cmd_char + ' ' + crc_l + ' ' + crc_h
                    # print(cmd_char)
                    cmd_hex = bytes.fromhex(cmd_char)
                    if self.current_port is not None:
                        ser_send(self.current_port, cmd_hex)
                    else:
                        print('>>>>>>>>>>>>>>>>>>>> 串口异常')
                else:
                    cmd_list[i][3] = str(hex(int(cmd_list[i][3], 16) + 1))[2:4]
                    cmd_list[i][4] = '00'
                    cmd_list[i][5] = '00'
                    cmd_char = ' '.join(cmd_list[i])
                    # print(cmd_char)
                    crc, crc_h, crc_l = self.CRC.CRC16(cmd_char)
                    cmd_char = cmd_char + ' ' + crc_l + ' ' + crc_h
                    # print(cmd_char)
                    cmd_hex = bytes.fromhex(cmd_char)
                    if self.current_port is not None:
                        ser_send(self.current_port, cmd_hex)
                    else:
                        print('>>>>>>>>>>>>>>>>>>>> 串口异常')
                time.sleep(1)
            cmd_list = ['01', '06', '04', '87', '00', '0A']
            # cmd_list[5] = '{:02X}'.format(int(self.ui.positionEdit.text()))
            # print(cmd_list)
            cmd_char = ' '.join(cmd_list)
            # print(cmd_char)
            crc, crc_h, crc_l = self.CRC.CRC16(cmd_char)
            cmd_char = cmd_char + ' ' + crc_l + ' ' + crc_h
            # print(cmd_char)
            cmd_hex = bytes.fromhex(cmd_char)
            if self.current_port is not None:
                ser_send(self.current_port, cmd_hex)
            else:
                print('>>>>>>>>>>>>>>>>>>>> 串口异常')
            # self.ui.rotateButton.setEnabled(True)

    def manual_position(self):
        # self.showWritePattern()
        # print(self.ui.positionEdit.text())
        cmd_list = ['01', '06', '04', '87', '00', '0A']
        cmd_list[5] = '{:02X}'.format(int(self.ui.positionEdit.text()))
        # print(cmd_list)
        cmd_char = ' '.join(cmd_list)
        # print(cmd_char)
        crc, crc_h, crc_l = self.CRC.CRC16(cmd_char)
        cmd_char = cmd_char + ' ' + crc_l + ' ' + crc_h
        # print(cmd_char)
        cmd_hex = bytes.fromhex(cmd_char)
        if self.current_port is not None:
            ser_send(self.current_port, cmd_hex)
        else:
            print('>>>>>>>>>>>>>>>>>>>> 串口异常')
        if self.ui.enAutoTofKstCheckBox.isChecked():
            time.sleep(float(self.ui.delay1Edit.text()))
            print('>>>>>>>>>>>>>>>>>>>> 开始执行自动梯形校正')
            self.auto_keystone_tof()

    def auto_focus_vision(self):
        os.system("adb shell am broadcast -a asu.intent.action.AutoFocusVision")

    def auto_focus_tof(self):
        create_dir_file()
        os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone --ei mode 0")
        time.sleep(float(self.ui.delay2Edit.text()))
        self.pull_data()
        position, target_pos = auto_focus_tof()
        if position < 0 or position > 2900 or target_pos < 0 or target_pos > 2900:
            print('数据异常 ', position, target_pos)
        print('当前马达位置:' + str(position) + ',目标位置:' + str(target_pos))
        if target_pos > position:
            direction = 2
            target_steps = target_pos - position
        else:
            target_steps = position - target_pos
            direction = 5
        cmd0 = 'adb shell am broadcast -a asu.intent.action.Motor --es operate '
        cmd1 = str(direction)
        cmd2 = ' --ei value '
        cmd3 = str(target_steps)
        cmd = cmd0 + cmd1 + cmd2 + cmd3
        print(cmd)
        os.system(cmd)
        # os.system(
        #     'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')
        # os.system("adb shell am broadcast -a asu.intent.action.AutoFocusTof")

    def auto_keystone_tof(self):
        if len(self.ui.snEdit.text()) >= 19:
            print(self.ui.snEdit.text())
            set_sn(str(self.ui.snEdit.text()).replace('/', ''))
        else:
            print('输入的SN号长度不对: ', len(self.ui.snEdit.text()))
            return
        create_dir_file()
        os.system('adb shell mkdir /sdcard/DCIM/projectionFiles')
        # os.system('adb push AsuKstPara.json /sdcard/DCIM/projectionFiles/AsuProjectorPara.json')
        # os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone --ei mode 0")
        ProjectorDev.pro_save_pos_data(7)
        time.sleep(float(self.ui.delay2Edit.text()))
        self.pull_data()
        # coordinate = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
        if keystone_correct_tof():
            QMessageBox.warning(self, "警告", "TOF全向校正成功")
        else:
            QMessageBox.warning(self, "警告", "TOF全向校正失败，校正数据错误")

    def auto_keystone_cam(self):
        create_dir_file()
        self.kst_reset()
        os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone --ei mode 1")
        time.sleep(float(self.ui.delay2Edit.text()))
        self.pull_data()
        if auto_keystone_cam():
            QMessageBox.warning(self, "警告", "相机全向校正成功")
        else:
            QMessageBox.warning(self, "警告", "相机全向校正失败")

    def cam_inter_cal(self):
        if reference_cam_calib():
            QMessageBox.warning(self, "警告", "相机内参标定成功")
        else:
            QMessageBox.warning(self, "警告", "相机内参标定失败")

    def parce_cal_data(self):
        create_dir_file()
        data = self.auto_cal_thread.parse_projector_json()
        print(data)
        if self.ui.enCalAlgoCheckBox.isChecked():
            auto_keystone_calib2(data)

    def kst_calibrate(self):
        if self.sn_changed():
            print('>>>>>>>>>>>>>>>>>>> 开始解析数据')
            create_dir_file()
            proj_data = self.auto_cal_thread.parse_projector_data()
            print(proj_data)
            auto_keystone_calib2(proj_data)
        else:
            print('请输入20位SN号!!!')

    # timerEvent 关联定时器  self.timer1 = QBasicTimer()
    def timerEvent(self, e):
        if self.pv >= 100:
            self.timer1.stop()
            # self.stop_auto_cal()
            # self.btn_start.setText("Finish")
            self.ui.stopAutoCalButton.setText("结束")
            self.ui.kstAutoCalButton.setText('开始')
            print('停止进度条定时器', self.pv)
            self.ui.autoCalProgressBar.setValue(100)
            self.pv = 0
        else:
            self.ui.autoCalProgressBar.setValue(int(self.pv))

    def sn_changed(self):
        if len(self.ui.snEdit.text()) >= 19:
            set_sn(str(self.ui.snEdit.text()).replace('/', '').upper())
            return True
        else:
            return False

    def write_to_nv(self):
        if not self.sn_changed():
            print('输入的SN号长度不对: ', len(self.ui.snEdit.text()))
            return
        ProjectorDev.pro_kst_cal_service()
        time.sleep(2.9)
        create_dir_file()
        cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
        print(cmd)
        os.system(cmd)
        os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
        # os.system('adb shell cp /sdcard/kst_cal_data.yml /sys/devices/platform/asukey/ksdpara')
        time.sleep(3)
        os.system('adb shell cat /sys/devices/platform/asukey/ksdpara')
        self.restore_ai_feature()
        print('恢复所有开关到默认状态')
        time.sleep(1)
        os.system('adb reboot')

    def auto_focus_motor(self):
        print(self.autofocus_cal_thread.dis_steps)
        # self.autofocus_cal_thread.dis_steps[1] = self.autofocus_cal_thread.dis_steps[1] + int(
        #     float(self.ui.pos11StepsEdit.text()) * 50)
        print(self.autofocus_cal_thread.dis_steps)
        file_path = globalVar.get_value('CALIB_DATA_PATH')
        print(file_path)
        prefix = 'FocusA: [ '
        suffix = ' ]\n'
        da = prefix + ",".join(list(map(str, self.autofocus_cal_thread.dis_steps))) + suffix
        with open(file_path, "a") as f1:
            f1.write(da)
        with open(file_path, "r") as f1:
            print(f1.read())
        # self.win.ui.autoFocusLabel.setText('开始写入数据')
        # cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
        # print(cmd)
        # os.system(cmd)
        # os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")

        # # 提取字符串里的数字
        # sss = 'pro_123uii'
        # print("".join(list(filter(str.isdigit, sss))))
        # os.system("adb shell am startservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
        # os.system('adb shell settings put global AsuAutoKeyStoneEnable 0')
        # os.system('adb shell settings put global tv_auto_focus_asu 0')
        # os.system('adb shell settings put global tv_image_auto_keystone_asu 0')
        # os.system('adb shell settings put global tv_image_auto_keystone_poweron 0')
        # os.system('adb shell settings put global tv_auto_focus_poweron 0')
        # os.system('adb shell settings put system tv_screen_saver 0')
        # time.sleep(2.6)
        # cmd = 'adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value 3000'
        # print(cmd)
        # os.system(cmd)
        # time.sleep(3.6)
        # cmd0 = 'adb shell am broadcast -a asu.intent.action.Motor --es operate 2 --ei value '
        # pos11_steps = self.ui.pos11StepsEdit.text()
        # cmd1 = pos11_steps
        # cmd = cmd0 + cmd1
        # print(cmd)
        # os.system(cmd)

    def save_laplace(self):
        pass
        # self.lap_list.append(self.ex_cam_af_thread.mLaplace)
        # print(self.lap_list, len(self.lap_list))
        # total = 0
        # for i in range(len(self.lap_list)):
        #     total += self.lap_list[i]
        # print(max(self.lap_list), round(total / len(self.lap_list), 2))
        # if len(self.lap_list) > 9:
        #     self.lap_list.clear()

    def clean_laplace(self):
        self.lap_list.clear()
        self.ex_cam_af_thread.clear()
        # self.ex_cam_af_thread.mLaplaceList.clear()
        # self.ex_cam_af_thread.mRailPosition.clear()

    def ex_cam_af(self):
        print('>>>>>>>>>> 外置CAM自动对焦')
        self.open_external_camera()
        self.cameraThread.mEnLaplace = True
        self.ex_cam_af_thread.ser = self.current_port
        self.ex_cam_af_thread.start()

    def auto_focus_cal(self):
        if not self.sn_changed():
            print('输入的SN号长度不对: ', len(self.ui.snEdit.text()))
            return
        self.cameraThread.mEnLaplace = True
        motor_position = os.popen('adb shell getprop persist.motor.position').read()
        # print('马达位置：', motor_position, self.ui.positionLabel.text())
        create_dir_file()
        # palette = QPalette()
        # palette.setColor(QPalette.Background, QColor(255, 0, 0))
        # self.ui.autoFocusLabel.setAutoFillBackground(True)
        # self.ui.autoFocusLabel.setPalette(palette)
        self.ui.autoFocusLabel.setStyleSheet("color:blue")
        self.ui.autoFocusLabel.setText('>>>>>>>>>> 开始标定')
        self.close_ai_feature()
        self.open_external_camera()
        self.cameraThread.mEnLaplace = True
        self.autofocus_cal_thread.ser = self.hui_yuan
        self.autofocus_cal_thread.start()

    def kst_auto_calibrate(self):

        if not self.sn_changed():
            print('输入的SN号长度不对: ', len(self.ui.snEdit.text()))
            return
        if self.timer1.isActive():
            print('>>>>>>>>>> 进度条定时器已开启')
            return
        else:
            self.pv = 0
            self.timer1.start(1000, self)  # ms
            self.ui.autoCalProgressBar.setValue(0)
            self.ui.stopAutoCalButton.setText("停止")
            self.ui.kstAutoCalButton.setText("测试中")
        self.statusBar_3.setText('SN:' + self.ui.snEdit.text())
        # self.ui.snEdit.setText('')
        # self.ui.snEdit.clear()

        create_dir_file()
        # 拉取对焦标定文件
        # calib_data_path = globalVar.get_value('CALIB_DATA_PATH')
        # cmd0 = 'adb pull /sdcard/kst_cal_data_bk.yml '
        # cmd1 = calib_data_path
        # cmd = cmd0 + cmd1
        # print(cmd)
        # os.system(cmd)
        os.system('adb shell mkdir /sdcard/DCIM/projectionFiles')
        os.system('adb push AsuKstPara.json /sdcard/DCIM/projectionFiles/AsuProPara.json')
        self.close_ai_feature()

        self.ui.kstCalButton.setEnabled(False)
        cmd = self.ui.kstAutoCalCountEdit.text().strip()
        print(cmd)
        if cmd != '':
            self.auto_cal_thread.positionList = list(map(int, cmd.split(',')))
        self.open_external_camera()
        self.auto_cal_thread.delay1 = float(self.ui.delay1Edit.text())
        self.auto_cal_thread.delay2 = float(self.ui.delay2Edit.text())
        self.auto_cal_thread.delay3 = float(self.ui.delay3Edit.text())
        self.auto_cal_thread.enableAlgo = self.ui.enableAlgoCheckBox.isChecked()
        if self.hy_enable:
            self.auto_cal_thread.ser = self.hui_yuan
        else:
            self.auto_cal_thread.ser = self.current_port
        self.auto_cal_thread.start()

    def stop_auto_cal(self):
        # rail_stop(self.current_port)
        # os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
        self.ex_cam_af_thread.mExit = True
        if self.auto_cal_thread is not None:
            self.auto_cal_thread.exit = True
        if self.timer1.isActive():
            self.timer1.stop()
        self.ui.kstAutoCalButton.setText('开始')
        self.ui.stopAutoCalButton.setText("结束")
        self.ui.autoCalProgressBar.setValue(0)
        self.pv = 0
        # cmd0 = 'adb shell am broadcast -a asu.intent.action.SetKstPoint --es point '
        # cmd1 = '"0.0,0.0,1920.0,0.0,1920.0,1080.0,0.0,1080.0"'
        # cmd = cmd0 + cmd1
        # print(cmd)
        # os.system(cmd)
        # os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")

    def kst_reset(self):
        print('----------------------')
        # cmd = "adb shell setprop persist.vendor.hwc.keystone 0,0,1920,0,1920.1080,0,1080"
        # os.system(cmd)
        # os.system("adb shell service call SurfaceFlinger 1006")
        # set_point('0,0,1920,0,1920,1080,0,1080')
        self.ui.ksdLeftDownEdit_x.setText('0')
        self.ui.ksdLeftDownEdit_y.setText('0')
        self.ui.ksdLeftUpEdit_x.setText('0')
        self.ui.ksdLeftUpEdit_y.setText('1079')
        self.ui.ksdRightUpEdit_x.setText('1919')
        self.ui.ksdRightUpEdit_y.setText('1079')
        self.ui.ksdRightDownEdit_x.setText('1919')
        self.ui.ksdRightDownEdit_y.setText('0')
        self.refresh_keystone()

    def refresh_keystone(self):
        ksdPoint = [0] * 8
        ksdPoint[0] = int(self.ui.ksdLeftDownEdit_x.text())
        ksdPoint[1] = int(self.ui.ksdLeftDownEdit_y.text())
        ksdPoint[6] = int(self.ui.ksdLeftUpEdit_x.text())
        ksdPoint[7] = int(self.ui.ksdLeftUpEdit_y.text())
        ksdPoint[4] = int(self.ui.ksdRightUpEdit_x.text())
        ksdPoint[5] = int(self.ui.ksdRightUpEdit_y.text())
        ksdPoint[2] = int(self.ui.ksdRightDownEdit_x.text())
        ksdPoint[3] = int(self.ui.ksdRightDownEdit_y.text())
        ProjectorDev.pro_set_kst_point(ksdPoint)

    def update_data(self):
        position = os.popen("adb shell getprop persist.motor.position").read()
        if not position:
            print("------------------update data------------------")
            self.update_data_timer.stop()
            self.close_ui()
        steps = os.popen("adb shell getprop persist.motor.steps").read()
        totalStepsBack = os.popen("adb shell getprop persist.motor.totalStepsBack").read()
        self.ui.posValueLabel.setText(position)
        self.ui.stepsValueLabel.setText(steps)
        self.ui.stepsTotalValueLabel.setText(totalStepsBack)

        self.label_used_time_text += 1
        hour = int(self.label_used_time_text // 3600)
        minute = int((self.label_used_time_text % 3600) // 60)
        second = int(self.label_used_time_text % 60)
        fmt = '累计运行时间：{:0>2d}:{:0>2d}:{:0>2d}'.format(hour, minute, second)
        self.statusBar_4.setText(fmt)

    def start_test_activity(self):
        os.system('adb shell am start -n com.nbd.autofocus/com.nbd.autofocus.MainActivity')

    def start_service(self):
        ProjectorDev.pro_kst_cal_service()

    def root_device(self):
        ProjectorDev.connect_dev(str(self.ui.ip_addr.text()))
        ProjectorDev.pro_kst_cal_service()
        # devices = os.popen("adb devices").read()
        # if len(devices) > 30:
        #     os.system(
        #         'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')
        #     # os.system("adb root")
        #     # os.system("adb remount")
        #     # os.system("adb shell chmod 777 /dev/stmvl53l1_ranging")
        #     self.open_ui()
        #     # self.update_data_timer.start(1000)
        # else:
        #     self.close_ui()
        # get_sn()
        # print("devices ", devices[::-1])
        # print("len ", len(devices))
        # self.ui.rootButton.setEnabled(True)

    def clean_data(self):
        localSN = get_sn()
        srcDirName = DIR_NAME + '/' + localSN
        srcExit = os.path.isdir(srcDirName)
        if srcExit:
            times = datetime.datetime.now(tz=None)
            distDirName = DIR_NAME_COPY + '/' + localSN + '_' + times.strftime("%Y-%m-%d %H:%M:%S").strip().replace(':',
                                                                                                                    '_')
            # shutil.copytree(DIR_NAME, 'copy')
            ret = shutil.move(srcDirName, distDirName)
            print('备份结束', ret)
        # os.system("rm -rf .\asuFiles")
        os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/* ")
        os.system("adb shell rm -rf /sdcard/kst_cal_data.yml ")
        os.system("adb shell rm -rf /sdcard/kst_cal_data_bk.yml ")
        os.system("adb shell am broadcast -a asu.intent.action.Clear")
        self.mCount = 0
        # os.system('adb uninstall com.nbd.tofmodule')
        #
        # dirExists = os.path.isdir('asuFiles')
        # if dirExists:
        #     shutil.rmtree('asuFiles')
        # else:
        #     print("No find asuFiles")
        #
        # fileExists = os.path.isfile('motor.log')
        # if fileExists:
        #     # mylog.shutdown()
        #     os.remove('motor.log')
        # else:
        #     print("No find files")
        self.count = 0

    def open_camera(self):
        cmd = "adb shell am broadcast -a asu.intent.action.TakePicture --ei value 0 "
        os.system(cmd)
        self.statusBar_2.setText("投影内部相机状态：打开")

    def take_picture(self):
        cmd = "adb shell am broadcast -a asu.intent.action.TakePicture --ei value 1 "
        os.system(cmd)

    def close_camera(self):
        cmd = "adb shell am broadcast -a asu.intent.action.TakePicture --ei value 2 "
        os.system(cmd)
        self.statusBar_2.setText("投影内部相机状态：关闭")

    def save_data(self):
        # if os.path.exists(DIR_NAME_PRO):
        #     files = os.listdir(DIR_NAME_PRO)  # 读入文件夹
        #     preLenFiles = len(files)
        # self.statusBar_3.clear()
        # self.statusBar_3.setText('保存当前姿态数据中...')
        save_finish = False
        self.ui.saveDataButton.setEnabled(False)

        startTime = time.time()
        # point = get_point()
        self.kst_reset()
        cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
        cmd1 = str(self.mCount)
        os.system(cmd0 + cmd1)
        self.mCount += 1

        time.sleep(2)
        self.cal = True
        self.external_take_picture()
        self.cal = False
        time.sleep(3)
        self.pull_data()
        # files = os.listdir(DIR_NAME_PRO)  # 读入文件夹
        # nowLenFiles = len(files)
        # preTime = time.time()
        # while (nowLenFiles - preLenFiles) == 0:
        #     files = os.listdir(DIR_NAME_PRO)  # 读入文件夹
        #     nowLenFiles = len(files)
        #     nowTime = time.time()
        #     if (nowTime - preTime) > 6:
        #         print('>>>>>>>>>>>>>>>>>>>> 采集数据超时，请重新抓取 ', DIR_NAME_PRO)
        #         QMessageBox.warning(self, "警告", "标定数据保存失败")
        #         return False
        #
        pro_file_list = []
        ret = {"jpg": 0, "png": 0, "bmp": 0}
        for root, dirs, files in os.walk(globalVar.get_value('DIR_NAME_PRO')):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:3]
                print(file, ext, head)
                if ext == '.bmp' and head == 'pro':
                    ret["bmp"] = ret["bmp"] + 1
                    pro_file_list.append(file)
                if ext == ".png" and head == 'pro':
                    ret["png"] = ret["png"] + 1
        if len(pro_file_list) > 0:
            pro_img = cv2.imread(globalVar.get_value('DIR_NAME_PRO') + pro_file_list[-1])
            pro_img_size = (pro_img.shape[0], pro_img.shape[1])
            imageSize = os.path.getsize(globalVar.get_value('DIR_NAME_PRO') + pro_file_list[-1])
            print('最新图片：', len(pro_file_list), pro_file_list[-1], pro_img_size[0], pro_img_size[1], imageSize)
            if pro_img.shape[0] == 720 and pro_img.shape[1] == 1280 and imageSize == 2764854:
                # 图片的大小
                endTime = time.time()
                print('保存数据耗时：', (endTime - startTime))
                QMessageBox.warning(self, "警告", "数据保存成功")
                os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/*.bmp ")
                # self.statusBar_3.setText('当前姿态下数据保存完成')
            else:
                # self.statusBar_3.setText('当前姿态下数据保存失败')
                QMessageBox.warning(self, "警告", "数据保存失败")
        else:
            print('没有发现投影设备返回的图片数据 ', pro_file_list)
            QMessageBox.warning(self, "警告", "没有发现投影设备返回的图片数据")
            # self.statusBar_3.setText('当前姿态下数据保存失败')
        # set_point(point)
        self.ui.saveDataButton.setEnabled(True)

    def pull_data(self):
        localSN = get_sn()
        distDirName = DIR_NAME + '/' + localSN
        cmd = 'adb pull /sdcard/DCIM/projectionFiles ' + distDirName
        print('Pull files from PC : ', cmd)
        os.system(cmd)

    def removePattern(self):
        # os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
        ProjectorDev.pro_show_pattern(0)

    def showCheckerPattern(self):
        os.system('adb push show_pattern.png sdcard/DCIM/show_pattern.png')
        # os.system('adb shell am broadcast -a asu.intent.action.ShowPattern2')
        ProjectorDev.pro_show_pattern(2)

    def showWritePattern(self):
        # os.system('adb shell am broadcast -a asu.intent.action.ShowBlankPattern')
        os.system('adb push show_pattern_af.png sdcard/DCIM/show_pattern_af.png')
        ProjectorDev.pro_show_pattern(1)

    def get_motor_position(self):
        self.ui.posValueLabel.setText(str(ProjectorDev.pro_get_motor_position()))

    def execute_motor_position(self):
        ProjectorDev.pro_motor_reset_steps(int(self.ui.motorPosition2Edit.text()))

    def motorReset(self):
        ProjectorDev.motor_reset()
        # ProjectorDev.pro_motor_reset_steps(0)
        # os.system('adb shell "echo 5 3000 > /sys/devices/platform/customer-AFmotor/step_set"')
        # os.system("adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value 3000")

    def motorForward(self):
        steps = int(self.ui.motorPositionEdit.text())
        ProjectorDev.pro_motor_forward2(5, steps)

    def motorBack(self):
        steps = int(self.ui.motorPositionEdit.text())
        ProjectorDev.pro_motor_forward2(2, steps)

    def init_status_bar(self):
        # 状态栏显示软件版本
        self.ui.statusBar = QStatusBar(self)

        # font = QtGui.QFont()
        # font.setPointSize(14)

        info = QLabel(self)
        # info.setFont(font)
        info.setText(
            '<html><head/><body><p><span style="font-size=24; color:#00aaff;">V1.0.1</span></p></body></html>')
        info.setAlignment(Qt.AlignLeft)
        self.ui.statusBar.addPermanentWidget(info, 1)

        info = QLabel(self)
        # info.setFont(font)
        info.setText('<html><head/><body><p><span style=" color:#00aaff;">V12121</span></p></body></html>')
        self.ui.statusBar.addWidget(info, 1)

        self.ui.setStatusBar(self.statusBar)
        self.ui.statusBar.setStatusTip('StatusTip')
        self.ui.statusBar.setToolTip('ToolTip')

    def initialize_ui(self):
        self.ui.send_data.setEnabled(False)
        self.ui.motorPositionEdit.setText("100")
        self.ui.posValueLabel.setText("0")
        self.ui.close_port.setEnabled(False)
        available_ports = get_ports()
        self.ui.serial_selection.addItems(available_ports)
        self.ui.baud_rate.setEditable(True)
        self.ui.baud_rate.setCurrentText("9600")

    def open_rotate(self):
        if self.hy_enable:
            # self.hui_yuan = HuiYuanRotate.open_hy_dev()
            pass
        else:
            self.open_dev(9600, 'E')

    def close_rotate(self):
        self.close_port()
        # if self.hy_enable:
        #     self.hui_yuan = HuiYuanRotate.close_hy_dev()
        print('关闭转台')

    def open_rail(self):
        self.open_dev(115200, 'N')

    def close_rail(self):
        self.close_port()
        print('关闭导轨')

    def open_dev(self, baud_rate, check_bit):
        current_port_name = self.ui.serial_selection.currentText()
        print(current_port_name)
        try:
            if self.current_port is None:
                self.current_port = open_port(current_port_name,
                                              baudrate=baud_rate,
                                              bytesize=8,
                                              parity=check_bit,
                                              stopbits=1.0,
                                              timeout=1)
            else:
                print('串口已经打开')
        except:
            self.ui.port_status.setText(current_port_name + ' 打开失败')
            print('打开串口失败')
            return

    def open_port(self):
        current_port_name = self.ui.serial_selection.currentText()
        baud_rate = int(self.ui.baud_rate.currentText())
        bytesize = 8
        # rail: check_bit = "N", 115200
        # rotate: check_bit = "E", 9600
        check_bit = "E"
        # check_bit = "N"
        stop_bit = 1.0
        try:
            self.current_port = open_port(current_port_name,
                                          baudrate=baud_rate,
                                          bytesize=bytesize,
                                          parity=check_bit,
                                          stopbits=stop_bit,
                                          timeout=1)
        except:
            self.ui.port_status.setText(current_port_name + ' 打开失败')
            return
        if self.current_port and self.current_port.isOpen():
            self.ui.port_status.setText(current_port_name + ' 打开成功')
            self.ui.open_port.setEnabled(False)
            self.ui.close_port.setEnabled(True)
            self.ui.send_data.setEnabled(True)
            self.ui.refresh_port.setEnabled(False)
            self.ui.frame_9.setEnabled(True)
            self.ui.frame_6.setEnabled(True)
            # self.serial_thread.ser = self.current_port
            # self.auto_cal_thread = AutoCalThread(self.current_port, self)
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
            # self.ui.frame_6.setEnabled(False)
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
        return
        # receive_ascii_format = self.ui.receive_ascii_format.isChecked()
        self.ui.receive_data_area.clear()
        receive_ascii_format = False
        raw_data_list = self.serial_thread.current_data
        cmd_data = ()
        cmd_data = asu_pdu_parse_one_frame(raw_data_list)
        print("parse data : ", cmd_data[0], cmd_data[1])
        if cmd_data[0] == 22:
            sw_version = str(cmd_data[1][0]) + "." \
                         + str(cmd_data[1][1]) + "." \
                         + str(cmd_data[1][2]) + "." \
                         + str(cmd_data[1][3])
            self.ui.label_sw_version.setText(sw_version)

        try:
            if receive_ascii_format:
                current_data = self.serial_thread.current_data.decode('utf-8')
            else:
                current_data = self.serial_thread.current_data.hex()
                # print("receive data hex : ", self.serial_thread.current_data)
                print("receive data hex ", current_data[2])

                # asu_parse_one_frame(current_data)
                data_list = re.findall('.{2}', current_data)
                print("receive data data_list len : ", str2hex(data_list[2]))
                # result = map(hex(), data_list)
                # print("receive data len ", result[2])
                # print("receive data data_list ", int(data_list[2]) + int(data_list[3]) + int(data_list[4]))
                print("receive data data_list : ", int(data_list[3]))
                # print(len(data_list), data_list[0], data_list[1], data_list[2])
                current_data = ' '.join(data_list) + ' '
                print("receive data X : ", current_data)
            # if self.ui.auto_new_line.checkState() == Qt.Checked and self.ui.show_time.checkState() == Qt.Checked:
            #     current_data = datetime.datetime.now().strftime('%H:%M:%S') + ' ' + current_data
            # if self.ui.auto_new_line.checkState() == Qt.Checked:
            #     current_data += '\n'
            self.ui.receive_data_area.insertPlainText(current_data)
            # if self.ui.scroll_show.isChecked():
            #     self.ui.receive_data_area.verticalScrollBar().setValue(
            #         self.ui.receive_data_area.verticalScrollBar().maximum())
            # self.ui.receive_data_status.setText('数据接收状态: 成功')
            self.ui.port_status.setText('数据接收状态: 成功')
        except:
            self.ui.port_status.setText('数据接收状态: 失败')

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

    def close_ai_feature(self):
        os.system('adb shell settings put global AsuAutoKeyStoneEnable 0')
        os.system('adb shell settings put global tv_auto_focus_asu 0')
        os.system('adb shell settings put global tv_image_auto_keystone_asu 0')
        os.system('adb shell settings put global tv_image_auto_keystone_poweron 0')
        os.system('adb shell settings put global tv_auto_focus_poweron 0')
        os.system('adb shell settings put system tv_screen_saver 0')

    def restore_ai_feature(self):
        # 算法切换到ASU
        os.system('adb shell setprop persist.sys.keystone.type 0')
        # 自动垂直校正
        os.system('adb shell settings put global AsuAutoKeyStoneEnable 0')
        # 位移自动对焦
        os.system('adb shell settings put global tv_auto_focus_asu 1')
        # 位移全向自动校正
        os.system('adb shell settings put global tv_image_auto_keystone_asu 1')
        # 开机相关
        os.system('adb shell settings put global tv_image_auto_keystone_poweron 0')
        os.system('adb shell settings put global tv_auto_focus_poweron 1')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ProjectorWindow()
    globalVar._init()

    # width height
    # w.resize(600, 820)
    w.show()
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=DarkPalette()))
    # mylog = Logger('motor.log', level='debug')
    # mylog.logger.debug("-------------重新启动应用-------------")
    sys.exit(app.exec_())
