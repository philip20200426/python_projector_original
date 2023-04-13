import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap, qRgb


def create_image(value):
    img_green = np.zeros([400, 600], np.uint8)
    print(value)
    # img_green = np.zeros([400, 400]) + 255
    img_green[:] = value
    img = Image.fromarray(img_green, 'L')
    # img.save("out.bmp")
    # img.show()
    print(img_green.shape[1], img_green.shape[0], img_green.shape[1] * 3)
    q_img = QImage(img_green.data, img_green.shape[1], img_green.shape[0], QImage.Format_Grayscale8)

    # image = QImage(3, 3, QImage.Format_Indexed8)
    # value = qRgb(122, 163, 39)  # 0xff7aa327
    # image.setColor(0, value)

    pix = QPixmap(q_img).scaled(600, 480)

    return pix

# img_green = np.zeros([400, 400, 3], np.uint8)
# img_green[:, :, 0] = np.zeros([400, 400]) + 255
# img = Image.fromarray(img_green, 'L')
# img.save("out.bmp")
