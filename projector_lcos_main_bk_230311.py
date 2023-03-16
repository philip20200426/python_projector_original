import re
import string
import threading
from log_utils import Logger

# import serial
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTextEdit, QMessageBox
import os, sys

from utils import check_hex
from projector_pdu import Ui_MainWindow
import subprocess
import datetime  # 导入datetime模块
import threading  # 导入threading模块
import time
from serial_utils import get_ports, open_port, parse_one_frame, str2hex, asu_pdu_parse_one_frame
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
            if self.ser is not None and self.ser.inWaiting():
                self.current_data = self.ser.read(self.ser.inWaiting())
                self.data_arrive_signal.emit()


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('调试工具')
        self.initialize_ui()
        # self.redSpinBox.valueChanged['int'].connect(self.set_red_current(int))
        # self.ui.redHorizontalSlider.valueChanged(self.set_red_current)
        self.ui.redHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.greenHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.blueHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.autoKsdButton.clicked.connect(self.auto_keystone)
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
        self.ui.cleanButton.clicked.connect(self.clean_data)
        self.ui.rootButton.clicked.connect(self.root_device)
        self.ui.open_port.clicked.connect(self.open_port)
        self.ui.close_port.clicked.connect(self.close_port)
        self.ui.refresh_port.clicked.connect(self.refresh_port)
        self.ui.send_data.clicked.connect(self.send_data)
        self.ui.getSwVerButton.clicked.connect(self.get_sw_version)

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        self.serial_thread.start()
        self.serial_thread.data_arrive_signal.connect(self.receive_data)

        self.ui.getSwVerButton.setEnabled(False)
        self.ui.redSpinBox.setEnabled(False)
        self.ui.redHorizontalSlider.setEnabled(False)
        self.ui.greenSpinBox.setEnabled(False)
        self.ui.greenHorizontalSlider.setEnabled(False)
        self.ui.blueSpinBox.setEnabled(False)
        self.ui.blueHorizontalSlider.setEnabled(False)

    def set_current(self):
        time.sleep(0.05)
        data = ""
        head = "FEFE"
        cmd = "1E"
        length = "03"
        current_r = self.ui.redHorizontalSlider.value()
        current_g = self.ui.greenHorizontalSlider.value()
        current_b = self.ui.blueHorizontalSlider.value()
        sum = current_r + current_g + current_b
        crc = str(hex(sum))[2:].upper()
        if len(crc) == 1:
            crc = "0" + crc + "00"
        if len(crc) == 2:
            crc = crc + "00"
        if len(crc) == 3:
            crc = "0" + crc
        # 校验码发送时，低字节在前，高字节在后
        if sum > 255:
            crc = crc[2:] + crc[0:2]
        print(crc[2:], crc[0:2])
        print("crc 0x%x : %d", crc, crc)
        # cmd = "14"
        # crc = "F000"
        size = 3
        data_r = str(hex(current_r))[2:].upper()
        data_g = str(hex(current_g))[2:].upper()
        data_b = str(hex(current_b))[2:].upper()
        if len(data_r) % 2 != 0:
            data_r = "0" + data_r
        if len(data_g) % 2 != 0:
            data_g = "0" + data_g
        if len(data_b) % 2 != 0:
            data_b = "0" + data_b
        data = head + cmd + length + crc + data_r + data_g + data_b
        print("data : ", data)
        Hex_str = bytes.fromhex(data)
        print("Hex_str : ", Hex_str)
        self.current_port.write(Hex_str)
        print(current_r, current_g, current_b)

    def auto_keystone(self):
        os.system("adb shell am broadcast -a asu.intent.action.AutoKeystone")

    def refresh_keystone(self):
        point_left_down_x = self.ui.ksdLeftDownEdit_x.text()
        point_left_down_y = self.ui.ksdLeftDownEdit_y.text()
        point_left_up_x = self.ui.ksdLeftUpEdit_x.text()
        point_left_up_y = self.ui.ksdLeftUpEdit_y.text()
        point_right_up_x = self.ui.ksdRightUpEdit_x.text()
        point_right_up_y = self.ui.ksdRightUpEdit_y.text()
        point_right_down_x = self.ui.ksdRightDownEdit_x.text()
        point_right_down_y = self.ui.ksdRightDownEdit_y.text()
        # if int(point_left_down_x) > 1920:
        #     point_left_down_x = 1920
        # if int(point_left_up_x) > 1920:
        #     point_left_up_x = 1920
        # if int(point_right_up_x) > 1920:
        #     point_right_up_x = 1920
        # if int(point_right_down_x) > 1920:
        #     point_right_down_x = 1920
        #
        # if int(point_left_down_y) > 1080:
        #     point_left_down_y = 1080
        # if int(point_left_up_y) > 1080:
        #     point_left_up_y = 1080
        # if int(point_right_up_y) > 1080:
        #     point_right_up_y = 1080
        # if int(point_right_down_y) > 1080:
        #     point_right_down_y = 1080

        ksdPoint = point_left_down_x + "," + point_left_down_y + "," + point_right_down_x + "," + point_right_down_y + ","
        ksdPoint = ksdPoint + point_right_up_x + "," + point_right_up_y + "," + point_left_up_x + "," + point_left_up_y

        cmd0 = "adb shell setprop persist.vendor.hwc.keystone "
        cmd1 = cmd0 + ksdPoint
        print("keystone : " + cmd1)
        os.system(cmd1)
        os.system("adb shell service call SurfaceFlinger 1006")

    def update_data(self):
        position = os.popen("adb shell getprop persist.motor.position").read()
        steps = os.popen("adb shell getprop persist.motor.steps").read()
        self.ui.posValueLabel.setText(position)
        self.ui.stepsValueLabel.setText(steps)
        # self.ui.redSpinBox.setValue(20)
        red_current_value = self.ui.redSpinBox.value()
        print(red_current_value)

    def root_device(self):
        os.system("adb root")
        os.system("adb remount")

    def clean_data(self):
        # os.system("rm -rf .\asuFiles")
        os.system("adb shell rm -rf sdcard/DCIM/asuFiles/* ")
        os.system("adb shell am broadcast -a asu.intent.action.Clear")

        dirExists = os.path.isdir('asuFiles')
        if dirExists:
            shutil.rmtree('asuFiles')
        else:
            print("No find asuFiles")

        fileExists = os.path.isfile('motor.log')
        if fileExists:
            mylog.shutdown()
            os.remove('motor.log')
        else:
            print("No find files")

    def take_picture(self):
        os.system("adb shell am broadcast -a asu.intent.action.TakePicture")

    def save_data(self):
        os.system("adb shell am broadcast -a asu.intent.action.SaveData")

    def pull_data(self):
        os.system("adb pull /sdcard/DCIM/asuFiles")

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
        mylog.logger.debug("-" + cmd2)
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
        mylog.logger.debug("+" + cmd2)
        cmd = cmd1 + cmd2
        print(cmd)
        os.system(cmd)

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

            # self.update_data_timer = QTimer()
            # self.update_data_timer.timeout.connect(self.update_data)
            # self.update_data_timer.start(1000)
            self.ui.getSwVerButton.setEnabled(True)
            self.ui.redSpinBox.setEnabled(True)
            self.ui.redHorizontalSlider.setEnabled(True)
            self.ui.greenSpinBox.setEnabled(True)
            self.ui.greenHorizontalSlider.setEnabled(True)
            self.ui.blueSpinBox.setEnabled(True)
            self.ui.blueHorizontalSlider.setEnabled(True)
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
            # self.update_data_timer.stop()

            self.ui.getSwVerButton.setEnabled(False)
            self.ui.redSpinBox.setEnabled(False)
            self.ui.redHorizontalSlider.setEnabled(False)
            self.ui.greenSpinBox.setEnabled(False)
            self.ui.greenHorizontalSlider.setEnabled(False)
            self.ui.blueSpinBox.setEnabled(False)
            self.ui.blueHorizontalSlider.setEnabled(False)
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
        if cmd_data[0] == 20:
            # self.set_current()
            print(cmd_data[1])
        # define CMD_GET_CURRENTS				20
        # define CMD_GET_FANS						21
        # define CMD_GET_VERSION					22
        # define CMD_GET_TEMPS						23
        # define CMD_GET_IWDG_FLAG				25

        # define CMD_SET_CURRENTS				30
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
    # w.resize(800,500)
    w.show()
    mylog = Logger('motor.log', level='debug')
    mylog.logger.debug("-------------重新启动应用-------------")
    sys.exit(app.exec_())
