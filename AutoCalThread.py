import json
import os

import cv2
from PyQt5.QtCore import QThread
import time

import globalVar
from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2
from math_utils import CRC


class AutoCalThread(QThread):
    def __init__(self, ser=None, win=None):
        super().__init__()
        self.ser = ser
        self.win = win
        self.position = 0
        self.num = 1
        # 转台完成动作后，稳定时间
        self.delay1 = 1.6
        # 发出保存数据后，等待时间
        self.delay2 = 2
        # 外部相机保存时间
        self.delay3 = 1.6
        self.enableAlgo = True
        self.exit = False
        self.CRC = CRC()
        print('>>>>>>>>>>>>>>>>>>> Init AutoCalThread')
        self.positionList = [1, 2, 3, 4, 5, 6]
        self.pos_init_finished = False

    def run(self):
        print('自动全向梯形标定 开始：', self.positionList)
        # print(self.parse_projector_json())
        # return
        start_time = time.time()
        if self.position == 0 and self.positionList[self.position] == 1 and len(self.positionList) > 5:
            # 直接到第一个位置，只有第一次在第一個位置時運行
            cmdList = ['01', '06', '04', '87', '00', '01']
            cmdChar = ' '.join(cmdList)
            crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
            cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
            cmdHex = bytes.fromhex(cmdChar)
            if self.ser is not None:
                self.ser.write(cmdHex)
            else:
                print('>>>>>>>>>>>>>>>>>>>> 串口异常')
            time.sleep(2.6)
            #os.system('adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')
            # time.sleep(2)
            # 只有自动标定会走到这里
            # os.system('adb install -r app-debug.apk')
            print('启动投影仪校准服务')
            os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
            # os.system("adb shell am stopservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
            # time.sleep(1)
            os.system("adb shell am startservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
            time.sleep(2.9)
            os.system('adb shell am broadcast -a asu.intent.action.KstReset')
            os.system('adb shell am broadcast -a asu.intent.action.TofCal')
            # self.win.showWritePattern()
            time.sleep(1.9)
            self.win.showCheckerPattern()
            self.pos_init_finished = True
        while len(self.positionList) > 0:
            if self.exit:
                os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
                self.position = 0
                self.exit = False
                print('>>>>>>>>>>>>>>>>>>> 紧急退出自动标定线程')
                break
            if self.enableAlgo:
                if len(self.positionList) == 1 and self.positionList[0] == -1:
                    self.position = 1
                    print('>>>>>>>>>>>>>>>>>>> 跳过数据采集，直接运行算法')
            else:
                print(' >>>>>>>>>>>>>>>>>>> 算法未使能')
            if self.position >= len(self.positionList):
                time.sleep(1.5)  # 2
                print('>>>>>>>>>>>>>>>>>>> 开始解析数据')
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
                self.win.pv -= len(self.positionList) * 10
                print('>>>>>>>>>>>>>>>>>>> %d个姿态有错误, ' % len(self.positionList))
                print(">>>>>>>>>>>>>>>>>>> ", self.positionList)
                self.position = 0
                if len(self.positionList) == 0:
                    self.win.pv += 5
                    os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
                    end0_time = time.time()
                    print('数据抓取及解析耗时：' + str((end0_time - start_time)))
                    print(proj_data)
                    if self.enableAlgo:
                        if auto_keystone_calib2(proj_data):
                            end1_ime = time.time()
                            print('算法运行耗时：' + str((end1_ime - end0_time)))
                            cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
                            os.system(cmd)
                            # os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/* ")
                            # self.win.clean_data()
                            os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
                            self.win.pv += 5
                            print('>>>>>>>>>>>>>>>>>>> 全向标定完成，总耗时：', str(end1_ime - start_time))
                            # os.system("adb shell am stopservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
                            # set_point(point)
                        else:
                            print('>>>>>>>>>>>>>>>>>>> 全向标定失败')
                    else:
                        print('未使能算法')
                    break
            print('>>>>>>>>>>>>>>>>>>>>> 控制转台到第%d个姿态 %d' % (self.positionList[self.position], self.position))
            cmdList = ['01', '06', '04', '87', '00', '0A']
            cmdList[5] = '{:02X}'.format(self.positionList[self.position])
            cmdChar = ' '.join(cmdList)
            crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
            cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
            # print(cmdChar)
            cmdHex = bytes.fromhex(cmdChar)
            if self.ser is not None:
                self.ser.write(cmdHex)
            else:
                print('>>>>>>>>>>>>>>>>>>>> 串口异常')

            time.sleep(self.delay1)

            print('>>>>>>>>>>>>>>>>>>>>> 开始保存第%d个姿态的数据 ' % self.positionList[self.position])
            cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
            cmd1 = str(self.positionList[self.position] - 1)
            os.system(cmd0 + cmd1)
            time.sleep(self.delay2)
            self.win.cal = True
            self.win.external_take_picture(self.positionList[self.position] - 1)
            time.sleep(self.delay3)
            self.win.cal = False
            print('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (len(self.positionList), self.positionList[self.position]))
            self.position += 1
            self.win.pv += 10
        # 标定结束，转台归位
        self.win.pv = 100
        cmdList = ['01', '06', '04', '87', '00', '01']
        cmdChar = ' '.join(cmdList)
        crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
        cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
        cmdHex = bytes.fromhex(cmdChar)
        if self.ser is not None:
            print('云台回到第一个位置')
            self.ser.write(cmdHex)
        else:
            print('>>>>>>>>>>>>>>>>>>>> 串口异常')

        os.system('adb shell setprop persist.sys.keystone.type 0')
        os.system('adb shell settings put global AsuAutoKeyStoneEnable 1')
        os.system('adb shell settings put global tv_auto_focus_asu 1')
        os.system('adb shell settings put global tv_image_auto_keystone_asu 1')
        os.system('adb shell settings put global tv_image_auto_keystone_poweron 0')
        os.system('adb shell settings put global tv_auto_focus_poweron 1')
        os.system('adb shell settings put system tv_screen_saver 1')
        os.system('adb reboot')
        self.win.ui.kstCalButton.setEnabled(True)

    def parse_projector_data(self):
        pos_error = [0] * 8
        startTime = time.time()

        self.win.pull_data()
        # parse data
        pro_img_list = []
        pro_file_list = []
        ret = {"jpg": 0, "png": 0, "bmp": 0, "txt": 0}
        print("解析目录：", globalVar.get_value('DIR_NAME_PRO'))
        for root, dirs, files in os.walk(globalVar.get_value('DIR_NAME_PRO')):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:5]
                full_head = os.path.splitext(file)[0]
                if ext == ".txt" and head == 'pro_n':
                    pro_file_list.append(file)
                    ret["txt"] = ret["png"] + 1
                if ext == '.bmp' and head == 'pro_n':
                    ret["bmp"] = ret["bmp"] + 1
                    pro_img_list.append(file)
                if ext == ".png" and head == 'pro_n':
                    ret["png"] = ret["png"] + 1
        print(pro_img_list)
        print(pro_file_list)

        tof_list = []
        imu_list = []
        img_list = []
        txt_list = []
        for i in range(max(len(pro_img_list), len(pro_file_list))):
            name = "pro_n" + str(i)
            print('============================= ', name)
            print('++++++++++++++++++++++++++ ', "".join(list(filter(str.isdigit, name))))
            if int("".join(list(filter(str.isdigit, name)))) > 7:
                break

            file_name = globalVar.get_value('DIR_NAME_PRO') + '/' + name + '.txt'
            img_name = globalVar.get_value('DIR_NAME_PRO') + '/' + name + '.bmp'
            if os.path.exists(file_name):
                txt_list.append(file_name)
                file = open(file_name)
                row = 0
                while row < 4:  # 直到读取完文件
                    line = file.readline().strip()  # 读取一行文件，包括换行符
                    if row == 1:
                        if len(line.split(',')) == 6:
                            tof_list += line.split(',')
                            print('+++++++++++++++++', tof_list)
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
                    print('图片尺寸不对')
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
        print('解析投影文件耗时', endTime-startTime)
        return pos_error, tof_list, imu_list, img_list

    def parse_projector_json(self):
        pos_count = 8
        pos_error = [0] * 8

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        dir_ref_path = globalVar.get_value('DIR_NAME_REF')

        tof_list = []
        imu_list = []
        ref_img_list = []
        pro_img_list = []

        # 分析json数据
        file_pro_path = dir_pro_path + "AsuProjectorPara.json"
        if os.path.isfile(file_pro_path):
            file = open(file_pro_path, )
            dic = json.load(file)
            if len(dic) > 0:
                for i in range(pos_count):
                    pos = 'POS' + str(i)
                    if pos in dic.keys():
                        if 'tof' in dic[pos].keys():
                            data = list(map(float, dic[pos]['tof'].split(',')))
                            if len(data) == 4:
                                tof_list += data
                            else:
                                pos_error[i] = -1
                        else:
                            pos_error[i] = -1
                        if 'imu' in dic[pos].keys():
                            data = list(map(float, dic[pos]['imu'].split(',')))
                            if len(data) == 5:
                                imu_list += data
                            else:
                                pos_error[i] = -1
                        else:
                            pos_error[i] = -1
                    else:
                        pos_error[i] = -1
            file.close()

            # 分析外部相机图片
            ref_list = []
            ret = {"jpg": 0, "png": 0, "bmp": 0}
            for root, dirs, files in os.walk(dir_ref_path):
                for file in files:
                    ext = os.path.splitext(file)[-1].lower()
                    head = os.path.splitext(file)[0].lower()[:3]
                    if ext == '.png':
                        ret["jpg"] = ret["jpg"] + 1
                    if ext == ".bmp" and head == 'ref':
                        # ref_img_list.append(dir_ref_path + file)
                        ref_img = cv2.imread(dir_ref_path + file)
                        ref_img_size = (ref_img.shape[0], ref_img.shape[1])
                        print('外部相机尺寸: ', ref_img_size[0], ' 列Col:', ref_img_size[1])
                        ref_list.append(file)
                        ret["bmp"] = ret["bmp"] + 1

            # 分析内部相机图片
            pro_list = []
            ret = {"jpg": 0, "png": 0, "bmp": 0}
            for root, dirs, files in os.walk(dir_pro_path):
                for file in files:
                    ext = os.path.splitext(file)[-1].lower()
                    head = os.path.splitext(file)[0].lower()[:3]
                    if ext == '.png':
                        ret["jpg"] = ret["jpg"] + 1
                    if ext == ".bmp" and head == 'pro':
                        # ref_img_list.append(dir_ref_path + file)
                        pro_img = cv2.imread(dir_pro_path + file)
                        pro_img_size = (pro_img.shape[0], pro_img.shape[1])
                        print('内部相机尺寸: ', pro_img_size[0], ' 列Col:', pro_img_size[1])
                        pro_list.append(file)
                        ret["bmp"] = ret["bmp"] + 1

            for i in range(pos_count):
                img = 'ref_n' + str(i) + '.bmp'
                print(pro_list)
                if img in ref_list:
                    ref_img_list.append(dir_ref_path + img)
                else:
                    pos_error[i] = -1
                img = 'pro_n' + str(i) + '.bmp'
                if img in pro_list:
                    pro_img_list.append(dir_pro_path + img)
                else:
                    pos_error[i] = -1

            if pos_count != ret["bmp"]:
                print('图片数量不对')
        return pos_error, tof_list, imu_list, ref_img_list, pro_img_list
