import os

import cv2
from PyQt5.QtCore import QThread
import time

from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO
from math_utils import CRC


class AutoCalThread(QThread):
    def __init__(self, ser=None, win=None):
        super().__init__()
        self.ser = ser
        self.win = win
        self.position = 0
        self.num = 1
        self.exit = False
        self.CRC = CRC()
        print('>>>>>>>>>>>>>>>>>>> Init AutoCalThread')
        self.positionList = [1, 2, 3, 4, 5, 6]

    def run(self):
        point = get_point()
        self.win.kst_reset()
        while len(self.positionList) > 0:
            if self.exit or self.position >= len(self.positionList):
                print('>>>>>>>>>>>>>>>>>>> Exit AutoCalThread, Save Data Finished')
                self.parse_projector_data()
                self.position = 0
                set_point(point)
                if auto_keystone_calib():
                    print('>>>>>>>>>>>>>>>>>>> 全向标定完成')
                else:
                    print('>>>>>>>>>>>>>>>>>>> 全向标定失败')
                self.win.ui.kstCalButton.setEnabled(True)
                break
            # cmd = '01 06 04 87 00 0A'
            cmdList = ['01', '06', '04', '87', '00', '0A']
            cmdList[5] = '{:02X}'.format(self.positionList[self.position])
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
            cmd1 = str(self.positionList[self.position] - 1)
            os.system(cmd0 + cmd1)
            time.sleep(3.6)
            self.win.cal = True
            self.win.external_take_picture()
            self.win.cal = False

            print('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (len(self.positionList), self.positionList[self.position]))
            self.position += 1

    def parse_projector_data(self):
        startTime = time.time()
        # os.system("adb shell am broadcast -a asu.intent.action.SaveData")
        # time.sleep(2)
        # self.cal = True
        # self.external_take_picture()
        # self.cal = False
        # time.sleep(2.5)
        self.win.pull_data()
        # parse data
        pro_img_list = []
        pro_file_list = []
        ret = {"jpg": 0, "png": 0, "bmp": 0, "txt": 0}
        print("解析目录：", DIR_NAME_PRO)
        for root, dirs, files in os.walk(DIR_NAME_PRO):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:5]
                print(file, ext, head)
                if ext == '.bmp' and head == 'pro_n':
                    ret["bmp"] = ret["bmp"] + 1
                    pro_img_list.append(file)
                if ext == ".png" and head == 'pro_n':
                    ret["png"] = ret["png"] + 1
                if ext == ".txt" and head == 'pro_n':
                    pro_file_list.append(file)
                    ret["txt"] = ret["png"] + 1
        print(pro_img_list)
        print(pro_file_list)
        if len(pro_img_list) > 0:
            pro_img = cv2.imread(DIR_NAME_PRO + pro_img_list[-1])
            pro_img_size = (pro_img.shape[0], pro_img.shape[1])
            imageSize = os.path.getsize(DIR_NAME_PRO + pro_img_list[-1])
            print('最新图片：', len(pro_img_list), pro_img_list[-1], pro_img_size[0], pro_img_size[1], imageSize)
            if pro_img.shape[0] == 720 and pro_img.shape[1] == 1280 and imageSize == 2764854:
                # 图片的大小
                endTime = time.time()
                print('分析数据耗时：', (endTime - startTime))
                # os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/*.bmp ")
                return True
                # self.statusBar_3.setText('当前姿态下数据保存完成')
            else:
                # self.statusBar_3.setText('当前姿态下数据保存失败')
                return False
        else:
            print('没有发现投影设备返回的图片数据 ', pro_file_list)
            return False
            # self.statusBar_3.setText('当前姿态下数据保存失败')
        self.ui.saveDataButton.setEnabled(True)
