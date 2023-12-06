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
from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2, \
    create_dir_file
from math_utils import CRC
from utils.logUtil import print_debug


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
        print_debug('>>>>>>>>>>>>>>>>>>> Init AutoFocusCalThread')
        self.positionList = [1, 2, 3, 4, 5, 6]
        self.pos_init_finished = False
        self.dis_steps = [-1, -1]

    # From auto_focus_cal
    def work0(self):
        pass
    def run(self):
        cal_start = time.time()
        if not self.win.auto_cal_flag:
            if self.win.root_device():
                self.auto_cal_callback.emit('find dev error')
                self.win.ui.calResultEdit.append('未找到投影设备！！！')
                return
        self.win.start_mtf_test_activity()
        ProjectorDev.pro_close_ai_feature()
        create_dir_file()
        self.win.cameraThread.mEnLaplace = True

        os.system("adb shell mkdir /sdcard/DCIM/projectionFiles")
        self.win.set_exposure_time()
        print_debug('开始对焦自动化标定,云台延时：{} 标定补偿：{}'.format(Constants.ROTATE_DELAY, Constants.DEV_AF_CAL_STEPS_OFFSET))
        # ProjectorDev.pro_show_pattern_af()
        # os.system('adb shell am broadcast -a asu.intent.action.TofCal')
        # self..win.ui.autoFocusLabel.setText('启动TOF校准')
        # time.sleep(1)

        self.win.ui.calResultEdit.append('对焦标定开始...')

        # 控制转台右转15度
        self.win.pv += Constants.CAL_PROGRESS_STEP
        HuiYuanRotate.hy_control(self.ser, 15, 0)
        time.sleep(Constants.ROTATE_DELAY)
        # 触发全向和自动对焦
        self.win.ui.calResultEdit.append('右15°对焦标定')
        if ProjectorDev.pro_auto_af_kst_cal(2):
            self.win.ui.calResultEdit.append('投影自动对焦失败，直接退出！！！')
            return
        time.sleep(2.9)
        dis_steps_r = self.read_para()
        print_debug('投影设备右投对焦后马达位置：', dis_steps_r[1])
        right_steps = dis_steps_r[1]
        # right_steps = ProjectorDev.pro_get_motor_position()
        self.win.ex_cam_af()
        time.sleep(0.3)
        right_ex_steps = self.win.ex_cam_af_thread.get_result()
        right_gap = right_ex_steps - right_steps
        self.dis_steps[1] = right_ex_steps - Constants.DEV_AF_CAL_STEPS_OFFSET

        # self.win.ui.calResultEdit.append('正投自动对焦')
        # # 控制转台到0度
        # self.win.pv += Constants.CAL_PROGRESS_STEP
        # # ProjectorDev.motor_reset()
        # # 梯形标定完成后，默认就是正投状态，不需要再控制云台
        # HuiYuanRotate.hy_control(self.ser, 0, 0)
        # time.sleep(Constants.ROTATE_DELAY)
        # ProjectorDev.pro_auto_af_kst_cal(1)
        # time.sleep(2.9)
        # dis_steps_c = self.read_para()
        # print_debug(self.dis_steps, dis_steps_c)
        # print_debug('投影设备正投对焦后马达位置：', dis_steps_c[1])
        # center_steps = dis_steps_c[1]
        # target_steps = center_steps + right_gap
        # self.dis_steps[1] = target_steps
        ################################################################################## 以上标定结束

        if self.dis_steps[0] > Constants.DIS_STEPS_1 and self.dis_steps[1] > Constants.DIS_STEPS_1:
            self.win.auto_focus_motor()
            self.win.write_to_nv()
            self.win.ui.calResultEdit.append('对焦标定完成')

            # 对焦标定评估
            self.win.ui.calResultEdit.append('正投对焦标定评估')
            self.win.pv += Constants.CAL_PROGRESS_STEP
            HuiYuanRotate.hy_control(self.ser, 0, 0)
            time.sleep(Constants.ROTATE_DELAY)
            ProjectorDev.pro_auto_af_kst_cal(2)
            time.sleep(0.6)
            right_steps_cal = ProjectorDev.pro_get_motor_position()
            # 基于外部CAM对焦，返回当前马达位置
            self.win.ex_cam_af()
            time.sleep(0.3)
            right_ex_steps_cal = self.win.ex_cam_af_thread.get_result()
            right_gap_cal = right_ex_steps_cal - right_steps_cal - Constants.DEV_AF_CAL_STEPS_OFFSET
            print_debug('右15度标定结果：', right_ex_steps_cal, right_steps_cal, right_gap_cal)

            self.win.ui.calResultEdit.append('左15°对焦标定评估')
            self.win.pv += Constants.CAL_PROGRESS_STEP
            HuiYuanRotate.hy_control(self.ser, -15, 0)
            time.sleep(Constants.ROTATE_DELAY)
            if ProjectorDev.pro_auto_af_kst_cal(2):
                self.win.ui.calResultEdit.append('投影自动对焦失败，直接退出！！！')
                return
            time.sleep(0.6)
            left_steps_cal = ProjectorDev.pro_get_motor_position()
            self.win.ex_cam_af()
            time.sleep(0.3)
            left_ex_steps_cal = self.win.ex_cam_af_thread.get_result()
            left_ex_steps_cal = left_ex_steps_cal
            left_gap_cal = left_ex_steps_cal - left_steps_cal - Constants.DEV_AF_CAL_STEPS_OFFSET
            print_debug('左15度标定结果：', left_ex_steps_cal, left_steps_cal, left_gap_cal)

            af_result = False
            if abs(left_gap_cal) < Constants.AF_CAL_EVAL and abs(right_gap_cal) < Constants.AF_CAL_EVAL:
                self.win.ui.calResultEdit.append('<font color="green" size="6">{}</font>'.format('对焦标定成功'))
                pix_white = QPixmap('res/pass.png')
                self.win.ui.calAfResultLabel.setPixmap(pix_white)
                af_result = True
            else:
                self.win.ui.calResultEdit.append('<font color="red" size="6">{}</font>'.format('对焦标定失败'))

            print_debug('对焦标定结果：', left_gap_cal, right_gap_cal)
        else:
            self.win.ui.calResultEdit.append('对焦标定失败，直接退出！！！')

        # 保存对焦标定数据
        af_cal_result = []
        af_cal_result.append(right_steps)
        af_cal_result.append(right_ex_steps)
        af_cal_result.append(right_gap)
        #af_cal_result.append(center_steps)
        af_cal_result.append(left_steps_cal)
        af_cal_result.append(left_ex_steps_cal)
        af_cal_result.append(left_gap_cal)
        af_cal_result.append(right_steps_cal)
        af_cal_result.append(right_ex_steps_cal)
        af_cal_result.append(right_gap_cal)
        af_cal_result.append(Constants.DEV_AF_CAL_STEPS_OFFSET)
        sn = globalVar.get_value('SN')
        result = self.dis_steps + af_cal_result

        times = datetime.datetime.now(tz=None)
        file_name = 'result/af/' + times.strftime("%Y-%m-%d").strip().replace(':', '_') + '.csv'
        if not os.path.exists(file_name):
            items_list = ['时间', 'SN', '结果', '补偿距离', '补偿步数', '正投对焦', '正投外对焦', '右差值', '左15对焦评估', '左15外对焦评估', '左差值', '右15对焦评估', '右15外对焦标评估', '右差值']
            with open(file_name, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(items_list)
                csvfile.close()
        with open(file_name, 'a+', newline='') as file:
            times = datetime.datetime.now(tz=None)
            date_time = times.strftime("%H:%M:%S").strip()
            result.insert(0, af_result)
            result.insert(0, sn)
            result.insert(0, date_time)
            writer = csv.writer(file)
            writer.writerow(result)
        print_debug(type(result), result)
        del result[0]
        del result[0]
        temp0 = [str(i) for i in result]
        temp0 = ' '.join(temp0)
        self.win.ui.calResultEdit.append(temp0)

        self.win.pv += 100
        os.system('adb shell getprop persist.sys.tof.offset.compensate')
        self.win.ui.snEdit.setFocus(True)
        #  self.win.ui.calResultEdit.append(res)
        # os.system('adb shell settings put global tv_image_auto_keystone_asu 0')
        self.auto_cal_callback.emit('af_cal_finished')  # 任务线程发射信号,图像数据作为参数传递给主线程
        cal_end = time.time()
        self.win.ui.calResultEdit.append('对焦标定耗时{}秒'.format(str(round(cal_end - cal_start, 1))))
        self.win.ui.snEdit.setText('')
        ProjectorDev.pro_show_pattern(0)
        ProjectorDev.pro_restore_ai_feature()
        HuiYuanRotate.hy_control(self.ser, 0, 0)

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
        ProjectorDev.pro_save_pos_data(6, 21, "0a15a15a0")
        time.sleep(2.9)
        self.win.ui.autoFocusLabel.setText('开始分析数据')
        self.win.pull_data()

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        file_pro_path = dir_pro_path + "AsuProData.json"
        if os.path.isfile(file_pro_path):
            file = open(file_pro_path, )
            dic = json.load(file)
            if len(dic) > 0 and 'POS21' in dic.keys() and 'tof' in dic['POS21'].keys():
                if dic['POS21']['tof'] != '':
                    # print_debug(dic['POS11']['tof'].split(',')[0])
                    self.dis_steps[0] = int(dic['POS21']['tof'].split(',')[0])
            if len(dic) > 0 and 'POS21' in dic.keys() and 'location' in dic['POS21'].keys():
                if dic['POS21']['location'] != '':
                    # print_debug(dic['POS11']['location'])
                    self.dis_steps[1] = dic['POS21']['location']
            file.close()
        location = ProjectorDev.pro_get_motor_position()
        self.dis_steps[1] = int(location)
        para = 'TOF: ' + str(self.dis_steps[0]) + '  马达: ' + str(self.dis_steps[1])
        self.win.ui.autoFocusLabel.setText(para)
        print_debug(
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
        print_debug("解析目录：", globalVar.get_value('DIR_NAME_PRO'))
        for root, dirs, files in os.walk(globalVar.get_value('DIR_NAME_PRO')):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:5]
                # print_debug(file, ext, head)
                if ext == '.bmp' and head == 'pro_n':
                    ret["bmp"] = ret["bmp"] + 1
                    pro_img_list.append(file)
                if ext == ".png" and head == 'pro_n':
                    ret["png"] = ret["png"] + 1
                if ext == ".txt" and head == 'pro_n':
                    pro_file_list.append(file)
                    ret["txt"] = ret["png"] + 1
        print_debug(pro_img_list)
        print_debug(pro_file_list)

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
                            print_debug('+++++++++++++++++', tof_list)
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
                    print_debug('图片尺寸不对')
                    pos_error[i] = -1
            else:
                pos_error[i] = -1
        tof_list = list(map(float, tof_list))
        imu_list = list(map(float, imu_list))
        # print_debug(len(tof_list), tof_list)
        # print_debug(len(imu_list), imu_list)
        # print_debug(len(img_list), img_list)
        # print_debug(pos_error)
        endTime = time.time()
        # 秒
        print_debug('解析投影文件耗时', endTime - startTime)
        return pos_error, tof_list, imu_list, img_list
