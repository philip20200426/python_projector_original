import binascii

import cv2

# bytes.fromhex 转化出来的是ASCII码
print(bytes.fromhex('0001020304DF'))

print(bytes.fromhex('6162636465'))

print(hex(ord('a')))

print(hex(ord('1')))

hexCmd = "01 03 06 00 00 10 44 8E"
hexCmd = hexCmd.replace(' ', '')  # 去除空格
cmd = binascii.a2b_hex(hexCmd)  # 转换为16进制串
print(cmd)

print(bytes([0, 1, 0x56]).hex())
print(bytes.fromhex(bytes([0, 1, 0x56]).hex()))


img_bgr = cv2.imread("output_image.jpg")
cv2.namedWindow("myImage", cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow("myImage", 0, 0)
cv2.setWindowProperty("myImage", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("myImage", img_bgr)
cv2.waitKey(0)