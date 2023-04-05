
import cv2
import numpy as np
# 读入图像
img = cv2.imread(r"op02_white_test.png", cv2.IMREAD_UNCHANGED)

# 二值化
# ret, thresh = cv2.threshold(
#     cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY),  # 转换为灰度图像,
#     240, 255,   # 大于130的改为255  否则改为0
#     cv2.THRESH_BINARY)  # 黑白二值化

# 搜索轮廓
contours, hierarchy = cv2.findContours(
    img,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_NONE)

for c in contours:

    x, y, w, h = cv2.boundingRect(c)
    """
    传入一个轮廓图像，返回 x y 是左上角的点， w和h是矩形边框的宽度和高度
    """
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    """
    画出矩形
        img 是要画出轮廓的原图
        (x, y) 是左上角点的坐标
        (x+w, y+h) 是右下角的坐标
        0,255,0）是画线对应的rgb颜色
        2 是画出线的宽度
    """

    # 获得最小的矩形轮廓 可能带旋转角度
    rect = cv2.minAreaRect(c)
    # 计算最小区域的坐标
    box = cv2.boxPoints(rect)
    # 坐标规范化为整数
    box = np.int0(box)
    # 画出轮廓
    cv2.drawContours(img, [box], 0, (0, 0, 255), 3)

    # 计算最小封闭圆形的中心和半径
    (x, y), radius = cv2.minEnclosingCircle(c)
    # 转换成整数
    center = (int(x), int(y))
    radius = int(radius)
    # 画出圆形
    img = cv2.circle(img, center, radius, (0, 255, 0), 2)

# 画出轮廓
cv2.drawContours(img, contours, -1, (255, 0, 0), 1)
cv2.imshow("contours", img)
cv2.waitKey()
cv2.destroyAllWindows()