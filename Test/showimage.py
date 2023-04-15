# -*- coding: utf-8 -*-
import cv2
import numpy as np

# mouse callback function
state = False


def MyCallBack(event, x, y, flags, param):
    global state
    if event == cv2.EVENT_LBUTTONDOWN:
        print('left button down')
        state = True
    elif event == cv2.EVENT_LBUTTONUP:
        state = False
        print('left button up')
    if event == cv2.EVENT_MOUSEMOVE:
        if state == True:
            cv2.circle(img, (x, y), 2, (255, 126, 0), -1)


def clear():
    global img
    img[:, :, -1] = 0


# 创建图像与窗口并将窗口与回调函数绑定
img = np.zeros((740, 1400, 3), np.uint8)
print('img ', type(img))
cv2.namedWindow('image')
cv2.setMouseCallback('image', MyCallBack, img)
tl_point = (220, 70)
br_point = (480, 280)
cv2.rectangle(img, tl_point, br_point, (0, 0, 255), 2)

while (1):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    break
    # k = cv2.waitKey(1) & 0xFF
    # if k == 32:
    #     img[:] = 0
    # elif k == 27:
    #     break

cv2.destroyAllWindows()