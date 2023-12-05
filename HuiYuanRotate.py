import binascii
import socket
import struct
import time
import re

from math_utils import CRC
from utils.logUtil import print_debug


def open_hy_dev():
    # 创建一个 socket 对象
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print_debug('打开转台')
    return udp_socket


def close_hy_dev(socket):
    socket.close()
    print('关闭转台')


def hy_control(socket, degree0, degree1):
    hy_rotate(socket, 0, degree0)
    hy_rotate(socket, 1, degree1)


def hy_rotate(socket, mode, degree):
    angle = degree
    data = 0
    if angle > 30:
        angle = 30
    elif angle < -30:
        angle = -30
    # 发送数据到服务端
    if mode == 1:
        print('垂直:', angle)
        # 垂直
        mode = '4d'
        if angle > 0:
            data = (angle * 100) >> 8
        elif angle < 0:
            data = 255 - ~((angle * 100) >> 8)
    elif mode == 0:
        # 水平
        print('水平:', angle)
        mode = '4b'
        if angle < 0:
            angle = angle + 360
        data = (angle * 100) >> 8

    cmd_list = ['ff', '01', '00', '4b', '05', '78', 'c9']
    cmd_list[3] = mode
    cmd_list[4] = '{:02x}'.format(data)
    cmd_list[5] = '{:02x}'.format((angle * 100) & 0x00ff)

    # 计算校验和
    sum_data = 0
    for i in range(1, len(cmd_list) - 1):
        sum_data += int(cmd_list[i], 16)
    cmd_list[len(cmd_list) - 1] = '{:02x}'.format(sum_data)[-2:]
    # print(sum_data, hex(sum_data), cmd_list)
    cmd_char = ' '.join(cmd_list)
    cmd_hex = bytes.fromhex(cmd_char)

    server_address = ('192.168.8.200', 6666)
    socket.sendto(cmd_hex, server_address)

    # 接收数据和地址
    data, server_address = socket.recvfrom(1024)

    print('UDP Client Received Data From Server: ', data)
