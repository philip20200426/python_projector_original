import cv2
from PIL import Image
#可能我应该写成"from cv2 import *"的，懒得改了
from cv2 import *
import numpy as np


def show_img(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

'''
1,对图像进行高斯模糊去噪，梯度计算对噪声很敏感；
2,调用Sobel函数计算图像在x,y方向梯度；
3,调用convertScaleAbs函数将x,y梯度图像像素值限制在0-255；
4,调用addWeight函数将x,y梯度图像融合；
5,调用threshold函数对融合图像进行二值化；
6,使用先腐蚀、后膨胀的形态学处理方法对二值图像进行非脏污区域过滤；
7,调用findContours方法查找脏污区域轮廓。
'''

image = Image.open('op02_white_test.png')
print(image.getpixel((1615, 327)), image.getpixel((0, 0)))
print(image)

im = cv2.imread(r"op02_white_test.png")
print(type(im))
show_img("1", im)
im_copy = np.copy(im)
print(im.shape, im.shape[0])
#多通道图像转化为单通道
gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#遍历灰度图，阈值大于150的全变白
for i in range(gray.shape[0]):
    for j in range(gray.shape[1]):
        if 150 > gray[i, j]:
            print(i, j, gray[i, j])
print(type(gray), gray.shape)
print(gray[520, 1443])


#二值化
ret, thresh = cv2.threshold(
    gray,  # 转换为灰度图像,
    230, 255,   # 大于130的改为255  否则改为0
    cv2.THRESH_BINARY)  # 黑白二值化
show_img("2", thresh)

#高斯滤波除噪
gray = cv2.GaussianBlur(thresh, (7, 7), 0)#我这里调整了高斯核大小，当你图片中的缺陷检测不出来时，调整它准没错！

#利用梯度变化检测缺陷（bobel算子）
#dst= cv2.Sobel(src,ddepth,dx,dy,ksize)
# dx=1,dy=0  表示计算水平方向的，不计算竖直方向，谁为1，计算谁
sobelX = cv2.Sobel(gray, cv2.CV_16S, 1, 0, 7)
sobelY = cv2.Sobel(gray, cv2.CV_16S, 0, 1, 7)
#上面的cv2.CV_16S会输出负数，需要下面的convertScaleAbs做绝对值转换
sobelX = cv2.convertScaleAbs(sobelX)
sobelY = cv2.convertScaleAbs(sobelY)
#对两个方向的图叠加
add_img = cv2.addWeighted(sobelX, 1, sobelY, 1, 0)

#ret, thres = cv2.threshold(add_img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)


#边缘检测
contours, hierarchy = cv2.findContours(add_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#print(contours)
cv2.drawContours(im_copy, contours, -1, (0, 0, 255), 1)
show_img("3", im_copy)