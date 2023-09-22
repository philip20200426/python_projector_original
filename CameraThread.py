import cv2
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal  # 缩放
from PyQt5.QtWidgets import QMessageBox

import MTF_measure3
import gxipy as gx
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
import time

from pro_correct_wrapper import auto_focus_cam


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
        self.mLaplace = 0
        self.mLaplace2 = 0
        self.mEnLaplace = True

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
        # self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)
        # set gain
        # self.cam.Gain.set(10.0)
        # start data acquisition
        self.cam.stream_on()
        self.frameNum = 0
        self.mRunning = True
        print("Camera Init Finished")
        last_time = time.time()
        la_list = []
        while True:
            # print('Preview FPS ', now_time - last_time)
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
            numpy_image_preview = raw_image.get_numpy_array()
            numpy_image_picture = numpy_image_preview.copy()

            if self.mEnLaplace:
                # 2048, 2448
                orig_img = Image.fromarray(numpy_image_preview)
                crop_img = orig_img.crop((600, 600, 1900, 1460))
                # crop_img.save('asuFiles/interRefFiles/crop123.bmp')
                numpy_image_preview = np.array(crop_img)
                # print('++++++++++++++++++++++++++++++', numpy_image_preview.shape)
                img, la = MTF_measure3.mtf_measure(numpy_image_preview)
                if len(la) > 2:
                    self.mLaplace = la[2]
                # print('==================================>>> ', self.mLaplace)
                now_time = time.time()
                # 单位ms
                str_time = str(round(int((now_time - last_time) * 1000), 2))
                last_time = now_time
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(numpy_image_preview, str_time, (500, 800), font, 3, (255, 255, 255), 8)
                # 计算拉普拉斯值
                # orig_img = Image.fromarray(numpy_image)
                # # crop_img = orig_img.crop((510, 280, 940, 820))
                # # 非梯形相机,1.6m,右转15
                # crop_img = orig_img.crop((690, 820, 1700, 1360))
                # o_h, o_w = crop_img.size
                # crop_img.save('asuFiles/interRefFiles/crop.bmp')
                # #print(type(numpy_image), type(crop_img), o_h, o_w)
                # size = numpy_image.shape
                # # print('Image size: ', size[0], size[1])
                # # dis = numpy_image.shape
                #
                # #laplacian = cv2.Laplacian(np.array(crop_img), cv2.CV_64F).var()
                # laplacian = cv2.Laplacian(numpy_image, cv2.CV_64F).var()
                # self.mLaplace = round(laplacian, 2)

                # la_list.append(laplacian)
                # sum_la = 0
                # for i in range(len(la_list)):
                #     sum_la += la_list[i]
                # if len(la_list) > 3:
                #     la_list.pop(0)
                # # print(la_list, len(la_list))
                # self.mLaplace = round(sum_la / (len(la_list)+1), 2)
                # now_time = time.time()
                # view = str(round(int((now_time - last_time) * 1000), 2)) + ' Laplace:' + str(self.mLaplace)
                # # 在图片添加文字，参数为，图片，绘制文字，位置，字体类型，字体大小，颜色，线条类型
                # font = cv2.FONT_HERSHEY_SIMPLEX
                # img = cv2.putText(numpy_image, view, (500, 100), font, 3, (255, 255, 255), 8)
                # # img = cv2.putText(numpy_image, view, (200, 200), font, 3, (255, 255, 255), 8)
                # last_time = now_time

            if numpy_image_preview is None:
                print("numpy_image is None.")
                continue
            if self.mTakePicture:
                self.mLaplace2 = auto_focus_cam(numpy_image_picture)
                self.mTakePicture = False
                # show acquired image
                img = Image.fromarray(numpy_image_picture, 'L')
                img.save(self.mImageName + '.bmp')

                print("TakePicture Frame ID: %d   Height: %d   Width: %d "
                      % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
                print(self.mImageName + '.bmp')

            q_img = QImage(numpy_image_preview.data, numpy_image_preview.shape[1], numpy_image_preview.shape[0], QImage.Format_Grayscale8)
            pix = QPixmap(q_img).scaled(720, 540)
            # pix = QPixmap(q_img).scaled(430, 540)
            self.camera_arrive_signal.emit(pix)  # 任务线程发射信号,图像数据作为参数传递给主线程
