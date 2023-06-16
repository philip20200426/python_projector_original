import os

from PyQt5.QtCore import QThread
import time

from pro_correct_wrapper import set_point, get_point, auto_keystone_calib
from math_utils import CRC


class AutoCalThread(QThread):
    def __init__(self, ser=None, win=None):
        super().__init__()
        self.ser = ser
        self.win = win
        self.position = 1
        self.num = 1
        self.exit = False
        self.CRC = CRC()
        print('>>>>>>>>>>>>>>>>>>> Init AutoCalThread')

    def run(self):
        point = get_point()
        self.win.kst_reset()
        while True:
            if self.exit or self.position > self.num:
                print('>>>>>>>>>>>>>>>>>>> Exit AutoCalThread, Save Data Finished')
                self.win.parse_position_data()
                self.position = 1
                set_point(point)
                # if auto_keystone_calib():
                #     print('>>>>>>>>>>>>>>>>>>> 全向标定完成')
                # else:
                #     print('>>>>>>>>>>>>>>>>>>> 全向标定失败')
                self.win.ui.kstCalButton.setEnabled(True)
                break
            # cmd = '01 06 04 87 00 0A'
            cmdList = ['01', '06', '04', '87', '00', '0A']
            cmdList[5] = '{:02X}'.format(self.position)
            cmdChar = ' '.join(cmdList)
            crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
            cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
            print(cmdChar)
            cmdHex = bytes.fromhex(cmdChar)
            if self.ser is not None:
                self.ser.write(cmdHex)
            else:
                print('>>>>>>>>>>>>>>>>>>>> 串口异常')
            time.sleep(3.6)
            print('>>>>>>>>>>>>>>>>>>>> 开始保存数据')

            cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
            cmd1 = str(self.position - 1)
            os.system(cmd0 + cmd1)
            time.sleep(3.6)
            self.win.cal = True
            self.win.external_take_picture()
            self.win.cal = False

            print('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (self.num-1, self.position))
            self.position += 1
