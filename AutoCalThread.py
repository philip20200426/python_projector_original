import csv
import datetime
import json
import os
import time
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import time

from PyQt5.QtGui import QPixmap
from matplotlib import pyplot as plt
import datetime
import Constants
import HuiYuanRotate
import ProjectorDev
import evaluate_correct_wrapper
import globalVar
from Constants import KST_EVAL_ANGLE
from pro_correct_wrapper import set_point, get_point, auto_keystone_calib, DIR_NAME_PRO, auto_keystone_calib2, \
    create_dir_file
from math_utils import CRC
from utils.logUtil import print_debug


class AutoCalThread(QThread):
    auto_cal_callback = pyqtSignal(str)

    def __init__(self, ser=None, win=None):
        super().__init__()
        self.ser = ser
        self.win = win
        self.mAfCal = False
        self.position = 0
        self.num = 1
        # 转台完成动作后，稳定时间
        self.delay1 = 1.6
        # 发出保存数据后，等待时间
        self.delay2 = 2
        # 外部相机保存时间
        self.delay3 = 1.6
        self.enableAlgo = True
        self.mExit = False
        self.mRunning = False
        self.CRC = CRC()
        print_debug('>>>>>>>>>>>>>>>>>>> Init AutoCalThread', self.mExit, self.mRunning)
        self.positionList = [1, 2, 3, 4, 5, 6, 7, 8]
        self.estimateAngelList = [[-15, -15], [15, -15]]
        self.position_list_bk = [1, 2, 3, 4, 5, 6, 7, 8]
        # self.angle_list = [[0, 0], [0, 7], [-7, 0], [7, 0], [0, -7], [-7, -7], [7, -7], [7, 7]]
        self.angle_list = [[0, 0], [15, 0], [15, 10], [0, 10], [-15, 10], [-15, 0], [-15, -12], [0, -12], [15, -12]]
        self.pos_init_finished = False
        self.pos_count = len(self.positionList)
        self.mode = 0

    def run(self, mode=0):
        print_debug('>>>>>>>>>>>>>>>>>> AutoCalThread Run, mode:', mode)
        if self.mode == 0:
            self.work0()
        elif self.mode == 1:
            self.estimate_test()

    def parse_projector_data(self):
        # self.parse_projector_json()
        pos_error = [0] * len(self.positionList)
        startTime = time.time()

        # parse data
        pro_img_list = []
        pro_file_list = []
        ret = {"jpg": 0, "png": 0, "bmp": 0, "txt": 0}
        print_debug("解析目录：", globalVar.get_value('DIR_NAME_PRO'))
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
        print_debug(pro_img_list)
        print_debug(pro_file_list)

        tof_list = []
        imu_list = []
        img_list = []
        txt_list = []
        for i in range(max(len(pro_img_list), len(pro_file_list))):
            name = "pro_n" + str(i)
            # print_debug('============================= ', name)
            # print_debug('++++++++++++++++++++++++++ ', "".join(list(filter(str.isdigit, name))))
            # print_debug(int("".join(list(filter(str.isdigit, name)))))
            # print_debug(len(self.positionList)-1)
            if int("".join(list(filter(str.isdigit, name)))) > (len(self.positionList) - 1):
                print_debug('！！！！！！只解析指定位置范围以内的数据：', int("".join(list(filter(str.isdigit, name)))),
                      len(self.positionList) - 1)
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
                            tof_data = line.split(',')
                            tof_list += line.split(',')
                            print_debug('TOF 数据；', tof_list)
                            tof_data = list(map(float, tof_data))[0:-2]
                            print_debug('TOF 数据；', i, tof_data, max(tof_data), min(tof_data))
                            if max(tof_data) > 1900 or min(tof_data) < 1300:
                                print_debug('!!!!!!!!!!!!!!!!!!!! TOF数据异常：', max(tof_data), min(tof_list), i)
                                pos_error[i] = -1
                        else:
                            pos_error[i] = -1
                    if row == 2:
                        if len(line.split(',')) == 5:
                            imu_data = line.split(',')
                            imu_data = list(map(float, imu_data))
                            imu_list += line.split(',')
                            gap = abs(abs(imu_data[3]) - abs(self.angle_list[i][1]))
                            if gap > 5:
                                print_debug('!!!!!!!!!!!!!!!!!!!! IMU数据与转台角度差异超过限值：', imu_data[3],
                                      self.angle_list[i][1], gap)
                                pos_error[i] = -1
                        else:
                            pos_error[i] = -1
                    row += 1
                file.close()  # 关闭文件
            else:
                pos_error[i] = -1

            # if os.path.exists(img_name):
            #     imageSize = os.path.getsize(img_name)
            #     if imageSize == 2764854:
            #         img_list.append(img_name)
            #     else:
            #         print_debug('图片尺寸不对')
            #         pos_error[i] = -1
            # else:
            #     pos_error[i] = -1
        tof_list = list(map(float, tof_list))
        imu_list = list(map(float, imu_list))
        # imu_list = [-0.35637358, -0.058934387, -9.621797, -2.1211205, -0.35069707, -1.5607239, -0.06814104, -9.396643, -9.430139, -0.40986606, 0.16314575, -0.041536115, -9.477646, 0.98616785, -0.25106198, 0.17572004, -0.053791054, -9.482669, 1.0615896, -0.32495475, 1.8895739, -0.028401155, -9.26852,11.52293, -0.17202999, 1.5429159, -0.027392864, -9.337974, 9.382189, -0.16582781, -1.2138578, -0.06935661, -9.435228, -7.330732, -0.41772044, 0.15215015, 1.6623696, -9.330419, 0.9197521, 10.100882]
        # print_debug(len(tof_list), tof_list)
        # print_debug(len(imu_list), imu_list)
        # print_debug(len(img_list), img_list)
        # print_debug(pos_error)
        endTime = time.time()
        # 秒
        print_debug('解析投影文件耗时', endTime - startTime)
        return pos_error, tof_list, imu_list, img_list

    def parse_projector_json(self):
        print_debug('开始解析Json数据, 一共有%d位置' % self.pos_count)
        pos_error = [0] * self.pos_count

        dir_pro_path = globalVar.get_value('DIR_NAME_PRO')
        dir_ref_path = globalVar.get_value('DIR_NAME_REF')

        tof_list = []
        tof_central = []
        imu_list = []
        ref_img_list = []
        pitch_ref = 0

        # 分析json数据
        file_pro_path = dir_pro_path + "AsuProData.json"
        if os.path.isfile(file_pro_path):
            file_size = os.path.getsize(file_pro_path)
            if file_size < 1000:
                print_debug('文件异常，文件大小不对：', file_size, file_pro_path)
                for i in range(self.pos_count):
                    pos_error[i] = -1
                return pos_error, tof_list, imu_list, ref_img_list
            file = open(file_pro_path, )
            dic = json.load(file)
            print_debug('解析文件：', file_pro_path)
            if len(dic) > 0:
                if 'TOF' in dic.keys():
                    if 'central' in dic['TOF'].keys():
                        # print_debug('>>>>>>>>>>>>>>>', dic['TOF']['central'])
                        tof_central = list(map(float, list(map(float, dic['TOF']['central'].split(',')))))
                for i in range(self.pos_count):
                    pos = 'POS' + str(i)
                    print_debug('POS:', pos)
                    if pos in dic.keys():
                        if 'tof' in dic[pos].keys():
                            if dic[pos]['tof'] != '':
                                data = list(map(float, dic[pos]['tof'].split(',')))
                                # print_debug('TOF数据：', data, i, max(data), min(data))
                                if len(data) == 4:
                                    if max(data) < Constants.TOF_MAX_THR and min(data) > Constants.TOF_MIN_THR:
                                        # print(self.angle_list[i][0], self.angle_list[i][1])
                                        if i == 0 and ((data[0] - data[1]) > 15):
                                            pos_error[i] = -1
                                        # elif (i == 1 or i == 2 or i == 8) and data[1] > data[2]:
                                        elif (self.angle_list[i][0] > 5) and data[1] > data[2]:
                                            print_debug(data)
                                            pos_error[i] = -1
                                        # elif (i == 4 or i == 5 or i == 6) and data[1] < data[2]:
                                        elif (self.angle_list[i][0] < -5) and data[1] < data[2]:
                                            pos_error[i] = -1
                                        tof_list += data
                                        tof_list += tof_central
                                    else:
                                        pos_error[i] = -1
                                else:
                                    pos_error[i] = -1
                                    print_debug('Json中TOF数据为空！！！')
                            else:
                                pos_error[i] = -1
                            if pos_error[i] == -1 and len(data) > 0:
                                print_debug('!!!!!!!!!!!!!!!!!!!! TOF数据异常:', data)
                        else:
                            pos_error[i] = -1
                            print_debug('json文件中，没有发现TOF数据')
                        if 'imu' in dic[pos].keys():
                            data = list(map(float, dic[pos]['imu'].split(',')))
                            if i == 0:
                                pitch_ref = data[3]
                            if len(data) == 5:
                                gap = abs(abs(data[3] - pitch_ref) - abs(self.angle_list[i][1]))
                                print_debug('!!!!!!!!!!!!!!!!!!!!>>>>>>>>', gap)
                                # gap = abs(abs(data[3]) - abs(self.angle_list[i][1]))
                                # print_debug(data, gap)
                                if gap > Constants.IMU_GAP:
                                    print_debug('!!!!!!!!!!!!!!!!!!!! IMU数据异常：', data[3],
                                          self.angle_list[i][1], gap)
                                    pos_error[i] = -1
                                imu_list += data
                            else:
                                pos_error[i] = -1
                        else:
                            pos_error[i] = -1
                    else:
                        print_debug('Json文件中未找到位置信息')
                        pos_error[i] = -1
            file.close()
        else:
            print_debug('%s文件不存在：' % file_pro_path)
            for i in range(self.pos_count):
                pos_error[i] = -1
            return pos_error, tof_list, imu_list, ref_img_list

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
                        print_debug('外部相机尺寸: ', ref_img_size[0], ' 列Col:', ref_img_size[1])
                        ref_list.append(file)
                        ret["bmp"] = ret["bmp"] + 1
                        # print_debug(ref_list)
            for i in range(self.pos_count):
                img = 'ref_n' + str(i) + '.bmp'
                if img in ref_list:
                    ref_img_list.append(dir_ref_path + img)
                else:
                    pos_error[i] = -1

            if self.pos_count != ret["bmp"]:
                print_debug('!!!!!!!!!!图片数量不对')

        return pos_error, tof_list, imu_list, ref_img_list

    def evaluate_kst_correct(self):
        if not self.win.cameraThread.mRunning:
            self.win.open_external_camera()
            time.sleep(1)
        img = self.win.cameraThread.get_img()
        dst = [0] * 12
        # img_size = (img.shape[0], img.shape[1])
        img_size = img.shape
        print_debug('Load EvaluateCorrectionRst:', img_size, dst)
        rst = evaluate_correct_wrapper.evaluate_correction_rst(img_size, img, dst)
        print_debug('返回参数:', dst)
        return dst

    def estimate_test(self):
        # 解析json中配置的云台角度
        print_debug('全向梯形标定评估...')
        est_lst_time = time.time()
        if os.path.isfile('res/para.json'):
            file = open('res/para.json', )
            dic = json.load(file)
            if len(dic) > 0 and 'angle0' in dic.keys():
                ang = dic['angle0']
                n = 2
                self.estimateAngelList = [ang[i * n:(i + 1) * n] for i in range((len(ang) + n - 1) // n)]
                # print_debug('使用json中的角度：', self.estimateAngelList)
            else:
                print_debug('json配置文件中未匹配到云台角度参数,使用默认角度配置')
            file.close()
        else:
            print_debug('未找到json文件,使用默认角度配置')

        result0 = []
        result1 = []
        result2 = []
        print_debug('云台角度配置参数：', self.estimateAngelList, len(self.estimateAngelList))
        self.auto_cal_callback.emit('全向梯形标定结果评估中...')
        print_debug('++++++++++++++++++++++++++++++++++')
        # self.win.pv += Constants.CAL_PROGRESS_STEP
        ProjectorDev.pro_show_pattern(2)

        edge_res = []
        angle_res = []
        angle_res2 = []
        edge_result = False
        angle_result = False
        kst_result = False
        for i in range(len(self.estimateAngelList)):
            count = 0
            print_debug(
                '>>>>>>>>>>>>>>>>>>>>> 控制转台到%d %d' % (self.estimateAngelList[i][0], self.estimateAngelList[i][1]))
            HuiYuanRotate.hy_control(self.ser, self.estimateAngelList[i][0],
                                     self.estimateAngelList[i][1])
            time.sleep(4.6)
            while count < Constants.KST_EST_RETRY_COUNT:
                result0 = []
                result1 = []
                ProjectorDev.pro_auto_af_kst_cal(2)
                time.sleep(1.8)
                dst = self.evaluate_kst_correct()
                print_debug(dst)
                result0.append(round(dst[0] * 100, 1))
                result0.append(round(dst[1] * 100, 1))
                for j in range(2, 6):
                    result1.append(round(dst[j], 1))
                print('测试记过：', result0, result1)

                count += 1
                edge_result = False
                angle_result = False
                kst_result = False
                if max(result0) <= Constants.KST_EVAL_EDGE:
                    edge_result = True
                result2 = [round(abs(x - 90), 1) for x in result1]
                if max(result2) <= Constants.KST_EVAL_ANGLE:
                    angle_result = True
                if edge_result and angle_result:
                    kst_result = True

                # 浮点List转化成字符串列表
                temp0 = [str(i) for i in result0]
                temp0 = ' '.join(temp0)
                temp1 = [str(i) for i in result2]
                temp1 = '  '.join(temp1)
                temp = str(kst_result) + ' ' + str(edge_result) + ' ' + str(angle_result) + ' ' + temp0 + " ; " + temp1
                self.win.ui.calResultEdit.append(temp)

                if kst_result:
                    break
            edge_res += result0
            angle_res += result2
            angle_res2 += result1
        print('全向梯形标定结束：', edge_res, angle_res, angle_res2)
        if self.win.auto_cal_flag:
            if max(edge_res) <= Constants.KST_EVAL_EDGE:
                edge_result = True
            if max(angle_res) <= Constants.KST_EVAL_ANGLE:
                angle_result = True
            if edge_result and angle_result:
                kst_result = True
            # 保存数据
            result = edge_res + angle_res + angle_res2
            sn = globalVar.get_value('SN')
            times = datetime.datetime.now(tz=None)
            file_name = 'result/kst/' + times.strftime("%Y-%m-%d").strip().replace(':', '_') + '.csv'
            if not os.path.exists(file_name):
                items_list = ['时间', 'SN', '结果', '畸变', '角度', '边差', '边差', '边差', '边差', '角度', '角度', '角度', '角度', '角度', '角度', '角度', '角度']
                with open(file_name, mode='a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(items_list)
                    csvfile.close()
            with open(file_name, 'a+', newline='') as file:
                times = datetime.datetime.now(tz=None)
                date_time = times.strftime("%Y-%m-%d %H:%M:%S").strip()
                result.insert(0, angle_result)
                result.insert(0, edge_result)
                result.insert(0, kst_result)
                result.insert(0, sn)
                result.insert(0, date_time)
                writer = csv.writer(file)
                writer.writerow(result)
            self.auto_cal_callback.emit('kst_est_finished')
        est_cur_time = time.time()
        self.auto_cal_callback.emit('梯形评估耗时{}秒'.format(round(est_cur_time-est_lst_time, 1)))
    def work0(self):
        # From kst_auto_calibrate
        print_debug('>>>>>>>>>> work0 识别设备...')
        cal_start = time.time()
        if self.win.root_device():
            self.auto_cal_callback.emit('find dev error')
            self.win.ui.calResultEdit.append('未找到投影设备！！！')
            return
        create_dir_file()
        ProjectorDev.pro_clear_data()
        ProjectorDev.pro_close_ai_feature()
        os.system('adb shell mkdir /sdcard/DCIM/projectionFiles')
        os.system('adb push AsuKstPara.json /sdcard/DCIM/projectionFiles/AsuProPara.json')

        ProjectorDev.pro_motor_reset_steps(Constants.DEV_LOCATION_STEPS)
        self.win.ui.calResultEdit.append('全向梯形标定开始...')
        self.mRunning = True
        # 解析json中配置的云台角度
        if os.path.isfile('res/para.json'):
            file = open('res/para.json', )
            dic = json.load(file)
            if len(dic) > 0 and 'angle' in dic.keys():
                ang = dic['angle']
                n = 2
                self.angle_list = [ang[i * n:(i + 1) * n] for i in range((len(ang) + n - 1) // n)]
                print_debug('使用json中的角度：', self.angle_list)
            else:
                print_debug('json配置文件中未匹配到云台角度参数,使用默认角度配置')
            file.close()
        else:
            print_debug('未找到json文件,使用默认角度配置')
        print_debug('云台角度配置参数：', self.angle_list, len(self.angle_list))

        self.pos_count = len(self.positionList)
        # self.position_list_bk = self.positionList
        os.system('adb shell am broadcast -a asu.intent.action.KstReset')
        ProjectorDev.pro_set_kst_point([0, 0, 1920, 0, 1920, 1080, 0, 1080])
        ProjectorDev.pro_show_pattern(2)
        time.sleep(2.6)
        start_time = time.time()
        print_debug('>>>>>>>>>>', len(self.positionList), self.positionList)
        if self.position == 0 and self.positionList[self.position] == 1 and len(self.positionList) > 5:
            # 直接到第一个位置，只有第一次在第一個位置時運行
            HuiYuanRotate.hy_control(self.ser, 0, 0)
            self.win.set_exposure_time()
            # 只有自动标定会走到这里
            # os.system('adb install -rd app-debug.apk')
            # print_debug('启动投影仪校准服务')
            # os.system("adb shell am stopservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
            # time.sleep(1)
            # ProjectorDev.pro_kst_cal_service()
            # time.sleep(1.9)
            # print_debug('0点位置准备：投影显示复位，TOF校准')
            # # 投影启动MikeySever时，会自动加载TOF校准参数，这里不再做TOF校准
            # os.system('adb shell am broadcast -a asu.intent.action.TofCal')
            # ProjectorDev.pro_tof_cal()
            # time.sleep(1.6)
            if abs(ProjectorDev.pro_get_motor_position() - Constants.DEV_LOCATION_STEPS) > 100:
                print_debug('马达位置不对，重新对焦！！！！！！')
                ProjectorDev.pro_motor_reset_steps(Constants.DEV_LOCATION_STEPS)
            # self.pos_init_finished = True
        lst_time = time.time()
        while len(self.positionList) > 0:
            # 超时处理
            now_time = time.time()
            if self.mExit or (now_time - lst_time) > 366:
                # os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
                self.position = 0
                ProjectorDev.pro_show_pattern(0)
                print_debug('>>>>>>>>>>>>>>>>>>> 紧急退出自动标定线程 或者 运行时间超时:', now_time - lst_time, self.mExit)
                break
            if self.position >= len(self.positionList):
                time.sleep(1.6)  # 2
                print_debug('>>>>>>>>>>>>>>>>>>> 开始解析数据')
                self.win.pull_data()
                # time.sleep(3)
                # proj_data = self.parse_projector_data()
                proj_data = self.parse_projector_json()
                print_debug('解析Json结果，各位置状态：', proj_data[0])
                # 这里的逻辑是把通过的位置设置成0，再删除掉。
                cmd = self.win.ui.kstAutoCalCountEdit.text().strip()
                self.position_list_bk = list(map(int, cmd.split(',')))
                for pos in range(self.pos_count):
                    if proj_data[0][pos] != -1:
                        self.position_list_bk[pos] = 0
                self.position_list_bk = list(set(self.position_list_bk))

                self.positionList = self.position_list_bk.copy()
                if 0 in self.positionList:
                    self.positionList.remove(0)
                # self.win.pv -= len(self.positionList) * 10
                print_debug('>>>>>>>>>>>>>>>>>>> %d个姿态有错误, ' % len(self.positionList))
                print_debug(">>>>>>>>>>>>>>>>>>> ", self.positionList)

                self.position = 0
                if len(self.positionList) == 0:
                    # self.win.pv += Constants.CAL_PROGRESS_STEP
                    # ProjectorDev.pro_show_pattern(0)
                    end0_time = time.time()
                    self.auto_cal_callback.emit('kst_cal_data_ready')  # 任务线程发射信号,图像数据作为参数传递给主线程
                    self.auto_cal_callback.emit('抓取数据耗时{}秒'.format(str(round(end0_time - cal_start, 1))))
                    print_debug('数据抓取及解析耗时：' + str((end0_time - start_time)))
                    print_debug(proj_data)
                    if self.enableAlgo:
                        self.auto_cal_callback.emit('算法处理中...')
                        if auto_keystone_calib2(proj_data) == 0:
                            end1_ime = time.time()
                            print_debug('算法运行耗时：' + str((end1_ime - end0_time)))
                            cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
                            os.system(cmd)
                            os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
                            # self.win.pv += Constants.CAL_PROGRESS_STEP
                            print_debug('>>>>>>>>>>>>>>>>>>> 全向标定完成，总耗时：', str(end1_ime - start_time))
                            ProjectorDev.switch_algo_vendor(0)
                            # ProjectorDev.pro_restore_ai_feature()
                            # os.system('adb reboot')
                            self.win.ui.calResultEdit.append('标定算法处理完成')
                            self.auto_cal_callback.emit('kst_cal_finished')  # 任务线程发射信号,图像数据作为参数传递给主线程
                        else:
                            self.mExit = True
                            self.win.ui.calResultEdit.append('标定算法返回错误！！！')
                            print_debug('>>>>>>>>>>>>>>>>>>> 算法返回ERROR,全向标定失败')
                    else:
                        print_debug('未使能算法')
                    break
            print_debug('>>>>>>>>>>>>>>>>>>>>> 控制转台到第%d个姿态 %d' % (self.positionList[self.position], self.position))
            self.win.ui.calResultEdit.append('控制转台到第{}个姿态'.format(self.positionList[self.position]))
            HuiYuanRotate.hy_control(self.ser, self.angle_list[int(self.positionList[self.position]) - 1][0],
                                     self.angle_list[int(self.positionList[self.position]) - 1][1])
            time.sleep(self.delay1)
            print_debug('>>>>>>>>>>>>>>>>>>>>> 开始保存第%d个姿态的数据 ' % self.positionList[self.position])
            # cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
            # cmd1 = str(self.positionList[self.position] - 1)
            # os.system(cmd0 + cmd1)
            ProjectorDev.pro_save_pos_data(6, str(self.positionList[self.position] - 1))

            time.sleep(self.delay2)
            self.win.cal = True
            self.win.external_take_picture(self.positionList[self.position] - 1)
            # dir_ref_path = globalVar.get_value('DIR_NAME_REF')
            # file_path = dir_ref_path + 'ref_n' + str(self.positionList[self.position] - 1) + '.bmp'
            # self.win.hk_win.save_cal_bmp(file_path)
            time.sleep(self.delay3)
            self.win.cal = False

            print_debug('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (
                len(self.positionList), self.positionList[self.position]))
            self.position += 1
            # self.win.pv += Constants.CAL_PROGRESS_STEP

        # 标定结束，转台归位
        # self.win.pv = 100
        # HuiYuanRotate.hy_control(self.ser, 0, 0)
        self.win.ui.kstCalButton.setEnabled(True)

        self.mExit = False
        self.mRunning = False
        cal_end = time.time()
        self.win.ui.calResultEdit.append('梯形标定耗时{}秒'.format(str(round(cal_end - cal_start, 1))))

    #
    # def work1(self):
    #     print_debug('自动全向梯形标定 开始：', self.positionList)
    #     # print_debug(self.parse_projector_json())
    #     # return
    #     self.win.showCheckerPattern()
    #     start_time = time.time()
    #     if self.position == 0 and self.positionList[self.position] == 1 and len(self.positionList) > 5:
    #         # 直接到第一个位置，只有第一次在第一個位置時運行
    #         cmdList = ['01', '06', '04', '87', '00', '01']
    #         cmdChar = ' '.join(cmdList)
    #         crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
    #         cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
    #         cmdHex = bytes.fromhex(cmdChar)
    #         if self.ser is not None:
    #             self.ser.write(cmdHex)
    #         else:
    #             print_debug('>>>>>>>>>>>>>>>>>>>> 串口异常')
    #         time.sleep(2.6)
    #         # os.system('adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')
    #         # time.sleep(2)
    #         # 只有自动标定会走到这里
    #         # os.system('adb install -r app-debug.apk')
    #         print_debug('启动投影仪校准服务')
    #         os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
    #         # os.system("adb shell am stopservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
    #         # time.sleep(1)
    #         ProjectorDev.pro_kst_cal_service()
    #         time.sleep(2.9)
    #         os.system('adb shell am broadcast -a asu.intent.action.KstReset')
    #         os.system('adb shell am broadcast -a asu.intent.action.TofCal')
    #         # self.win.showWritePattern()
    #         time.sleep(1.9)
    #         self.win.showCheckerPattern()
    #         self.pos_init_finished = True
    #     while len(self.positionList) > 0:
    #         if self.mExit:
    #             os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
    #             self.position = 0
    #             print_debug('>>>>>>>>>>>>>>>>>>> 紧急退出自动标定线程')
    #             break
    #         if self.enableAlgo:
    #             if len(self.positionList) == 1 and self.positionList[0] == -1:
    #                 self.position = 1
    #                 print_debug('>>>>>>>>>>>>>>>>>>> 跳过数据采集，直接运行算法')
    #         else:
    #             print_debug(' >>>>>>>>>>>>>>>>>>> 算法未使能')
    #         if self.position >= len(self.positionList):
    #             time.sleep(1.5)  # 2
    #             print_debug('>>>>>>>>>>>>>>>>>>> 开始解析数据')
    #             proj_data = self.parse_projector_data()
    #             print_debug(proj_data[0])
    #             for pos in range(len(self.positionList)):
    #                 if proj_data[0][pos] != -1:
    #                     self.positionList[pos] = 0
    #             print_debug(self.positionList)
    #             self.positionList = list(set(self.positionList))
    #             print_debug(self.positionList)
    #             if 0 in self.positionList:
    #                 self.positionList.remove(0)
    #             self.win.pv -= len(self.positionList) * 10
    #             print_debug('>>>>>>>>>>>>>>>>>>> %d个姿态有错误, ' % len(self.positionList))
    #             print_debug(">>>>>>>>>>>>>>>>>>> ", self.positionList)
    #             self.position = 0
    #             if len(self.positionList) == 0:
    #                 self.win.pv += 5
    #                 os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
    #                 end0_time = time.time()
    #                 print_debug('数据抓取及解析耗时：' + str((end0_time - start_time)))
    #                 print_debug(proj_data)
    #                 if self.enableAlgo:
    #                     if auto_keystone_calib2(proj_data):
    #                         end1_ime = time.time()
    #                         print_debug('算法运行耗时：' + str((end1_ime - end0_time)))
    #                         cmd = 'adb push ' + globalVar.get_value('CALIB_DATA_PATH') + ' /sdcard/kst_cal_data.yml'
    #                         os.system(cmd)
    #                         # os.system("adb shell rm -rf sdcard/DCIM/projectionFiles/* ")
    #                         # self.win.clean_data()
    #                         os.system("adb shell am broadcast -a asu.intent.action.KstCalFinished")
    #                         self.win.pv += 5
    #                         print_debug('>>>>>>>>>>>>>>>>>>> 全向标定完成，总耗时：', str(end1_ime - start_time))
    #                         self.win.restore_ai_feature()
    #                         # os.system("adb shell am stopservice com.nbd.tofmodule/com.nbd.autofocus.TofService")
    #                         # set_point(point)
    #                     else:
    #                         print_debug('>>>>>>>>>>>>>>>>>>> 全向标定失败')
    #                 else:
    #                     print_debug('未使能算法')
    #                 break
    #         print_debug('>>>>>>>>>>>>>>>>>>>>> 控制转台到第%d个姿态 %d' % (self.positionList[self.position], self.position))
    #         cmdList = ['01', '06', '04', '87', '00', '0A']
    #         cmdList[5] = '{:02X}'.format(self.positionList[self.position])
    #         cmdChar = ' '.join(cmdList)
    #         crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
    #         cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
    #         # print_debug(cmdChar)
    #         cmdHex = bytes.fromhex(cmdChar)
    #         if self.ser is not None:
    #             self.ser.write(cmdHex)
    #         else:
    #             print_debug('>>>>>>>>>>>>>>>>>>>> 串口异常')
    #
    #         time.sleep(self.delay1)
    #
    #         print_debug('>>>>>>>>>>>>>>>>>>>>> 开始保存第%d个姿态的数据 ' % self.positionList[self.position])
    #         cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
    #         cmd1 = str(self.positionList[self.position] - 1)
    #         os.system(cmd0 + cmd1)
    #         time.sleep(self.delay2)
    #         self.win.cal = True
    #         self.win.external_take_picture(self.positionList[self.position] - 1)
    #         time.sleep(self.delay3)
    #         self.win.cal = False
    #         print_debug('>>>>>>>>>>>>>>>>>>>>> 一共%d个姿态, 已完成第%d个, ' % (
    #             len(self.positionList), self.positionList[self.position]))
    #         self.position += 1
    #         self.win.pv += 10
    #     # 标定结束，转台归位
    #     self.win.pv = 100
    #     cmdList = ['01', '06', '04', '87', '00', '01']
    #     cmdChar = ' '.join(cmdList)
    #     crc, crc_H, crc_L = self.CRC.CRC16(cmdChar)
    #     cmdChar = cmdChar + ' ' + crc_L + ' ' + crc_H
    #     cmdHex = bytes.fromhex(cmdChar)
    #     if self.ser is not None:
    #         print_debug('云台回到第一个位置')
    #         self.ser.write(cmdHex)
    #     else:
    #         print_debug('>>>>>>>>>>>>>>>>>>>> 串口异常')
    #
    #     # if not self.mExit:
    #     #     os.system('adb reboot')
    #     self.win.ui.kstCalButton.setEnabled(True)
    #     self.mExit = False
