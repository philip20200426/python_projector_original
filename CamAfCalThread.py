import os

import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal  # 缩放
from PyQt5.QtWidgets import QMessageBox

import Fmc4030
import gxipy as gx
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
import time
from Fmc4030 import init
from math_utils import CRC


# import matplotlib.pyplot as plt

# 多线程类
class CamAfCalThread(QThread):  # 建立一个任务线程类
    camera_arrive_signal = pyqtSignal(QPixmap)  # 设置触发信号传递的参数数据类型,传递信号必须事先定义好数据类型

    def __init__(self, ser=None, win=None):
        super(CamAfCalThread, self).__init__()
        self.ser = ser
        self.win = win
        self.mRunning = True
        self.mRailPosition = -100
        self.mLaplace = 0
        self.mLaplaceList = []
        self.mPositionList = []
        print('>>>>>>>>>> CamAfCalThread')

    def run(self):
        self.work2()

    def work1(self):
        relative_position = 36
        rail_speed = 200  # mm/s
        direction = 0
        self.clear()
        a = 1.07762125153429e-07
        b = -0.000151494881929664
        c = 0.358375201288244
        d = 1009.02094861660

        self.mRailPosition = Fmc4030.rail_position(self.ser)

        motor_pos = int(self.win.ui.motorPosPositionEdit.text())
        position = a * (motor_pos ** 3) + b * (motor_pos ** 2) + c * motor_pos + d
        position = position - 900
        print('导轨位置:', self.mRailPosition, '导轨移动初始位置:', position, abs(position - self.mRailPosition))

        Fmc4030.rail_forward_pos(self.ser, position)
        sleep = abs(position - self.mRailPosition) / rail_speed + 0.5

        print('延时:', sleep)
        time.sleep(sleep)
        print('延时完成:', sleep)

        while True:
            self.mRailPosition = Fmc4030.rail_position(self.ser)
            self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))

            location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
            location = location[9:-1]
            self.win.ui.posValueLabel.setText(location)

            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mPositionList.append(self.mRailPosition)
            if len(self.mLaplaceList) > 1:
                gap = self.mLaplaceList[len(self.mLaplaceList) - 1] - self.mLaplaceList[len(self.mLaplaceList) - 2]
                if gap < 0:
                    if direction == 0:
                        direction = 1
                    elif direction == 1:
                        direction = 0
                    relative_position = relative_position * 0.618
                # print('>>>>>>>>>>>>>>>>>>>> 切换方向：', gap, direction, relative_position)

            if not self.mRunning or relative_position < 3:
                print(self.mPositionList)
                print(self.mLaplaceList)
                absolute_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
                Fmc4030.rail_forward_pos(self.ser, absolute_position)
                print("退出对焦自动标定线程,最清晰的导轨位置:", absolute_position, ',清晰度:', max(self.mLaplaceList))
                self.mRunning = True
                return

            Fmc4030.rail_forward(self.ser, direction, relative_position)
            wait_time = relative_position / rail_speed
            if wait_time < 3:
                wait_time = 3
            print('延时等待：', wait_time)
            time.sleep(wait_time)
            print('延时等待完成,', wait_time)

            # plt.plot(self.mPositionList, self.mLaplaceList)
            # plt.show()

    # 控制马达找到最清晰的点
    def work2(self):
        step_size = 160
        motor_speed = 3.6/2589  # s/step
        direction = 2
        self.clear()
        a = 6.47681438841663e-07
        b = -0.00449064062802631
        c = 11.0460386267558
        d = -7278.83032890080
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))
        distance = 901 + self.mRailPosition
        steps = a * (distance ** 3) + b * (distance ** 2) + c * distance + d
        steps = int(steps)
        print('投影仪位置:', distance, '马达初始化位置:', steps)
        motor_init_pos = self.motor_reset_steps(steps)
        print('移动马达到初始位置, motor_init_pos', motor_init_pos)
        while True:
            location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
            location = int(location[9:-1])
            self.win.ui.posValueLabel.setText(str(location))
            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mPositionList.append(int(location))
            if len(self.mLaplaceList) > 1:
                gap = self.mLaplaceList[len(self.mLaplaceList) - 1] - self.mLaplaceList[len(self.mLaplaceList) - 2]
                if gap < 0:
                    if direction == 5:
                        direction = 2
                    elif direction == 2:
                        direction = 5
                    step_size = step_size * 0.618
                # print('>>>>>>>>>>>>>>>>>>>> 切换方向：', gap, direction, step_size)

            if not self.mRunning or step_size < 30:
                print('马达位置:', self.mPositionList)
                print('清晰度值:', self.mLaplaceList)
                absolute_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
                # dif = absolute_position - location
                # if dif > 0:
                #     self.motor_forward(5, abs(dif))
                # elif dif < 0:
                #     self.motor_forward(2, abs(dif))
                print('已找到最清晰的马达位置:', absolute_position, max(self.mLaplaceList))
                self.motor_reset_steps(absolute_position)
                print("退出对焦自动标定线程,最清晰的马达位置:", absolute_position, ',清晰度:', max(self.mLaplaceList))
                self.mRunning = True
                return

            self.motor_forward(direction, step_size)
            # wait_time = step_size / motor_speed
            # if wait_time < 0.5:
            #     wait_time = 0.5
            # print('延时等待：', wait_time)
            wait_time = int(self.win.ui.exTimeSpinBox.text())/1000/1000*8
            time.sleep(wait_time)
            print('延时等待完成,', wait_time)
            # plt.plot(self.mPositionList, self.mLaplaceList)
            # plt.show()

    def clear(self):
        self.mLaplaceList.clear()
        self.mPositionList.clear()
        print('清除队列:', len(self.mLaplaceList), len(self.mPositionList))

    def motor_forward(self, direction, steps):
        # inputCmd = 'adb shell "echo 5 $hello > /sys/devices/platform/customer-AFmotor/step_set"'
        # execute_adb_command(inputCmd, 0)
        # subprocess.Popen('adb shell "echo 5 2000 > /sys/devices/platform/customer-AFmotor/step_set"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cmd1 = "adb shell "
        # cmd2 = '"echo 5 '
        # cmd3 = self.ui.motorPositionEdit.text()
        # cmd4 = '> /sys/devices/platform/customer-AFmotor/step_set"'
        # cmd = cmd1 + cmd2 + cmd3 + cmd4
        # print(cmd)
        # os.system(cmd)
        # 5 2
        location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
        location = int(location[9:-1])

        cmd1 = 'adb shell am broadcast -a asu.intent.action.Motor --es operate '
        cmd2 = str(direction)
        cmd3 = ' --ei value '
        cmd4 = str(int(steps))
        # mylog.logger.debug("-" + cmd2)
        cmd = cmd1 + cmd2 + cmd3 + cmd4
        print(cmd)
        os.system(cmd)
        start = time.time()
        while True:
            cur = time.time()
            if abs(cur - start) > 6:
                print('马达执行步数，超时处理', steps)
                return -1
            new_location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
            new_location = int(new_location[9:-1])
            if abs(abs(new_location - location) - steps) < 5:
                print(steps, location, new_location)
                print('马达执行' + str(steps) + '步')
                time.sleep(0.2)
                return steps

    def motor_reset_steps(self, steps):
        count = 0
        location = 0
        motor_pos = 0
        while count < 3:
            self.win.motorReset()
            start = time.time()
            while True:
                cur = time.time()
                if abs(cur - start) > 6:
                    print('马达复位超时')
                    count += 1
                    break
                location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
                location = location[9:-1]
                if (abs(int(location) - 0)) < 3:
                    print('马达复位完成', location)
                    count = 3
                    break
        time.sleep(0.3)
        motor_pos = self.motor_forward(2, steps)
        if abs(motor_pos - steps) < 5:
            print('马达运行到位置:', motor_pos, steps)
        else:
            print('马达运行到位置:' + str(motor_pos) + '时,发生错误')
        return motor_pos
    # def run(self):  # 在启动线程后任务从这个函数里面开始执行
    #     print('>>>>>>>>>> CAM 自动对焦标定')
    #     print("Open Camera")
    #     # create a device manager
    #     device_manager = gx.DeviceManager()
    #     dev_num, dev_info_list = device_manager.update_device_list()
    #     if dev_num == 0:
    #         print("Number of enumerated devices is 0")
    #         return
    #     # open the first device
    #     self.cam = device_manager.open_device_by_index(1)
    #     # exit when the camera is a color camera
    #     if self.cam.PixelColorFilter.is_implemented() is True:
    #         print("This sample does not support color camera.")
    #         self.cam.close_device()
    #         return
    #     # set continuous acquisition
    #     self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
    #     # self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)
    #     # set gain
    #     # self.cam.Gain.set(10.0)
    #     # start data acquisition
    #     self.cam.stream_on()
    #     self.frameNum = 0
    #     self.mRunning = True
    #     print("Camera Init Finished")
    #     last_time = time.time()
    #
    #     la_list = []
    #     while True:
    #         now_time = time.time()
    #         # Fmc4030.rail_forward(self.ser, 0, 10)
    #         self.mRailPosition = Fmc4030.rail_position(self.ser)
    #         print(self.mRailPosition)
    #         # if self.mRailPosition > 1000:
    #         #     print('导轨运行结束')
    #         #     break
    #         # time.sleep(0.02)
    #         #print('Preview FPS ', now_time - last_time)
    #         # time.sleep(1)
    #         # img_green = np.zeros([400, 600], np.uint8)
    #         # self.value = self.exposureTime
    #         # img_green[:] = self.value
    #         # q_img = QImage(img_green.data, img_green.shape[1], img_green.shape[0], QImage.Format_Grayscale8)
    #         # set exposure
    #         if not self.mRunning:
    #             print("Close Camera")
    #             self.cam.stream_off()
    #             self.cam.close_device()
    #             return
    #         self.frameNum += 1
    #         # 曝光时间单位:us
    #         #self.cam.ExposureTime.set(self.exposureTime)
    #         # get raw image
    #         raw_image = self.cam.data_stream[0].get_image()
    #         if raw_image is None:
    #             print("Get raw image failed.")
    #             continue
    #         # 将 RGB 数据转换为 numpy 对象
    #         # create numpy array with data from raw image
    #         numpy_image = raw_image.get_numpy_array()
    #         orig_img = Image.fromarray(numpy_image)
    #         o_h, o_w = orig_img.size
    #         print(o_h, o_w)
    #         size = numpy_image.shape
    #         # print('Image size: ', size[0], size[1])
    #         # dis = numpy_image.shape
    #         laplacian = cv2.Laplacian(numpy_image, cv2.CV_64F).var()
    #         la_list.append(laplacian)
    #         sum_la = 0
    #         for i in range(len(la_list)):
    #             sum_la += la_list[i]
    #         if len(la_list) > 5:
    #             la_list.pop(0)
    #         print(la_list)
    #         self.mLaplace = round(sum_la/len(la_list), 2)
    #         view = str(round(int((now_time - last_time)*1000), 2)) + ' Laplace:' + str(self.mLaplace)
    #         # 在图片添加文字，参数为，图片，绘制文字，位置，字体类型，字体大小，颜色，线条类型
    #         font = cv2.FONT_HERSHEY_SIMPLEX
    #         cv2.putText(numpy_image, view, (800, 100), font, 3, (255, 255, 255), 8)
    #         last_time = now_time
    #
    #         if numpy_image is None:
    #             print("numpy_image is None.")
    #             continue
    #         if self.mTakePicture:
    #             self.mTakePicture = False
    #             # show acquired image
    #             img = Image.fromarray(numpy_image, 'L')
    #             img.save(self.mImageName + '.bmp')
    #             print("TakePicture Frame ID: %d   Height: %d   Width: %d "
    #                   % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
    #             print(self.mImageName + '.bmp')
    #
    #         q_img = QImage(numpy_image.data, numpy_image.shape[1], numpy_image.shape[0], QImage.Format_Grayscale8)
    #         pix = QPixmap(q_img).scaled(720, 540)
    #         self.camera_arrive_signal.emit(pix)  # 任务线程发射信号,图像数据作为参数传递给主线程
