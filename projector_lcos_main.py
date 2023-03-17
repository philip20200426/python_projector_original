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
            if self.ser is not None and self.ser.inWaiting():
                self.current_data = self.ser.read(self.ser.inWaiting())
                self.data_arrive_signal.emit()


class ProjectorWindow(QMainWindow, Ui_MainWindow):
    update_temp_flag = False

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('调试工具')
        self.initialize_ui()

        self.ui.getSwVerButton.clicked.connect(self.get_sw_version)
        self.ui.savePduDataButton.clicked.connect(self.save_pdu_data)
        self.ui.fan1HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.fan2HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.fan3HorizontalSlider.valueChanged['int'].connect(self.set_fan_speed)
        self.ui.redHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.greenHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.blueHorizontalSlider.valueChanged['int'].connect(self.set_current)
        self.ui.redMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)
        self.ui.greenMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)
        self.ui.blueMaxHorizontalSlider.valueChanged['int'].connect(self.set_max_current)

        self.ui.motorBackButton.clicked.connect(self.motor_back)
        self.ui.motorForwardButton.clicked.connect(self.motor_forward)
        self.ui.updateTempButton.clicked.connect(self.update_temperature)

        self.ui.open_port.clicked.connect(self.open_port)
        self.ui.close_port.clicked.connect(self.close_port)
        self.ui.refresh_port.clicked.connect(self.refresh_port)
        self.ui.send_data.clicked.connect(self.send_data)

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        self.serial_thread.start()
        self.serial_thread.data_arrive_signal.connect(self.receive_data)

        # self.ui.getSwVerButton.setEnabled(False)
        # self.ui.redSpinBox.setEnabled(False)
        # self.ui.redHorizontalSlider.setEnabled(False)
        # self.ui.greenSpinBox.setEnabled(False)
        # self.ui.greenHorizontalSlider.setEnabled(False)
        # self.ui.blueSpinBox.setEnabled(False)
        # self.ui.blueHorizontalSlider.setEnabled(False)

    def motor_back(self):
        data = [1, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        print(data)
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.current_port.write(strHex)

    def motor_forward(self):
        data = [0, 0, 0]
        # 步数用两个字节表示，低字节在前，高字节在后
        print(hex(int(self.ui.motorStepsEdit.text())))
        data[1] = int(self.ui.motorStepsEdit.text()) & 0x00FF
        data[2] = int(self.ui.motorStepsEdit.text()) >> 8
        print(data)
        strHex = asu_pdu_build_one_frame('CMD_SET_FOCUSMOTOR', len(data), data)
        self.current_port.write(strHex)

    def save_pdu_data(self):
        #PARA_CURRENT 0
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
        #data = list()
        data = [0, 0, 0, 1]
        print(len(data))
        data[0] = int(self.ui.fan1HorizontalSlider.value())
        data[1] = int(self.ui.fan2HorizontalSlider.value())
        data[2] = int(self.ui.fan3HorizontalSlider.value())
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

    def set_max_current(self):
        data = [0, 0, 0]
        data[0] = int(self.ui.redMaxHorizontalSlider.value())
        data[1] = int(self.ui.greenMaxHorizontalSlider.value())
        data[2] = int(self.ui.blueMaxHorizontalSlider.value())
        strHex = asu_pdu_build_one_frame('CMD_SET_MAX_CURRENTS', len(data), data)
        self.current_port.write(strHex)
        time.sleep(0.05)

    def update_data(self):
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

    def open_port(self):
        print("88888888")
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
        self.ui.receive_data_area.clear()
        receive_ascii_format = False
        raw_data_list = self.serial_thread.current_data
        # cmd_data = ()  # 如果下面不分开，通过元祖接收
        cmd, length, dataList = asu_pdu_parse_one_frame(raw_data_list)
        print("parse data : ", cmd, length, dataList)
        if cmd in mPduCmdDict2Rev.keys():
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_VERSION':
                sw_version = str(dataList[0]) + "." \
                             + str(dataList[1]) + "." \
                             + str(dataList[2])
                self.ui.label_sw_version.setText(sw_version)
            if mPduCmdDict2Rev[cmd] == 'CMD_GET_TEMPS':
                self.ui.temp1Label.setText(str(dataList[0]))    # 背光
                self.ui.temp2Label.setText(str(dataList[1]))    # 显示屏
            if mPduCmdDict2Rev[cmd] == 'CMD_SET_FOCUSMOTOR':
                print("motor callback data : ", cmd, dataList)
                self.ui.motorStatuslabel.setText(str(dataList[0]))
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
            #self.ui.port_status.setText('数据接收状态: 成功')
        except:
            pass
            #self.ui.port_status.setText('数据接收状态: 失败')

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
