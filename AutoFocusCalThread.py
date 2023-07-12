import json
import os

import cv2
from PyQt5.QtCore import QThread
import time

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

    def run(self):
        print('自动对焦标定 开始：')
        start_time = time.time()
        pos11_steps = self.win.ui.pos11StepsEdit.text()

        self.win.ui.autoFocusLabel.setText('安装标定APK')
        os.system('adb install -r app-debug.apk')
        os.system("adb shell mkdir /sdcard/DCIM/projectionFiles")
        os.system("adb push AsuFocusPara.json /sdcard/DCIM/projectionFiles/AsuProjectorPara.json")
        os.system("adb shell am startservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
        self.win.ui.autoFocusLabel.setText('启动标定服务')
        time.sleep(2.6)
        os.system('adb shell am broadcast -a asu.intent.action.TofCal')
        self.win.ui.autoFocusLabel.setText('启动TOF校准')
        time.sleep(1)
        self.win.ui.autoFocusLabel.setText('保存位置数据')
        cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
        cmd1 = '11'
        cmd = cmd0 + cmd1
        os.system(cmd)

        time.sleep(3.6)
        self.win.ui.autoFocusLabel.setText('开始分析数据')
        self.win.pull_data()

        dis_steps = ['-1', pos11_steps]

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        file_pro_path = dir_pro_path + "AsuProjectorPara.json"
        if os.path.isfile(file_pro_path):
            file = open(file_pro_path, )
            dic = json.load(file)
            if len(dic) > 0 and 'POS11' in dic.keys() and 'tof' in dic['POS11'].keys():
                if dic['POS11']['tof'] != '':
                    print(dic['POS11']['tof'].split(',')[0])
                    dis_steps[0] = dic['POS11']['tof'].split(',')[0]
                    print(pos11_steps)
            if len(dic) > 0 and 'POS11' in dic.keys() and 'steps' in dic['POS11'].keys():
                if dic['POS11']['steps'] != '':
                    print(dic['POS11']['steps'])
                    dis_steps[1] = str(dic['POS11']['steps'])
                    if dis_steps[1] != pos11_steps:
                        self.win.ui.autoFocusLabel.setText('马达位置错误')
                        print('马达位置错误')
                        return
            file.close()
        print(dis_steps)

        file_path = globalVar.get_value('CALIB_DATA_PATH')
        file_pro_path1 = dir_pro_path + "pro_n11.txt"
        file_pro_path2 = dir_pro_path + "pro_n12.txt"
        if os.path.exists(file_pro_path1):
            tof_list = []
            file = open(file_pro_path1)
            row = 0
            while row < 4:  # 直到读取完文件
                line = file.readline().strip()  # 读取一行文件，包括换行符
                if row == 1:
                    tof_list += line.split(',')
                    dis_steps[0] = tof_list[0]
                    break
                row += 1
            file.close()  # 关闭文件

            prefix = 'FocusA: [ '
            suffix = ' ]\n'
            da = prefix + ",".join(dis_steps) + suffix
            print(da)
            with open(file_path, "a") as f1:
                f1.write('%YAML:1.0\n')
                f1.write('---\n')
                f1.write(da)
            self.win.ui.autoFocusLabel.setText('开始写入数据')
            cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
            print(cmd)
            os.system(cmd)
            os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
            self.win.ui.autoFocusLabel.setText('标定完成')
        else:
            self.win.ui.autoFocusLabel.setText('数据异常')
            print(file_pro_path1, '文件不存在')

        os.system('adb shell settings put global tv_auto_focus_asu 1')
        # os.system('adb shell settings put global tv_image_auto_keystone_asu 1')
        os.system('adb shell setprop persist.sys.keystone.type 0')
        ksd_para = os.popen('adb shell cat sys/devices/platform/asukey/ksdpara').read()
        index = ksd_para.find('FocusA')
        print(ksd_para)
        result = ksd_para[index+8: index+21]
        print(len(ksd_para), index, result)
        self.win.ui.autoFocusLabel.setText(result)
        os.system('adb shell "rm -rf /sdcard/DCIM/projectionFiles/pro_n11.txt"')
        os.system('adb shell "rm -rf /sdcard/DCIM/projectionFiles/pro_n11.bmp"')

        # print(index)

        # os.system('adb reboot ')

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
