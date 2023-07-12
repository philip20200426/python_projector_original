# -*- coding: utf-8 -*-

import gxipy as gx
from PIL import Image
import PyQt5

import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal  # 多线程
from PyQt5.QtCore import Qt  # 缩放

dev_num = 0


class CameraHelper(QThread):  # 建立一个任务线程类
    signal = pyqtSignal(QImage)  # 设置触发信号传递的参数数据类型,传递信号必须事先定义好数据类型

    def __init__(self):
        # 按钮事件信号槽
        # self.Open.clicked.connect(self.OpenCamera)
        # 采集线程
        self.OpenCamera()
        global dev_num
        if dev_num is not 0:
            self.camThread = CameraThread()  # 实例化自己建立的任务线程类
            self.camThread.signal.connect(self.image_callback)  # 设置任务线程发射信号触发的函数
            self.camThread.start()

    def OpenCamera(self):
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num is 0:
            print("Number of enumerated devices is 0")
            return

        # open the first device
        self.cam = device_manager.open_device_by_index(1)

        # exit when the camera is a color camera
        if self.PixelColorFilter.is_implemented() is True:
            print("This sample does not support color camera.")
            self.cam.close_device()
            return

        # set continuous acquisition
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

        # set exposure
        self.cam.ExposureTime.set(2000)

        # set gain
        # self.cam.Gain.set(10.0)

        # start data acquisition
        self.cam.stream_on()

    # def OpenCamera(self):
    #     global camera
    #
    #     cameraInfo = Refresh()  # 刷新并获取相机列表
    #     camera = Camera(int(0))  # 以索引号的方式打开相机
    #     camera.Start()  # 启动视频流
    #
    #     self.mythread.start()  # 启动任务线程
    #     return None

    # =======================多线程回调
    def image_callback(self, image):  # 这里的image就是任务线程传回的图像数据,类型必须是已经定义好的数据类型
        self.label.setPixmap(QPixmap.fromImage(image))
        return None


# 多线程类
class CameraThread(QThread):  # 建立一个任务线程类
    signal = pyqtSignal(QImage)  # 设置触发信号传递的参数数据类型,传递信号必须事先定义好数据类型

    def __init__(self):
        super(CameraThread, self).__init__()

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        global camera
        while self.cam.isOpen:
            # acquire image: num is the image number
            num = 1
            for i in range(num):
                # get raw image
                raw_image = self.cam.data_stream[0].get_image()
                if raw_image is None:
                    print("Getting image failed.")
                    continue
                # create numpy array with data from raw image
                numpy_image = raw_image.get_numpy_array()
                if numpy_image is None:
                    continue
                # show acquired image
                img = Image.fromarray(numpy_image, 'L')
                # img.show()
                # print height, width, and frame ID of the acquisition image
                print("Frame ID: %d   Height: %d   Width: %d"
                      % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
            mat = QImage(img, img.iWidth, img.iHeight, QImage.Format_Indexed8)  # 转为QImage类型
            mat = mat.scaled(mat.width() * 0.5, mat.height() * 0.5, Qt.IgnoreAspectRatio,
                             Qt.SmoothTransformation)  # 缩放图像，SmoothTransformation平滑缩放，FastTransformation快速缩放
            self.signal.emit(QImage(mat))  # 任务线程发射信号,图像数据作为参数传递给主线程
        # stop data acquisition
        self.cam.stream_off()
        # close device
        self.cam.close_device()
#
# def takePicture(exposure_time):
#     # 创建窗口
#     cv2.namedWindow('video', cv2.WINDOW_NORMAL)
#     cv2.resizeWindow('video', 640, 480)  # 设置窗口大小
#     # 获取视频设备
#     cap = cv2.VideoCapture(1)
#     # 从摄像头读视频帧
#     ret, frame = cap.read()
#     cap.set(cv2.CAP_PROP_EXPOSURE, exposure_time)
#     cap.set(cv2.CAP_PROP_GAIN, 10)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 6)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 6)
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
#     print("width: ", width, "height: ", height, "fps: ", fps, "exposure: ", exposure)
#     # 将视频帧在窗口中显示
#     cv2.imwrite("external_camera.bmp", frame)  # 用来保存图片
#     cv2.imshow('video', frame)
#     # 释放资源
#     cap.release()  # 释放视频资源
#     cv2.destroyAllWindows()  # 释放窗口资源
#
# def preview():
# # 创建窗口
# cv2.namedWindow('video', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('video', 640, 480)  # 设置窗口大小
#
# # 获取视频设备
# cap = cv2.VideoCapture(1)
#
# while True:
#     # 从摄像头读视频帧
#     # cdll.LoadLibrary('G:\python_test\learn_serial\pro_correction.dll')
#     # CDLL('G:\python_test\learn_serial\pro_correction.dll', winmode=0)
#
#     # if platform.system().lower() == 'windows':
#     #     #cdll.LoadLibrary('pro_correction.dll')
#     #     CDLL('G:/python_test/learn_serial/pro_correction.dll', winmode=0)
#     # else:
#     #     cdll.LoadLibrary('./platform/libpercipio_cam.so')
#     ret, frame = cap.read()
#     cap.set(cv2.CAP_PROP_EXPOSURE, 1000)
#     cap.set(cv2.CAP_PROP_GAIN, 10)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 6)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 6)
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
#     print("width: ", width, "height: ", height, "fps: ", fps, "exposure: ", exposure)
#     # 将视频帧在窗口中显示
#     print("frame: ", frame)
#     cv2.imshow('video', frame)
#     key = cv2.waitKey(1)  # 不能为0，0为等待中断，只能读取到一帧的数据
#     if (key & 0xFF == ord('q')):
#         cv2.imwrite("example.bmp", frame)  # 用来保存图片
#         break
#
# # 释放资源
# cap.release()  # 释放视频资源
# cv2.destroyAllWindows()  # 释放窗口资源
