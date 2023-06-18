import os

import cv2
from PyQt5.QtCore import QThread
import time

from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2
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
        print(self.positionList)
        while len(self.positionList) > 0:
            if self.exit:
                os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
                self.position = 0
                print('>>>>>>>>>>>>>>>>>>> 紧急退出自动标定线程')
                break

            if self.position >= len(self.positionList):
                time.sleep(1.5)  # 2
                print('>>>>>>>>>>>>>>>>>>> Exit AutoCalThread, Save Data Finished')
                proj_data = self.parse_projector_data()
                print(proj_data[0])
                for pos in range(len(self.positionList)):
                    if proj_data[0][pos] != -1:
                        self.positionList[pos] = 0
                print(self.positionList)
                self.positionList = list(set(self.positionList))
                print(self.positionList)
                if 0 in self.positionList:
                    self.positionList.remove(0)
                print(">>>>>>>>>>>>>>>>>>> ", self.positionList)
                self.position = 0
                if len(self.positionList) == 0:
                    os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
                    self.win.ui.kstCalButton.setEnabled(True)
                    if auto_keystone_calib2(proj_data):
                        print('>>>>>>>>>>>>>>>>>>> 全向标定完成')
                        set_point(point)
                    else:
                        print('>>>>>>>>>>>>>>>>>>> 全向标定失败')
                    break

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
            time.sleep(1.6) # 3.6
            print('>>>>>>>>>>>>>>>>>>>> 开始保存数据')

            cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
            cmd1 = str(self.positionList[self.position] - 1)
            os.system(cmd0 + cmd1)
            time.sleep(0.5) # 2
            self.win.cal = True
            self.win.external_take_picture(self.positionList[self.position] - 1)
            time.sleep(0.5) # 1.6
            self.win.cal = False
            print('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (len(self.positionList), self.positionList[self.position]))
            self.position += 1

    def parse_projector_data(self):
        pos_error = [0] * 8
        startTime = time.time()

        self.win.pull_data()
        # parse data
        pro_img_list = []
        pro_file_list = []
        ret = {"jpg": 0, "png": 0, "bmp": 0, "txt": 0}
        #DIR_NAME_PRO = "asuFiles/ASUXMJGYYD2V0220230200514/projectionFiles"
        print("解析目录：", DIR_NAME_PRO)
        for root, dirs, files in os.walk(DIR_NAME_PRO):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:5]
                # print(file, ext, head)
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

        tof_list = []
        imu_list = []
        img_list = []
        txt_list = []
        for i in range(max(len(pro_img_list), len(pro_file_list))):
            name = "pro_n" + str(i)
            file_name = DIR_NAME_PRO + '/' + name + '.txt'
            img_name = DIR_NAME_PRO + '/' + name + '.bmp'
            if os.path.exists(file_name):
                txt_list.append(file_name)
                file = open(file_name)
                row = 0
                while row < 4:  # 直到读取完文件
                    line = file.readline().strip()  # 读取一行文件，包括换行符
                    if row == 1:
                        if len(line.split(',')) == 4:
                            tof_list += line.split(',')
                        else:
                            pos_error[i] = -1
                    if row == 2:
                        if len(line.split(',')) == 5:
                            imu_list += line.split(',')
                        else:
                            pos_error[i] = -1
                    row += 1
                file.close()  # 关闭文件
            else:
                pos_error[i] = -1

            if os.path.exists(img_name):
                imageSize = os.path.getsize(img_name)
                if imageSize == 2764854:
                    img_list.append(img_name)
                else:
                    pos_error[i] = -1
            else:
                pos_error[i] = -1
        tof_list = list(map(float, tof_list))
        imu_list = list(map(float, imu_list))
        # print(len(tof_list), tof_list)
        # print(len(imu_list), imu_list)
        # print(len(img_list), img_list)
        # print(pos_error)
        endTime = time.time()
        # 秒
        print(endTime-startTime)
        return pos_error, tof_list, imu_list, img_list

