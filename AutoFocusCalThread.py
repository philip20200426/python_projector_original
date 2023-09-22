import json
import os

import cv2
from PyQt5.QtCore import QThread
import time

import HuiYuanRotate
import globalVar
from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2
from math_utils import CRC


class AutoFocusCalThread(QThread):
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
        print('>>>>>>>>>>>>>>>>>>> Init AutoFocusCalThread')
        self.positionList = [1, 2, 3, 4, 5, 6]
        self.pos_init_finished = False
        self.dis_steps = [-1, -1]

    def run(self):
        start_time = time.time()
        self.init()
        time.sleep(2.6)
        if not self.win.ui.getTofCheckBox.isChecked():
            print('开始自动化标定：')
            self.win.showWritePattern()
            # os.system('adb shell am broadcast -a asu.intent.action.TofCal')
            # self.win.ui.autoFocusLabel.setText('启动TOF校准')
            # time.sleep(1)

            # 控制转台左转15度
            HuiYuanRotate.hy_control(self.ser, 15, 0)
            time.sleep(4.6)
            # 触发全向 触发对焦
            self.auto_ai_feature()
            time.sleep(11)

            print('开始读取投影自动对焦后的马达位置')
            left_para_auto = self.read_para()
            print('自动对焦后的马达数据：', left_para_auto)
            left_steps = left_para_auto[1]

            # 基于外部CAM对焦，返回当前马达位置
            self.win.auto_cam_af_cal()
            time.sleep(39)
            print('开始读取外部CAM对焦后的马达位置')
            left_para_cam = self.read_para()
            left_ex_steps = left_para_cam[1]
            print('左投外部对焦：', left_para_cam)
            gap = left_ex_steps - left_steps
            print('GAP:', gap)

            # 控制转台到0度
            HuiYuanRotate.hy_control(self.ser, 0, 0)
            time.sleep(3)
            # 触发自动梯形和自动对焦
            # 触发全向
            self.auto_ai_feature()
            time.sleep(5)
            center_para_auto = self.read_para()
            print('中心：', center_para_auto)
            target_dis = center_para_auto[1] + gap
            self.dis_steps[1] = target_dis
            print(self.dis_steps, target_dis, center_para_auto, gap)
            self.win.auto_focus_motor()
            self.win.write_to_nv()
            self.win.removePattern()
        else:
            print('开始保存数据：')
            left_para_auto = self.read_para()
            print(left_para_auto)

    def init(self):
        # self.win.ui.autoFocusLabel.setText('安装标定APK')
        # os.system('adb install -r app-debug.apk')
        os.system("adb shell mkdir /sdcard/DCIM/projectionFiles")
        os.system("adb push AsuFocusPara.json /sdcard/DCIM/projectionFiles/AsuProjectorPara.json")
        os.system("adb shell am startservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
        self.win.ui.autoFocusLabel.setText('启动标定服务')

    def auto_ai_feature(self):
        # 触发自动梯形和自动对焦
        # 触发全向
        # os.system(
        #    'adb shell am startservice -n com.asu.asuautofunction/com.asu.asuautofunction.AsuSessionService -a "com.asu.projector.focus.AUTO_FOCUS" --ei type 0 flag 0')
        # 触发对焦
        os.system(
            'adb shell am startservice -n com.asu.asuautofunction/com.asu.asuautofunction.AsuSessionService -a "com.asu.projector.focus.AUTO_FOCUS" --ei type 2 flag 0')
        # # 触发自动梯形和自动对焦
        # # 触发全向
        # os.system(
        #     'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 2 flag 0')
        # # 触发对焦
        # os.system(
        #     'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')

    def read_para(self):
        self.win.ui.autoFocusLabel.setText('保存位置数据')
        cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
        cmd1 = '11'
        cmd = cmd0 + cmd1
        os.system(cmd)

        time.sleep(2.9)
        self.win.ui.autoFocusLabel.setText('开始分析数据')
        self.win.pull_data()

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        file_pro_path = dir_pro_path + "AsuProjectorPara.json"
        if os.path.isfile(file_pro_path):
            file = open(file_pro_path, )
            dic = json.load(file)
            if len(dic) > 0 and 'POS11' in dic.keys() and 'tof' in dic['POS11'].keys():
                if dic['POS11']['tof'] != '':
                    # print(dic['POS11']['tof'].split(',')[0])
                    self.dis_steps[0] = int(dic['POS11']['tof'].split(',')[0])
            if len(dic) > 0 and 'POS11' in dic.keys() and 'location' in dic['POS11'].keys():
                if dic['POS11']['location'] != '':
                    # print(dic['POS11']['location'])
                    self.dis_steps[1] = dic['POS11']['location']
            file.close()
        location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
        if location != '':
            location = location[9:-1]
        self.dis_steps[1] = int(location)
        para = 'TOF: ' + str(self.dis_steps[0]) + '  马达: ' + str(self.dis_steps[1])
        self.win.ui.autoFocusLabel.setText(para)
        print('TOF:' + str(self.dis_steps[0]) + ',马达位置:' + str(self.dis_steps[1]) + ',马达location:' + location)
        return self.dis_steps

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
        print('解析投影文件耗时', endTime - startTime)
        return pos_error, tof_list, imu_list, img_list
