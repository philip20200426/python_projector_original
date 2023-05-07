import csv
import datetime
import re
from pathlib import Path

import cv2
import qdarkstyle
from PyQt5.QtCore import Qt
from qdarkstyle import DarkPalette

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
from serial_utils import get_ports, open_port, str2hex, asu_pdu_parse_one_frame
import shutil
from ctypes import *

import os
import shutil
from glob import glob

class SerialThread(QThread):
    data_arrive_signal = pyqtSignal(name='serial_data')

    def __init__(self, ser=None):
        super().__init__()
        self.ser = ser
        self.current_data = b''

    def run(self):
        time.sleep(1)  # 防止直接进循环, 阻塞主ui
        while True:
            if self.ser is not None and self.ser.inWaiting():
                self.current_data = self.ser.read(self.ser.inWaiting())
                self.data_arrive_signal.emit()


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    label_used_time_text = 0

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('调试工具')
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

        self.ui.kstResetButton.clicked.connect(self.kst_reset)
        self.ui.camInterCalButton.clicked.connect(self.cam_inter_cal)
        self.ui.camAfButton.clicked.connect(self.auto_focus_vision)
        self.ui.tofAfButton.clicked.connect(self.auto_focus_tof)
        self.ui.autoTofKsdButton.clicked.connect(self.auto_keystone_tof)
        self.ui.autoCamKstButton.clicked.connect(self.auto_keystone_cam)
        self.ui.kstCalButton.clicked.connect(self.kst_calibrate)
        self.ui.refreshKsdButton.clicked.connect(self.refresh_keystone)
        self.ui.motorForwardButton.clicked.connect(self.motorForward)
        self.ui.motorBackButton.clicked.connect(self.motorBack)
        self.ui.motorResetButton.clicked.connect(self.motorReset)
        self.ui.showWritePatternButton.clicked.connect(self.showWritePattern)
        self.ui.showCheckerPatternButton.clicked.connect(self.showCheckerPattern)
        self.ui.removePatternButton.clicked.connect(self.removePattern)
        self.ui.saveDataButton.clicked.connect(self.save_data)
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
        self.ui.getSwVerButton.clicked.connect(self.get_sw_version)
        self.ui.eOpenCameraButton.clicked.connect(self.open_external_camera)
        self.ui.eCloseCameraButton.clicked.connect(self.close_external_camera)
        self.ui.eTakePictureButton.clicked.connect(self.external_take_picture)
        self.ui.exTimesHorizontalSlider.valueChanged['int'].connect(self.set_exposure_time)
        self.close_ui()
        # self.init_status_bar()

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        self.serial_thread.start()
        self.serial_thread.data_arrive_signal.connect(self.receive_data)

        self.update_data_timer = QTimer()
        self.update_data_timer.timeout.connect(self.update_data)
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

    def image_callback(self, image):  # 这里的image就是任务线程传回的图像数据,类型必须是已经定义好的数据类型
        self.ui.previewCameraLabel.setPixmap(image)
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

    def open_external_camera(self):
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
            self.ui.previewCameraLabel.hide()
        else:
            print("External camera is not opened")

    def set_exposure_time(self):
        if self.cameraThread is not None:
            self.cameraThread.exposureTime = float(self.ui.exTimeSpinBox.text())

    def external_take_picture(self):
        if self.cameraThread.mRunning:
            path = DIR_NAME_REF
            inter_path = DIR_NAME_INTER_REF
            dirExists = os.path.isdir(path)
            if not dirExists:
                os.makedirs(path)
            internal_dirExists = os.path.isdir(inter_path)
            if not internal_dirExists:
                os.makedirs(inter_path)
            if self.cal:
                name = 'ref_n0' + str(self.count)
                filePath = path + '/' + name
                self.count += 1
            else:
                times = datetime.datetime.now(tz=None)
                filePath = inter_path + '/' + times.strftime("%Y-%m-%d %H:%M:%S").strip().replace(':', '_')
            self.cameraThread.takePicture(filePath)
        else:
            print("External camera is not opened")

    def auto_focus_vision(self):
        os.system("adb shell am broadcast -a asu.intent.action.AutoFocusVision")

    def auto_focus_tof(self):
        os.system("adb shell am broadcast -a asu.intent.action.AutoFocusTof")

    def auto_keystone_tof(self):
        os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone")
        time.sleep(3)
        self.pull_data()
        # coordinate = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
        if keystone_correct_tof():
            QMessageBox.warning(self, "警告", "TOF全向校正成功")
        else:
            QMessageBox.warning(self, "警告", "TOF全向校正失败，校正数据错误")

    def auto_keystone_cam(self):
        self.kst_reset()
        os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone")
        time.sleep(3)
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

    def kst_calibrate(self):
        # os.system("adb shell am broadcast -a asu.intent.action.SaveData")
        # 拿到所有数据 n组，每组两个照片，imu，tof
        self.kst_reset()
        if auto_keystone_calib():
            QMessageBox.warning(self, "警告", "全向自动标定成功")
        else:
            QMessageBox.warning(self, "警告", "全向自动标定失败")

    def kst_reset(self):
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
        ksdPoint[0] = self.ui.ksdLeftDownEdit_x.text()
        ksdPoint[1] = self.ui.ksdLeftDownEdit_y.text()
        ksdPoint[6] = self.ui.ksdLeftUpEdit_x.text()
        ksdPoint[7] = self.ui.ksdLeftUpEdit_y.text()
        ksdPoint[4] = self.ui.ksdRightUpEdit_x.text()
        ksdPoint[5] = self.ui.ksdRightUpEdit_y.text()
        ksdPoint[2] = self.ui.ksdRightDownEdit_x.text()
        ksdPoint[3] = self.ui.ksdRightDownEdit_y.text()
        set_point(ksdPoint)

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

    def root_device(self):
        devices = os.popen("adb devices").read()
        if len(devices) > 30:
            os.system("adb root")
            os.system("adb remount")
            self.open_ui()
            self.update_data_timer.start(1000)
        else:
            self.close_ui()
        get_sn()

        print("devices ", devices[::-1])
        print("len ", len(devices))
        self.ui.rootButton.setEnabled(True)

    def clean_data(self):
        localSN = get_sn()
        srcDirName = DIR_NAME + '/' + localSN
        srcExit = os.path.isdir(srcDirName)
        if srcExit:
            times = datetime.datetime.now(tz=None)
            distDirName = DIR_NAME_COPY + '/' + localSN + '_' + times.strftime("%Y-%m-%d %H:%M:%S").strip().replace(':', '_')
            # shutil.copytree(DIR_NAME, 'copy')
            ret = shutil.move(srcDirName, distDirName)
            print('备份结束', ret)
        print('创建新目录: ', srcDirName)
        create_dir_file()
        # os.system("rm -rf .\asuFiles")
        os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/* ")
        os.system("adb shell am broadcast -a asu.intent.action.Clear")
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
        os.system("adb shell am broadcast -a asu.intent.action.SaveData")
        time.sleep(2)
        self.cal = True
        self.external_take_picture()
        self.cal = False
        time.sleep(2)
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
        for root, dirs, files in os.walk(DIR_NAME_PRO):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:2]
                if ext == '.bmp' and head == 'n0':
                    ret["jpg"] = ret["jpg"] + 1
                if ext == ".png" and head == 'n0':
                    pro_file_list.append(file)
                    ret["png"] = ret["png"] + 1
        # print('最新图片: ', len(pro_file_list), pro_file_list[-1])
        if len(pro_file_list) > 0:
            pro_img = cv2.imread(DIR_NAME_PRO + pro_file_list[-1])
            pro_img_size = (pro_img.shape[0], pro_img.shape[1])
            imageSize = os.path.getsize(DIR_NAME_PRO + pro_file_list[-1])
            print(pro_img_size[0], pro_img_size[1], imageSize)
            if pro_img.shape[0] == 720 and pro_img.shape[1] == 1280 and imageSize > 132500:
                # 图片的大小
                QMessageBox.warning(self, "警告", "数据保存成功")
            else:
                QMessageBox.warning(self, "警告", "数据保存失败")
        else:
            QMessageBox.warning(self, "警告", "没有发现图片数据")

    def pull_data(self):
        localSN = get_sn()
        srcDirName = DIR_NAME + '/' + localSN
        cmd = 'adb pull /sdcard/DCIM/projectionFiles ' + srcDirName
        print(cmd)
        os.system(cmd)

    def removePattern(self):
        os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")

    def showCheckerPattern(self):
        os.system('adb push show_pattern.png sdcard/DCIM/show_pattern.png')
        os.system('adb shell am broadcast -a asu.intent.action.ShowPattern2')

    def showWritePattern(self):
        os.system('adb shell am broadcast -a asu.intent.action.ShowBlankPattern')

    def motorReset(self):
        # os.system('adb shell "echo 5 3000 > /sys/devices/platform/customer-AFmotor/step_set"')
        os.system("adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value 3000")

    def motorForward(self):
        # inputCmd = 'adb shell "echo 5 $hello > /sys/devices/platform/customer-AFmotor/step_set"'
        # execute_adb_command(inputCmd, 0)
        # subprocess.Popen('adb shell "echo 5 2000 > /sys/devices/platform/customer-AFmotor/step_set"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cmd1 = "adb shell "
        # cmd2 = '"echo 5 '
        # cmd3 = self.ui.motorPositionEdit.text()
        # cmd4 = '> /sys/devices/platform/customer-AFmotor/step_set"'
        # cmd = cmd1 + cmd2 + cmd3 + cmd4
        # print(cmd)
        # os.system(cmd)
        cmd1 = "adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value "
        cmd2 = self.ui.motorPositionEdit.text()
        # mylog.logger.debug("-" + cmd2)
        cmd = cmd1 + cmd2
        print(cmd)
        os.system(cmd)

    def motorBack(self):
        # inputCmd = 'adb shell "echo 5 $hello > /sys/devices/platform/customer-AFmotor/step_set"'
        # execute_adb_command(inputCmd, 0)
        # subprocess.Popen('adb shell "echo 5 2000 > /sys/devices/platform/customer-AFmotor/step_set"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cmd1 = "adb shell "
        # cmd2 = '"echo 2 '
        # cmd3 = self.ui.motorPositionEdit.text()
        # cmd4 = '> /sys/devices/platform/customer-AFmotor/step_set"'
        # cmd = cmd1 + cmd2 + cmd3 + cmd4
        # print(cmd)
        # os.system(cmd)
        cmd1 = "adb shell am broadcast -a asu.intent.action.Motor --es operate 2 --ei value "
        cmd2 = self.ui.motorPositionEdit.text()
        # mylog.logger.debug("+" + cmd2)
        cmd = cmd1 + cmd2
        print(cmd)
        os.system(cmd)

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
        self.ui.baud_rate.setCurrentText("921600")

    def open_port(self):
        self.ui.statusBar.showMessage("4556")
        print("88888888");
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

    def get_sw_version(self):
        data = "FEFE16000000"
        Hex_str = bytes.fromhex(data)
        print("Hex_str : ", Hex_str)
        # count = count + 1
        # print("count : %d", count)
        # if count > 2:
        #     count = 0
        self.current_port.write(Hex_str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ProjectorWindow()
    # width height
    # w.resize(600, 820)
    w.show()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=DarkPalette()))
    # mylog = Logger('motor.log', level='debug')
    # mylog.logger.debug("-------------重新启动应用-------------")
    sys.exit(app.exec_())
