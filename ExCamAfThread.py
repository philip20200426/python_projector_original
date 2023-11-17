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
        self.mExit = 0
        self.mRailPosition = -100
        self.mLaplace = 0
        self.mLaplaceList = []
        self.mLaplaceList2 = []
        self.mPositionList = []
        self.motor_position = 0
        self.result = []
        print('>>>>>>>>>> CamAfCalThread')

    def run(self):
        self.mRunning = True
        # self.work2()
        # self.work2_detailed_search()
        self.work2_detailed_search2()
        self.mRunning = False
        # self.work2()

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
        cur = time.time()
        wait_time0 = float(self.win.ui.exTimeSpinBox.text()) / 1000 / 1000 * 2
        print('>>>>>>>>>> 外置相机 work2 E:', cur)
        # motor_speed = 3.6 / 2589  # s/step
        motor_speed = 7.6 / 2589  # s/step
        step_size = 180
        direction = 2
        self.clear()
        a = 6.47681438841663e-07
        b = -0.00449064062802631
        c = 11.0460386267558
        d = -7278.83032890080
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))
        # distance = 1026 + self.mRailPosition
        # distance = 1626
        distance = 1500
        steps = a * (distance ** 3) + b * (distance ** 2) + c * distance + d
        steps = int(steps)
        print('投影仪位置:', distance, '马达初始化位置:', steps)
        motor_init_pos = ProjectorDev.pro_motor_reset_steps(steps)
        print('移动马达到初始位置, motor_init_pos', motor_init_pos)
        time.sleep(wait_time0*2)
        while True:
            location = ProjectorDev.pro_get_motor_position()
            self.win.ui.posValueLabel.setText(str(location))
            self.mLaplaceList.append(int(round(self.win.cameraThread.mLaplace, 2)*100))
            self.mPositionList.append(int(location))
            if len(self.mLaplaceList) > 1:
                gap = self.mLaplaceList[len(self.mLaplaceList) - 1] - self.mLaplaceList[len(self.mLaplaceList) - 2]
                if gap < 0:
                    if direction == 5:
                        direction = 2
                    elif direction == 2:
                        direction = 5
                    step_size = step_size * 0.618
                    print('>>>>>>>>>>>>>>>>>>>> 切换方向：', gap, self.mLaplaceList[len(self.mLaplaceList) - 1], self.mLaplaceList[len(self.mLaplaceList) - 2])

            if self.mExit or step_size < 30:
                print('马达位置:', self.mPositionList)
                print('清晰度值:', self.mLaplaceList)
                self.motor_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
                print('已找到最清晰的马达位置:', self.motor_position, max(self.mLaplaceList))
                ProjectorDev.pro_motor_reset_steps(self.motor_position)
                print("退出对焦自动标定线程,最清晰的马达位置:", self.motor_position, ',清晰度:', max(self.mLaplaceList))
                self.mExit = False
                lst = time.time()
                print('>>>>>>>>>> 外置相机 work2 耗时:', lst, (lst - cur))
                return
            time.sleep(2)
            ProjectorDev.pro_motor_forward(direction, step_size)
            # us -> s
            wait_time1 = motor_speed*step_size
            if wait_time1 < 0.6:
                wait_time1 = 0.6
            time.sleep(motor_speed*step_size)
            time.sleep(3)
            print('延时等待完成,', wait_time0+wait_time1)
            # 这里只要延时足够长，就能保证拿到的清晰度值是当前位置的
            # plt.plot(self.mPositionList, self.mLaplaceList)
            # plt.show()

    def work2_coarse_search(self):
        step_size = 360
        direction = 2
        self.clear()
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        self.win.ui.currentPositionLabel.setText(str(self.mRailPosition))

        while True:
            location = ProjectorDev.pro_get_motor_position()
            self.win.ui.posValueLabel.setText(str(location))
            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mPositionList.append(int(location))
            if len(self.mLaplaceList) > 1:
                gap = self.mLaplaceList[len(self.mLaplaceList) - 1] - self.mLaplaceList[len(self.mLaplaceList) - 2]
                if gap < 0:
                    if step_size < 90:
                        print('粗搜结束：', self.mPositionList)
                        break
                    if direction == 5:
                        direction = 2
                    elif direction == 2:
                        direction = 5
                    step_size = step_size / 2
            wait_time = float(self.win.ui.exTimeSpinBox.text()) / 1000 / 1000 * 2
            ProjectorDev.pro_motor_forward(direction, step_size)
            time.sleep(wait_time)
            print('延时等待完成,', wait_time)

    # 控制马达找到最清晰的点,细搜
    def work2_detailed_search(self):
        self.dis_to_steps()
        sta = time.time()
        ProjectorDev.pro_motor_forward(5, 180)
        direction = 2
        pos = [[90, 90, 90, 90], [60, 60, 60, 60, 60], [90, 60, 60]]
        for i in range(len(pos)):
            for j in range(len(pos[i])):
                location = ProjectorDev.pro_get_motor_position()
                self.win.ui.posValueLabel.setText(str(location))
                self.mLaplaceList.append(self.win.cameraThread.mLaplace)
                self.mPositionList.append(int(location))

                wait_time = float(self.win.ui.exTimeSpinBox.text()) / 1000 / 1000 * 2
                time.sleep(wait_time*2)
                ProjectorDev.pro_motor_forward(direction, pos[i][j])
                time.sleep(wait_time*3)
            if direction == 2:
                direction = 5
            elif direction == 5:
                direction = 2
        if len(self.mPositionList) > 5:
            self.motor_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
            print('耗时：', time.time() - sta)
            self.mRunning = False
            ProjectorDev.pro_motor_reset_steps(self.motor_position)
            print('已找到最清晰的马达位置:', self.motor_position, max(self.mLaplaceList))
            print(self.mLaplaceList, self.mPositionList)
            print('耗时：', time.time() - sta)

    def work2_detailed_search2(self):
        ProjectorDev.pro_show_pattern_af()
        ProjectorDev.pro_show_pattern(1)
        sta = time.time()
        # 先粗搜
        self.mPositionList.clear()
        self.mLaplaceList.clear()
        print(self.mPositionList, self.mLaplaceList)
        pri_steps = self.dis_to_steps()
        # 再细搜
        steps = 50
        steps_range = 200
        count = steps_range / steps * 2
        print('后退%d步' % steps_range)
        motor_speed = 7.6 / 2589  # s/step
        # ProjectorDev.pro_motor_forward(5, steps_range-150)
        direction = 2
        time.sleep(200 * motor_speed)
        print('后退%d步完成' % steps_range)

        while count > 0:
            if self.mExit:
                self.mExit = False
                return
            location = ProjectorDev.pro_get_motor_position()
            self.win.ui.posValueLabel.setText(str(location))
            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mPositionList.append(int(location))
            print('>>>>>>>>>> mLaplace', self.win.cameraThread.mLaplace)

            exp_time = float(self.win.ui.exTimeSpinBox.text()) / 1000 / 1000 * 2
            # time.sleep(exp_time * 2)
            ProjectorDev.pro_motor_forward(direction, steps)
            time.sleep(exp_time * 2)
            time.sleep(motor_speed * 50 * 2)
            time.sleep(1.6)
            count -= 1
        if len(self.mPositionList) > (count - 1):
            self.motor_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
            print('耗时：', time.time() - sta)
            ProjectorDev.pro_motor_reset_steps(self.motor_position)
            for i in range(len(self.mPositionList)):
                print(str(self.mPositionList[i]) + ':' + str(self.mLaplaceList[i]))
            print('已找到最清晰的马达位置:', self.motor_position, max(self.mLaplaceList))
            print('耗时：', time.time() - sta)

        self.result.append(self.mLaplaceList.copy())
        for i in range(len(self.result)):
            print(self.result[i])

    def work2_detailed_search3(self):
        ProjectorDev.pro_show_pattern_af()
        ProjectorDev.pro_show_pattern(1)
        sta = time.time()
        # 先粗搜
        self.mPositionList.clear()
        self.mLaplaceList.clear()
        print(self.mPositionList, self.mLaplaceList)
        pri_steps = self.dis_to_steps()
        # 再细搜
        steps = 50
        steps_range = 200
        count = steps_range/steps*2
        print('后退%d步' % steps_range)
        motor_speed = 7.6 / 2589  # s/step
        # ProjectorDev.pro_motor_forward(5, steps_range-150)
        direction = 2
        time.sleep(200*motor_speed)
        print('后退%d步完成' % steps_range)

        while count > 0:
            if self.mExit:
                self.mExit = False
                return
            location = ProjectorDev.pro_get_motor_position()
            self.win.ui.posValueLabel.setText(str(location))
            self.mLaplaceList.append(self.win.cameraThread.mLaplace)
            self.mPositionList.append(int(location))
            print('>>>>>>>>>> mLaplace', self.win.cameraThread.mLaplace)

            exp_time = float(self.win.ui.exTimeSpinBox.text()) / 1000 / 1000 * 2
            # time.sleep(exp_time * 2)
            #ProjectorDev.pro_motor_forward(direction, steps)

            ProjectorDev.pro_motor_reset_steps(pri_steps + steps)
            time.sleep(exp_time * 2)
            time.sleep(motor_speed * 50 * 2)
            time.sleep(1.6)
            count -= 1
            steps = steps + 50
        if len(self.mPositionList) > (count-1):
            self.motor_position = self.mPositionList[self.mLaplaceList.index(max(self.mLaplaceList))]
            print('耗时：', time.time() - sta)
            ProjectorDev.pro_motor_reset_steps(self.motor_position)
            for i in range(len(self.mPositionList)):
                print(str(self.mPositionList[i]) + ':' + str(self.mLaplaceList[i]))
            print('已找到最清晰的马达位置:', self.motor_position, max(self.mLaplaceList))
            print('耗时：', time.time() - sta)

        self.result.append(self.mLaplaceList.copy())
        for i in range(len(self.result)):
            print(self.result[i])

    def dis_to_steps(self):
        motor_speed = 7.6 / 2589  # s/step
        # a = 6.47681438841663e-07
        # b = -0.00449064062802631
        # c = 11.0460386267558
        # d = -7278.83032890080
        a = 4.0721e-07
        b = -0.00302
        c = 7.9745
        d = -5345.0431
        distance = 1626
        #distance = 1769
        steps = a * (distance ** 3) + b * (distance ** 2) + c * distance + d
        steps = int(steps)
        print('投影仪当前距离:', distance, '马达初始化位置:', steps)
        motor_init_pos = ProjectorDev.pro_motor_reset_steps(steps)
        print('移动马达到初始位置, motor_init_pos', motor_init_pos)
        time.sleep(motor_speed*steps)
        return steps

    def work_test(self):
        rail_speed = 200  # mm/s
        if not os.path.exists('asuFiles/interRefFiles'):
            os.mkdir('asuFiles/interRefFiles')
        self.clear()
        position = 0
        self.mRailPosition = Fmc4030.rail_position(self.ser)
        # print('导轨位置:', self.mRailPosition, '导轨移动初始位置:', position, abs(position - self.mRailPosition))
        ProjectorDev.pro_motor_reset_steps(1700)
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
            file_path = 'asuFiles/interRefFiles' + '/' + str(position) + '_' + times.strftime(
                "%Y-%m-%d %H:%M:%S").strip().replace(':', '_')
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
            time.sleep(200 / rail_speed)
            print('导轨移动结束')

    def clear(self):
        self.mLaplaceList.clear()
        self.mPositionList.clear()
        print('清除队列:', len(self.mLaplaceList), len(self.mPositionList))

    def get_result(self):
        print('1111111111111111111111>', self.mRunning)
        while self.mRunning:
            pass
        print('0000000000000000000000>', self.motor_position, self.mRunning)
        return self.motor_position
