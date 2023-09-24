import datetime
import os

import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal  # 缩放
from PyQt5.QtWidgets import QMessageBox
from matplotlib import pyplot as plt

import Fmc4030
import ProjectorDev
import gxipy as gx
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
import time
from Fmc4030 import init
from math_utils import CRC


# import matplotlib.pyplot as plt

# 多线程类
class ExCamAfThread(QThread):  # 建立一个任务线程类
    camera_arrive_signal = pyqtSignal(QPixmap)  # 设置触发信号传递的参数数据类型,传递信号必须事先定义好数据类型

    def __init__(self, ser=None, win=None):
        super(ExCamAfThread, self).__init__()
        self.ser = ser
        self.win = win
        self.mRunning = True
        self.mRailPosition = -100
        self.mLaplace = 0
        self.mLaplaceList = []
        self.mLaplaceList2 = []
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
            self.mLaplaceList2.append(self.win.cameraThread.mLaplace2)
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
        direction = 2
        self.clear()
        a = 6.47681438841663e-07
        b = -0.00449064062802631
        c = 11.0460386267558
        d = -7278.83032890080
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))
        # distance = 1026 + self.mRailPosition
        distance = 1626
        steps = a * (distance ** 3) + b * (distance ** 2) + c * distance + d
        steps = int(steps)
        print('投影仪位置:', distance, '马达初始化位置:', steps)
        motor_init_pos = ProjectorDev.pro_motor_reset_steps(steps)
        print('移动马达到初始位置, motor_init_pos', motor_init_pos)
        while True:
            location = ProjectorDev.pro_get_motor_position()
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
                print('已找到最清晰的马达位置:', absolute_position, max(self.mLaplaceList))
                ProjectorDev.pro_motor_reset_steps(absolute_position)
                print("退出对焦自动标定线程,最清晰的马达位置:", absolute_position, ',清晰度:', max(self.mLaplaceList))
                self.mRunning = True
                return

            wait_time = float(self.win.ui.exTimeSpinBox.text())/1000/1000*2
            time.sleep(wait_time)
            ProjectorDev.pro_motor_forward(direction, step_size)
            time.sleep(wait_time)
            print('延时等待完成,', wait_time)
            # plt.plot(self.mPositionList, self.mLaplaceList)
            # plt.show()

    # 控制马达找到最清晰的点,细搜
    def work2_detailed_search(self):
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
        distance = 1026 + self.mRailPosition
        steps = a * (distance ** 3) + b * (distance ** 2) + c * distance + d
        steps = int(steps)-150
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

    def work_test(self):
        rail_speed = 200  # mm/s
        if not os.path.exists('asuFiles/interRefFiles'):
            os.mkdir('asuFiles/interRefFiles')
        self.clear()
        position = 0
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        # print('导轨位置:', self.mRailPosition, '导轨移动初始位置:', position, abs(position - self.mRailPosition))
        self.motor_reset_steps(1700)
        time.sleep(1)
        while True:
            self.mRailPosition = Fmc4030.rail_position(self.ser)
            self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))

            location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
            location = location[9:-1]
            self.win.ui.posValueLabel.setText(location)

            # 保存数据
            print('保存数据')
            times = datetime.datetime.now(tz=None)
            file_path = 'asuFiles/interRefFiles' + '/' + str(position) + '_' + times.strftime("%Y-%m-%d %H:%M:%S").strip().replace(':', '_')
            self.win.cameraThread.takePicture(file_path)
            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mLaplaceList2.append(self.win.cameraThread.mLaplace2)
            self.mPositionList.append(self.mRailPosition)
            if not self.mRunning or position > 1900:
                print(self.mPositionList)
                print(self.mLaplaceList)
                absolute_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
                print("退出对焦自动标定线程,最清晰的导轨位置:", absolute_position, ',清晰度:', max(self.mLaplaceList))
                self.mRunning = True
                return
            time.sleep(3)
            # 上面延时是为了保证数据保存完成后，再移动导轨
            position += 200
            Fmc4030.rail_forward(self.ser, 0, position)
            time.sleep(200/rail_speed)
            print('导轨移动结束')

    def clear(self):
        self.mLaplaceList.clear()
        self.mPositionList.clear()
        print('清除队列:', len(self.mLaplaceList), len(self.mPositionList))
