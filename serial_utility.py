import base64
import sys
import time
import datetime
import re

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QSettings, Qt
# from qt_material import apply_stylesheet
# import qdarkstyle
# from qdarkstyle.light.palette import LightPalette
# from qdarkstyle.dark.palette import DarkPalette

from my_serial import Ui_MainWindow
from serial_utils import get_ports, open_port

count = 0


def tobool(s):
    if isinstance(s, bool):
        return s
    return s.lower() == 'true'


class SerialThread(QThread):
    data_arrive_signal = pyqtSignal(name='serial_data')

    def __init__(self, ser=None):
        super().__init__()
        self.ser = ser
        self.current_data = b''

    def run(self):
        time.sleep(0.5)  # 防止直接进循环, 阻塞主ui
        while True:
            if self.ser is not None and self.ser.inWaiting():
                self.current_data = self.ser.read(self.ser.inWaiting())
                self.data_arrive_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('自动全向梯形标定')
        self.initialize_ui()
        self.read_settings()

        self.ui.showPattern2Button.clicked.connect(self.show_pattern2)
        self.ui.open_port.clicked.connect(self.open_port)
        self.ui.close_port.clicked.connect(self.close_port)
        self.ui.send_data.clicked.connect(self.send_data)
        self.ui.send_data.clicked.connect(self.check_repeat_send)
        self.ui.clear_screen.clicked.connect(self.clear_screen)
        self.ui.stop_send.clicked.connect(self.stop_send)
        self.ui.refresh_port.clicked.connect(self.refresh_port)

        self.current_port = None
        self.serial_thread = SerialThread(self.current_port)
        self.serial_thread.start()
        self.serial_thread.data_arrive_signal.connect(self.receive_data)

        self.repeat_send_timer = QTimer()
        self.repeat_send_timer.timeout.connect(self.send_data)

    def refresh_port(self):
        """
        刷新串口
        :return:
        """
        available_ports = get_ports()
        self.ui.serial_selection.clear()
        self.ui.serial_selection.addItems(available_ports)

    def check_repeat_send(self):
        """
        是否开启重复发送定时器
        :return:
        """
        if self.ui.repeat_send.checkState() == Qt.Checked:
            send_interval = self.ui.send_interval.value()
            self.repeat_send_timer.start(send_interval)
            self.ui.send_data.setEnabled(False)
            self.ui.stop_send.setEnabled(True)
            self.ui.send_interval.setEnabled(False)
            self.ui.repeat_send.setEnabled(False)

        # 将字符串转为16进制

    def strtohex(self, content):
        total = ''
        for i in content:
            text = base64.b16encode(bytes(i, encoding="gbk"))
            text = text.decode('ascii')
            total = total + text
        result = ''

        for k, v in enumerate(total):
            if not (k % 2) == 0:
                result = result + total[k - 1:k] + v + " "
        return result.rstrip()

    def send_data(self):
        """
        数据发送
        :return:
        """
        global count
        input_data = self.ui.input_data.toPlainText()
        if len(input_data) == 0:
            return
        send_ascii_format = self.ui.send_ascii_format.isChecked()
        print(input_data, send_ascii_format)
        try:
            if send_ascii_format:
                self.current_port.write(input_data.encode('utf-8'))
            else:
                list1 = ["FC FC 01 04 0D 02 02 FF 15 FB FB", "00 02 00 06 00 01 09", "00 02 00 06 00 01 10"]
                Hex_str = bytes.fromhex(input_data)
                count = count + 1
                print("count : %d", count)
                if count > 2:
                    count = 0
                self.current_port.write(Hex_str)
            self.ui.send_data_status.setText('数据发送状态: 成功')
        except:
            self.ui.send_data_status.setText('数据发送状态: 失败')

    def stop_send(self):
        """
        停止发送
        :return:
        """
        self.repeat_send_timer.stop()
        self.ui.send_data.setEnabled(True)
        self.ui.stop_send.setEnabled(False)
        self.ui.repeat_send.setEnabled(True)
        self.ui.send_interval.setEnabled(True)

    def receive_data(self):
        receive_ascii_format = self.ui.receive_ascii_format.isChecked()
        try:
            if receive_ascii_format:
                current_data = self.serial_thread.current_data.decode('utf-8')
            else:
                current_data = self.serial_thread.current_data.hex()
                data_list = re.findall('.{2}', current_data)
                #print(len(data_list), data_list[0], data_list[1], data_list[2])
                current_data = ' '.join(data_list) + ' '
            if self.ui.auto_new_line.checkState() == Qt.Checked and self.ui.show_time.checkState() == Qt.Checked:
                current_data = datetime.datetime.now().strftime('%H:%M:%S') + ' ' + current_data
            if self.ui.auto_new_line.checkState() == Qt.Checked:
                current_data += '\n'
            self.ui.receive_data_area.insertPlainText(current_data)
            if self.ui.scroll_show.isChecked():
                self.ui.receive_data_area.verticalScrollBar().setValue(
                    self.ui.receive_data_area.verticalScrollBar().maximum())
            self.ui.receive_data_status.setText('数据接收状态: 成功')
        except:
            self.ui.receive_data_status.setText('数据接收状态: 失败')

    def clear_screen(self):
        self.ui.receive_data_area.clear()

    def show_pattern2(self):
        print("99999999999999");

    def open_port(self):
        print("88888888");
        current_port_name = self.ui.serial_selection.currentText()
        baud_rate = int(self.ui.baud_rate.currentText())
        bytesize = int(self.ui.data_bit.currentText())
        check_bit = self.ui.check_bit.currentText()[0]
        stop_bit = float(self.ui.stop_bit.currentText())
        print(baud_rate, bytesize, check_bit, stop_bit)
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
            self.repeat_send_timer.stop()
            self.current_port.close()
            self.ui.port_status.setText(self.current_port.port + ' 关闭成功')
            self.ui.open_port.setEnabled(True)
            self.ui.send_data.setEnabled(False)
            self.ui.close_port.setEnabled(False)
            self.ui.stop_send.setEnabled(False)
            self.ui.send_interval.setEnabled(True)
            self.ui.repeat_send.setEnabled(True)
            self.ui.refresh_port.setEnabled(True)
            self.current_port = None
        else:
            self.ui.port_status.setText('无串口可关闭')

    def initialize_ui(self):
        self.ui.send_data.setEnabled(False)
        self.ui.close_port.setEnabled(False)
        self.ui.stop_send.setEnabled(False)
        available_ports = get_ports()
        self.ui.serial_selection.addItems(available_ports)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.current_port is not None:
            self.current_port.close()
        self.serial_thread.terminate()
        self.write_settings()

    def read_settings(self):
        settings = QSettings('serial_config', 'serial_app')
        # window
        if settings.value('windowState') is not None:
            self.restoreState(settings.value('windowState'))
        if settings.value('geometry') is not None:
            self.restoreGeometry(settings.value('geometry'))
        self.ui.serial_selection.setCurrentIndex(int(settings.value('port_name', defaultValue=0)))
        self.ui.data_bit.setCurrentIndex(int(settings.value('data_bit', defaultValue=0)))
        self.ui.check_bit.setCurrentIndex(int(settings.value('check_bit', defaultValue=0)))
        self.ui.stop_bit.setCurrentIndex(int(settings.value('stop_bit', defaultValue=0)))
        self.ui.baud_rate.setCurrentIndex(int(settings.value('baud_rate', defaultValue=0)))
        self.ui.auto_new_line.setChecked(tobool(settings.value('auto_new_line', defaultValue=False)))
        self.ui.repeat_send.setChecked(tobool(settings.value('repeat_send', defaultValue=False)))
        self.ui.show_time.setChecked(tobool(settings.value('show_time', defaultValue=False)))
        self.ui.send_interval.setValue(int(settings.value('send_interval', defaultValue=1000)))
        self.ui.send_ascii_format.setChecked(tobool(settings.value('send_ascii_format', defaultValue=True)))
        self.ui.send_hex_format.setChecked(tobool(settings.value('send_hex_format', defaultValue=False)))
        self.ui.receive_ascii_format.setChecked(tobool(settings.value('receive_ascii_format', defaultValue=True)))
        self.ui.receive_hex_format.setChecked(tobool(settings.value('receive_hex_format', defaultValue=False)))

    def write_settings(self):
        settings = QSettings('serial_config', 'serial_app')
        # window
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        settings.setValue('port_name', self.ui.serial_selection.currentIndex())
        settings.setValue('baud_rate', self.ui.baud_rate.currentIndex())
        settings.setValue('data_bit', self.ui.data_bit.currentIndex())
        settings.setValue('check_bit', self.ui.check_bit.currentIndex())
        settings.setValue('stop_bit', self.ui.stop_bit.currentIndex())
        settings.setValue('auto_new_line', self.ui.auto_new_line.isChecked())
        settings.setValue('repeat_send', self.ui.repeat_send.isChecked())
        settings.setValue('show_time', self.ui.show_time.isChecked())
        settings.setValue('send_interval', self.ui.send_interval.value())
        settings.setValue('send_ascii_format', self.ui.send_ascii_format.isChecked())
        settings.setValue('send_hex_format', self.ui.send_hex_format.isChecked())
        settings.setValue('receive_ascii_format', self.ui.receive_ascii_format.isChecked())
        settings.setValue('receive_hex_format', self.ui.receive_hex_format.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=DarkPalette()))
    w.resize(800, 500)
    w.show()
    sys.exit(app.exec_())

    # import keyword
    # print(keyword.kwlist)
    #
    # #a = input("请输入\n\t你的密码")
    # print(a)
    # if int(a) == 3:
    #     print(sum)
    # print("---------", 6+6, 8+8, 2**3)
    # print(True and False)
    # print(True or False)
    # print(not False)
    # name = "你好我爱你0 1 23456"
    # print(name[0::2])
    # a = "philip"
    # b = "china"
    # c = 10
    # print("nihao,woshi{},wolaizi{}, age{}".format(a, b, c))
    # a = "aiaiai"
    # b = 100
    # c = "dododo"
    # print(F"nihao,woshi {a}, age {b}, length {len(a)}")
    # list1 = [1,"2,3,4","woaini",[10,20,30]]
    # print(len(list1))
    # print(list1[1])
    # list1[1] = "hello"
    # print(list1[1])
    # list1 = [0, 1, 2, 3, 4, 5, 6]
    # list2 = [7, 8, 9]
    #
    # print(list1[1] + list1[2])
    # print(list1 + list2)
    # del list1[1]
    # print(list1[1:6:2])

# # 导入库
# from pyecharts import options as opts
# from pyecharts.charts import Scatter
#
# # 设置销售数据
# week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
# c = Scatter()  # 散点图绘制
# c.add_xaxis(week)
# c.add_yaxis("商家A", [80, 65, 46, 37, 57, 68, 90])
#
# c.set_global_opts(title_opts=opts.TitleOpts(title="一周的销售额（万元）"))  # 设置图表标题
# c.render()
#
# # os.system("render.html")
# c.render_notebook()
#
# c = (
#     Gauge(init_opts=opts.InitOpts(bg_color='#2F4F4F'))
#     .add(
#         '销售部门',
#         [('AA组', 540), ('BB组', 395)],
#         radius="75%",
#         title_label_opts=opts.LabelOpts(font_size=25, color="#FFFFFF"),
#         split_number=10,
#         min_=0,  # 最小刻度
#         max_=600,  # 最大刻度
#         start_angle=225,
#         end_angle=-45,
#         detail_label_opts=opts.LabelOpts(is_show=False),  # 多指针下只显示第一个数值，建议false
#         axisline_opts=opts.AxisLineOpts(
#             linestyle_opts=opts.LineStyleOpts(
#                 color=[(0.3, 'white'), (0.5, '#00FF00'), (0.8, "#00CDCD"), (1, '#fd666d')],
#                 width=30,
#             )
#         )
#     )
#     .set_global_opts(title_opts=opts.TitleOpts(title='销售部年度销量', subtitle='林老头ss',
#                                                title_textstyle_opts=opts.TextStyleOpts(color='#FFFF00', font_size=30),
#                                                subtitle_textstyle_opts={'color': '#D3D3D3', 'font_size': 13},
#                                                pos_left='center'),
#                      legend_opts=opts.LegendOpts(is_show=False))
#     .render('仪表盘示例.html')
# )
# os.system("仪表盘示例.html")

"""
多行屏蔽
True
False
"""
