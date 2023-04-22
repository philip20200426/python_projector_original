from PyQt5.QtCore import Qt, QThread, pyqtSignal  # 缩放
from PyQt5.QtWidgets import QMessageBox

import gxipy as gx
from PyQt5.QtGui import QImage, QPixmap
import cv2
from PIL import Image


# 多线程类
class CameraThread(QThread):  # 建立一个任务线程类
    camera_arrive_signal = pyqtSignal(QPixmap)  # 设置触发信号传递的参数数据类型,传递信号必须事先定义好数据类型

    def __init__(self, threadID, threadName, exposureTime=6000.0):
        super(CameraThread, self).__init__()
        self.threadID = threadID
        self.name = threadName
        self.exposureTime = exposureTime
        self.value = 0
        self.cam = None
        self.mTakePicture = False
        self.mImageName = 'ref_cam'
        self.frameNum = 0
        self.mRunning = False

    def openCamera(self):
        pass

    def closeCamera(self):
        self.mRunning = False

    def setPictureName(self, name):
        self.mImageName = name

    def takePicture(self, name='temp'):
        self.mImageName = name
        self.mTakePicture = True

    def run(self):  # 在启动线程后任务从这个函数里面开始执行
        print("Open Camera")
        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num == 0:
            print("Number of enumerated devices is 0")
            return
        # open the first device
        self.cam = device_manager.open_device_by_index(1)
        # exit when the camera is a color camera
        if self.cam.PixelColorFilter.is_implemented() is True:
            print("This sample does not support color camera.")
            self.cam.close_device()
            return
        # set continuous acquisition
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        #self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)
        # set gain
        self.cam.Gain.set(10.0)
        # start data acquisition
        self.cam.stream_on()
        self.frameNum = 0
        while True:
            # time.sleep(1)
            # img_green = np.zeros([400, 600], np.uint8)
            # self.value = self.exposureTime
            # img_green[:] = self.value
            # q_img = QImage(img_green.data, img_green.shape[1], img_green.shape[0], QImage.Format_Grayscale8)
            # set exposure
            if not self.mRunning:
                print("Close Camera")
                self.cam.stream_off()
                self.cam.close_device()
                return
            self.frameNum += 1
            self.cam.ExposureTime.set(self.exposureTime)
            # get raw image
            raw_image = self.cam.data_stream[0].get_image()
            if raw_image is None:
                print("Get raw image failed.")
                continue
            # create numpy array with data from raw image
            numpy_image = raw_image.get_numpy_array()
            if numpy_image is None:
                print("numpy_image is None.")
                continue
            if self.mTakePicture:
                self.mTakePicture = False
                # show acquired image
                img = Image.fromarray(numpy_image, 'L')
                img.save(self.mImageName + '.bmp')
                print("TakePicture Frame ID: %d   Height: %d   Width: %d"
                    % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

            q_img = QImage(numpy_image.data, numpy_image.shape[1], numpy_image.shape[0], QImage.Format_Grayscale8)
            pix = QPixmap(q_img).scaled(720, 540)
            self.camera_arrive_signal.emit(pix)  # 任务线程发射信号,图像数据作为参数传递给主线程

