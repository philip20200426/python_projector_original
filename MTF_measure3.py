## this program is used to catch pattern and calculate the MTF
## by Dongfeng Lin

# 库
import os
import time

import cv2
import numpy as np
import matplotlib as mpl
from PIL import Image


IMG_MODE = 1

# 预定义
mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']
def img_contrast_bright(img,a,b,g):
    h,w,c=img.shape
    blank=np.zeros([h,w,c],img.dtype)
    dst=cv2.addWeighted(img,a,blank,b,g)
    return dst
def contrast_stretching(img,shift):
    min_val = np.min(img)
    max_val = np.max(img)
    out = ((img - min_val) / (max_val - min_val)) * 255
    out = out + shift
    out[out<0]=0
    out[out>255]=255
    return out.astype(np.uint8)

def mtf_measure(image):
    laplace_list = []
    if IMG_MODE == 0:
        # 读图
        #image0 = cv2.imread("asuFiles/interRefFiles/2023-09-21 12_45_50.bmp")
        # 图片预处理
        img_cp = image.copy()
        gray = image
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        shift = 200 - np.argmax(hist)

        img = contrast_stretching(image, shift)
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        ret, threshold = cv2.threshold(img, 250, 255, cv2.THRESH_TOZERO)
        kernel = np.ones((100, 100), np.uint8)
        erosion = cv2.dilate(threshold, kernel)
        #获得目标区域集合
        contours, hierarchy = cv2.findContours(erosion, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #每个目标的性质输出
        coordinate_list = [[], [], [], []]
        count = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt) #目标的坐标和长宽
            # image1 = image[y:y + h, x:x + w]
            image1 = img_cp[y:y + h, x:x + w]
            orig_img = Image.fromarray(image1)
            # orig_img.save('asuFiles/interRefFiles/crop.bmp')
            MTF = cv2.Laplacian(image1, cv2.CV_64F).var() #目标的清晰度值
            laplace_list.append(MTF)
            # print(x, y, w, h, MTF)
            #显示
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_size = 3
            font_color = (255, 255, 255)
            thickness = 6
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2) #画框
            cv2.putText(image, str(round(MTF*100)/100), (x, y), font, font_size, font_color, thickness) #显示数值
        return img, laplace_list
    elif IMG_MODE == 1:
        MTF = cv2.Laplacian(image, cv2.CV_64F).var()  # 目标的清晰度值
        laplace_list.append(MTF)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 3
        font_color = (255, 255, 255)
        thickness = 6
        #cv2.putText(image, str(round(MTF, 2)), (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 9, (255, 255, 255), 8)
        # 下面尺寸适用于汽车尾门，远焦镜头
        cv2.putText(image, str(round(MTF, 2)), (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255), 8)
        return image,laplace_list
        #print(MTF)
    # now_time = time.time()
    # fps = str(round(int((now_time - last_time) * 1000), 2))
    # cv2.putText(image, fps, (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)
    # last_time = now_time

    #画图
    # cv2.namedWindow("img", cv2.WINDOW_KEEPRATIO)
    # cv2.imshow("img", image0)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# image = cv2.imread("asuFiles/interRefFiles/2023-09-21 12_45_50.bmp")
# mtf_measure(image)