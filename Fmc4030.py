import binascii
import struct
import time
import re

from math_utils import CRC


def test(ser):
    print('串口测试:')
    if ser is not None:
        ser.write('xu 7411\n\r'.encode())
        #ser.write('am start -n com.nbd.autofocus/com.nbd.autofocus.KeystoneCalibration\n\r'.encode())
        ser.write('cat /sdcard/DCIM/projectionFiles/AsuProData.json\n\r'.encode())
    s = ''
    while True:
        if ser is not None:
            data = ser.readline().decode('utf-8')
            #print(data)
            if data == '':
                print('结束读数据')
                break
            else:
                s = s + data

    print('>>>>>>>>>>>>>>>>>>>>>>>>')
    print(s)
    pattern = r'\{(.*?)\}'  # 匹配中括号中的内容
    result = re.search(pattern, s)
    print('!!!!!!!!!!!!!!!!!!!!!!')
    print(result)

def init(ser):
    # 归零，设置参数
    cmd_list = [[], []]
    cmd_list[0] = ['01', '05', '00', '12', 'FF', '00']
    cmd_list[1] = ['01', '10', '00', '4E', '00', '02', '04', '43', '48', '00', '00']
    start = time.time()
    i = 0
    while i < len(cmd_list):
        data_list = rail_send(ser, cmd_list[i])
        print('+++++++++++++++ ', data_list)
        if data_list != '' and len(data_list) > 2:
            if data_list[0:3] == cmd_list[i][0:3]:
                i += 1
            else:
                print('返回数据错误，重新发送')
            cur = time.time()
            if (cur - start) > 6:
                print('>>>>>>>>>> 导轨操作超时:', (cur - start))
                return -100


def rail_forward(ser, direction, rel_dis):
    if not ser is None:
        cmd_list = [[], []]
        # 距离
        cmd_list[0] = ['01', '10', '00', '4C', '00', '02', '04']
        # 正反转
        cmd_list[1] = ['01', '05', '00', '00', 'FF', '00']
        rel_dis_char = float_to_hex(rel_dis)
        cmd_list[0].append(rel_dis_char[0:2])
        cmd_list[0].append(rel_dis_char[2:4])
        cmd_list[0].append(rel_dis_char[4:6])
        cmd_list[0].append(rel_dis_char[6:8])
        if direction == 0:
            cmd_list[1][3] = '00'
        if direction == 1:
            cmd_list[1][3] = '03'
        # print(cmd_list[0])
        # print(cmd_list[1])
        start = time.time()
        i = 0
        while i < len(cmd_list):
            print('++++++++++++++++', i)
            data_list = rail_send(ser, cmd_list[i])
            print(cmd_list[i])
            if data_list[0:3] == cmd_list[i][0:3]:
                i += 1
            cur = time.time()
            if (cur - start) > 5.6:
                print('>>>>>>>>>> 导轨操作超时:', (cur - start))
                return -100
    else:
        print('请先打开串口')


def rail_forward_pos(ser, rel_dis):
    if not ser is None:
        cmd_list = [[], []]
        # 位移值
        cmd_list[0] = ['01', '10', '00', '4C', '00', '02', '04']
        # 绝对位移
        cmd_list[1] = ['01', '05', '00', '06', 'FF', '00']
        rel_dis_char = float_to_hex(rel_dis)
        cmd_list[0].append(rel_dis_char[0:2])
        cmd_list[0].append(rel_dis_char[2:4])
        cmd_list[0].append(rel_dis_char[4:6])
        cmd_list[0].append(rel_dis_char[6:8])

        start = time.time()
        i = 0
        while i < len(cmd_list):
            data_list = rail_send(ser, cmd_list[i])
            if data_list[0:3] == cmd_list[i][0:3]:
                i += 1
            cur = time.time()
            if (cur - start) > 3:
                print('>>>>>>>>>> rail_forward_pos timeout:', (cur - start))
                return -100
    else:
        print('请先打开串口')


def rail_position(ser):
    if not ser is None:
        cmd_list = ['01', '03', '00', '3E', '00', '02']
        data_list = rail_send(ser, cmd_list)
        print(data_list)
        if data_list[0:2] == cmd_list[0:2]:
            pos = int(hex_to_float(''.join(data_list[3:7])))
            # print(pos)
        else:
            pos = -100
        return pos
    else:
        print('请先打开串口')


def rail_stop(ser):
    cmd_list = ['01', '05', '00', '09', 'FF', '00']
    data_list = rail_send(ser, cmd_list)
    if data_list[0:2] == cmd_list[0:2]:
        pos = int(hex_to_float(''.join(data_list[3:7])))
        print(pos)
    else:
        pos = -100
    return pos


def rail_send(ser, cmd_list):
    if not ser is None:
        cmd_lit_cp = cmd_list.copy()
        cmd_char = ' '.join(cmd_lit_cp)
        crc, crc_h, crc_l = CRC().CRC16(cmd_char)
        cmd_lit_cp.append(crc_l)
        cmd_lit_cp.append(crc_h)
        cmd_char = ' '.join(cmd_lit_cp)
        print('rail_send,发送数据:', cmd_char)
        cmd_hex = bytes.fromhex(cmd_char)
        if ser is not None:
            ser.write(cmd_hex)
        else:
            print('rail_send:串口写异常', ser)

        start = time.time()
        data = b''
        ret = b''
        while True:
            cur = time.time()
            if (cur - start) > 2:
                print('rail_send, 串口读数据超时:', (cur - start))
                return -100
            if ser is not None:
                ret = ser.read()
            else:
                print('rail_send:串口读异常', ser)
            if len(ret):
                data += ret
            else:
                cur_data = data.hex()
                data_list = re.findall('.{2}', cur_data)
                # print('rail_send,返回数据:', data_list)
                return data_list
    else:
        print('请先打开串口')


def float_to_hex(f):
    # IEEE 754浮点数十六进制相互转换(32位,四字节,单精度)
    # 将浮点数转换为字节串
    b = struct.pack('!f', f)
    # 将字节串转换为16进制字符串
    h = binascii.hexlify(b)
    return h.decode('ascii')


def hex_to_float(h):
    # IEEE 754浮点数十六进制相互转换(32位,四字节,单精度)
    # 将16进制字符串转换为字节串
    b = binascii.unhexlify(h)
    # 将字节串转换为浮点数
    f = struct.unpack('!f', b)[0]
    return f

# def rail_send(ser, cmd_list):
#     # 归零，设置参数
#     # cmd_list = ['01', '03', '00', '3E', '00', '02']
#     data_list = []
#     cmd_char = ' '.join(cmd_list)
#     crc, crc_h, crc_l = CRC().CRC16(cmd_char)
#     cmd_list.append(crc_l)
#     cmd_list.append(crc_h)
#     cmd_char = ' '.join(cmd_list)
#     print(cmd_char)
#     cmd_hex = bytes.fromhex(cmd_char)
#     if ser is not None:
#         ser.write(cmd_hex)
#     else:
#         print('>>>>>>>>>>>>>>>>>>>> 串口异常')
#
#     start = time.time()
#     data = b''
#     while True:
#         cur = time.time()
#         if (cur - start) > 3:
#             print('>>>>>>>>>> 串口读数据超时')
#             return -100
#         time.sleep(0.1)
#         data = ser.read(ser.inWaiting())
#         current_data = data.hex()
#         data_list = re.findall('.{2}', current_data)
#         # print('============== ', data_list)
#         # pos = int(hex_to_float(''.join(data_list[3:7])))
#         # print(pos)
#     return data_list
