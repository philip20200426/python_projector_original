import csv
import datetime
import json
import os

import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import time

from PyQt5.QtGui import QPixmap

import Constants
import HuiYuanRotate
import ProjectorDev
import globalVar
from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2
from math_utils import CRC


class AutoFocusCalThread(QThread):
    auto_cal_callback = pyqtSignal(str)
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

    # From auto_focus_cal
    def run(self):
        cal_start = time.time()
        right_steps2 = 0
        af_cal_result = []
        os.system("adb shell mkdir /sdcard/DCIM/projectionFiles")
        # self.win.ui.autoFocusLabel.setText('启动对焦标定服务')
        # time.sleep(2.6)
        print('开始对焦自动化标定')
        # ProjectorDev.pro_show_pattern_af()
        # os.system('adb shell am broadcast -a asu.intent.action.TofCal')
        # self..win.ui.autoFocusLabel.setText('启动TOF校准')
        # time.sleep(1)
        self.win.ui.calResultEdit.append('对焦标定开始...')
        self.win.ui.calResultEdit.append('正投自动对焦')
        # 控制转台到0度
        self.win.pv += Constants.CAL_PROGRESS_STEP
        # ProjectorDev.motor_reset()
        # 梯形标定完成后，默认就是正投状态，不需要再控制云台
        # HuiYuanRotate.hy_control(self.ser, 0, 0)
        # time.sleep(3)
        # 触发自动梯形和自动对焦
        ProjectorDev.pro_auto_af_kst_cal(1)
        time.sleep(1.6)
        dis_steps_c = self.read_para()
        print('投影段正投对焦后马达位置：', dis_steps_c[1])
        center_steps = dis_steps_c[1]

        # 控制转台左转15度
        self.win.pv += Constants.CAL_PROGRESS_STEP
        HuiYuanRotate.hy_control(self.ser, -15, 0)
        time.sleep(3.6)
        # 触发全向和自动对焦
        self.win.ui.calResultEdit.append('左15°对焦标定')
        if ProjectorDev.pro_auto_af_kst_cal(2):
            self.win.ui.calResultEdit.append('投影自动对焦失败，直接退出！！！')
            return
        time.sleep(2.6)
        # print('开始读取投影自动对焦后的马达位置')
        dis_steps_l = self.read_para()
        left_steps = dis_steps_l[1]
        # print('投影自动对焦后，马达位置：', left_steps, left_para_auto)
        # 基于外部CAM对焦，返回当前马达位置
        self.win.ex_cam_af()
        time.sleep(1)
        left_ex_steps = self.win.ex_cam_af_thread.get_result()
        left_ex_steps = left_ex_steps - Constants.DEV_LOCATION_STEPS_OFFSET
        left_gap = left_ex_steps - left_steps

        # 控制转台右转15度
        self.win.pv += Constants.CAL_PROGRESS_STEP
        HuiYuanRotate.hy_control(self.ser, 15, 0)
        time.sleep(3.6)
        # 触发全向和自动对焦
        self.win.ui.calResultEdit.append('右15°对焦标定')
        if ProjectorDev.pro_auto_af_kst_cal(2):
            self.win.ui.calResultEdit.append('投影自动对焦失败，直接退出！！！')
            return
        time.sleep(2.6)
        # print('开始读取投影自动对焦后的马达位置')
        dis_steps_r = self.read_para()
        right_steps = dis_steps_r[1]
        self.win.ex_cam_af()
        time.sleep(1)
        right_ex_steps = self.win.ex_cam_af_thread.get_result()
        right_ex_steps = right_ex_steps - Constants.DEV_LOCATION_STEPS_OFFSET
        ProjectorDev.pro_show_pattern(0)
        right_gap = right_ex_steps - right_steps

        gap = (right_gap + left_gap) / 2

        target_steps = center_steps + gap
        self.dis_steps[1] = target_steps
        print('投影对焦标定后的数据,距离和马达位置：', self.dis_steps)

        if self.dis_steps[0] > Constants.DIS_STEPS_1 and self.dis_steps[1] > Constants.DIS_STEPS_1:
            self.win.auto_focus_motor()
            self.win.write_to_nv()
            self.win.ui.calResultEdit.append('对焦标定完成')

            # 对焦标定评估
            self.win.pv += Constants.CAL_PROGRESS_STEP
            self.win.ui.calResultEdit.append('对焦标定评估开始')
            HuiYuanRotate.hy_control(self.ser, 15, 0)
            time.sleep(2.6)
            ProjectorDev.pro_auto_af_kst_cal(2)
            time.sleep(3.6)
            dis_steps_r2 = self.read_para()
            right_steps2 = dis_steps_r2[1]
            if abs(right_steps2 - right_ex_steps) < 100:
                self.win.ui.calResultEdit.append('<font color="green" size="6">{}</font>'.format('对焦标定成功'))
                pix_white = QPixmap('res/pass.png')
                self.win.ui.calAfResultLabel.setPixmap(pix_white)
            else:
                self.win.ui.calResultEdit.append('<font color="green" size="6">{}</font>'.format('对焦标定失败'))

            print('对焦标定结果：', right_steps2, right_ex_steps)
        else:
            self.win.ui.calResultEdit.append('对焦标定失败，直接退出！！！')

        # 保存对焦标定数据
        af_cal_result.append(right_steps)
        af_cal_result.append(right_ex_steps)
        af_cal_result.append(right_gap)
        af_cal_result.append(left_steps)
        af_cal_result.append(left_ex_steps)
        af_cal_result.append(left_gap)
        af_cal_result.append(center_steps)
        af_cal_result.append(gap)
        af_cal_result.append(right_steps2)
        sn = globalVar.get_value('SN')
        result = self.dis_steps + af_cal_result
        with open('asuFiles/af_cal_data.csv', 'a+', newline='') as file:
            times = datetime.datetime.now(tz=None)
            date_time = times.strftime("%Y-%m-%d %H:%M:%S").strip()
            result.insert(0, sn)
            result.insert(0, date_time)
            writer = csv.writer(file)
            writer.writerow(result)

        self.win.pv += 100
        self.win.ui.snEdit.setText('')
        # HuiYuanRotate.hy_control(self.ser, 0, 0)
        self.win.start_mtf_test_activity()
        res = os.popen('adb shell getprop persist.sys.tof.offset.compensate')
        print(res)
        self.win.ui.calResultEdit.append(res)
        # os.system('adb shell settings put global tv_image_auto_keystone_asu 0')
        self.auto_cal_callback.emit('af_cal_finished')  # 任务线程发射信号,图像数据作为参数传递给主线程
        cal_end = time.time()
        self.win.ui.calResultEdit.append('对焦标定耗时{}秒'.format(str(round(cal_end - cal_start, 1))))

    def init(self):
        # self.win.ui.autoFocusLabel.setText('安装标定APK')
        # os.system('adb install -r app-debug.apk')
        os.system("adb shell mkdir /sdcard/DCIM/projectionFiles")
        # os.system("adb push AsuFocusPara.json /sdcard/DCIM/projectionFiles/AsuProjectorPara.json")
        # ProjectorDev.pro_kst_cal_service()
        # ProjectorDev.pro_tof_cal()
        self.win.ui.autoFocusLabel.setText('启动标定服务')

    def read_para(self):
        self.win.ui.autoFocusLabel.setText('保存位置数据')
        ProjectorDev.pro_save_pos_data(6, 11, "0a15a15a0")
        time.sleep(2.9)
        self.win.ui.autoFocusLabel.setText('开始分析数据')
        self.win.pull_data()

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        file_pro_path = dir_pro_path + "AsuProData.json"
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
        # location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
        # if location != '':
        #     location = location[9:-1]
        location = ProjectorDev.pro_get_motor_position()
        self.dis_steps[1] = int(location)
        para = 'TOF: ' + str(self.dis_steps[0]) + '  马达: ' + str(self.dis_steps[1])
        self.win.ui.autoFocusLabel.setText(para)
        print(
            'TOF:' + str(self.dis_steps[0]) + ',马达位置:' + str(self.dis_steps[1]) + ',马达location:' + str(location))
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
