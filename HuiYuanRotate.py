import binascii
import socket
import struct
import time
import re

import Constants
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
    print_debug('设置云台角度：', degree0, degree1)
    hy_rotate(socket, 0, degree0)
    hy_rotate(socket, 1, degree1)
    # time.sleep(6)
    # h_angle, v_angle = hy_get_rotate(socket)
    lst = time.time()
    while True:
        time.sleep(0.6)
        cur = time.time()
        h_angle, v_angle = hy_get_rotate(socket)
        if abs(v_angle - degree1) < 0.5 and abs(h_angle - degree0) < 0.5:
            print_debug('耗时：', round(cur - lst, 1), h_angle, v_angle)
            return h_angle, v_angle
        if cur - lst > 5:
            print('!!!!!!!!!!转台角度异常,超时：', cur-lst, h_angle, v_angle)
            return h_angle, v_angle


def hy_rotate(socket, mode, degree):
    angle = degree
    data = 0
    if angle > 30:
        angle = 30
    elif angle < -30:
        angle = -30
    # 发送数据到服务端
    if mode == 1:
        # print('垂直:', angle)
        # 垂直
        mode = '4d'
        if angle > 0:
            data = (angle * 100) >> 8
        elif angle < 0:
            data = 255 - ~((angle * 100) >> 8)
    elif mode == 0:
        # 水平
        # print('水平:', angle)
        mode = '4b'
        if angle < 0:
            angle = angle + 360
        data = (angle * 100) >> 8

    # cmd_list = ['ff', '01', '00', '4b', '05', '78', 'c9']
    cmd_list = ['ff', '01', '4b', '86', '05', '78', 'c9']
    cmd_list[2] = mode
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
    # print(mode, cmd_char)
    # print(mode, cmd_hex)
    server_address = ('192.168.8.200', 6666)
    socket.sendto(cmd_hex, server_address)

    # 接收数据和地址
    data, server_address = socket.recvfrom(1024)
    #print('9999999999999: ', data.hex())


def hy_get_rotate(socket):
    # 读取角度
    cmd_list = ['ff', '01', '00', '51', '00', '00', 'c9']

    # 计算校验和
    sum_data = 0
    for i in range(1, len(cmd_list) - 1):
        sum_data += int(cmd_list[i], 16)
    cmd_list[len(cmd_list) - 1] = '{:02x}'.format(sum_data)[-2:]
    # print(sum_data, hex(sum_data), cmd_list)
    cmd_char = ' '.join(cmd_list)
    cmd_hex = bytes.fromhex(cmd_char)

    socket.sendto(cmd_hex, Constants.ROTATE_SERVER_ADDRESS)
    data, server_address = socket.recvfrom(1024)
    h_angle = int(data.hex()[8] + data.hex()[9] + data.hex()[10] + data.hex()[11], 16) / 100
    if h_angle > 180:
        h_angle = h_angle - 360
    h_angle = round(h_angle, 1)
    # print(data.hex())
    # print('水平返回的角度数据: ', h_angle)

    # 读取角度
    cmd_list = ['ff', '01', '00', '53', '00', '00', 'c9']
    # 计算校验和
    sum_data = 0
    for i in range(1, len(cmd_list) - 1):
        sum_data += int(cmd_list[i], 16)
    cmd_list[len(cmd_list) - 1] = '{:02x}'.format(sum_data)[-2:]
    # print(sum_data, hex(sum_data), cmd_list)
    cmd_char = ' '.join(cmd_list)
    cmd_hex = bytes.fromhex(cmd_char)

    socket.sendto(cmd_hex, Constants.ROTATE_SERVER_ADDRESS)
    data, server_address = socket.recvfrom(1024)
    v_angle = int(data.hex()[8] + data.hex()[9] + data.hex()[10] + data.hex()[11], 16)
    if v_angle > 32768:
        v_angle = (v_angle - 2**16)/100
    else:
        v_angle = v_angle/100
    v_angle = round(v_angle, 1)
    # print(data.hex())
    # print('水平返回的角度数据: ', h_angle)
    return h_angle, v_angle
