# -*- coding: utf-8 -*-

"""
@File    : 3.py
@Author  : raymood
@Time    : 2022/5/6 14:53
@description : NULL
"""
import serial
import time


class Binary:
    """
        自定义进制转化
    """

    @staticmethod
    def Hex2Dex(e_hex):
        """
        十六进制转换十进制
        :param e_hex:
        :return:
        """
        return int(e_hex, 16)

    @staticmethod
    def Hex2Bin(e_hex):
        """
        十六进制转换二进制
        :param e_hex:
        :return:
        """
        return bin(int(e_hex, 16))

    @staticmethod
    def Dex2Bin(e_dex):
        """
        十进制转换二进制
        :param e_dex:
        :return:
        """
        return bin(e_dex)


class CRC:
    """
     CRC验证
    """

    def __init__(self):
        self.Binary = Binary()

    def CRC16(self, hex_num):
        """
        CRC16校验
        :param hex_num:
        :return:
        """
        crc = '0xffff'
        crc16 = '0xA001'
        # test = '01 06 00 00 00 00'
        test = hex_num.split(' ')
        print(test)

        crc = self.Binary.Hex2Dex(crc)  # 十进制
        crc16 = self.Binary.Hex2Dex(crc16)  # 十进制
        for i in test:
            temp = '0x' + i
            # 亦或前十进制准备
            temp = self.Binary.Hex2Dex(temp)  # 十进制
            # 亦或
            crc ^= temp  # 十进制
            for i in range(8):
                if self.Binary.Dex2Bin(crc)[-1] == '0':
                    crc >>= 1
                elif self.Binary.Dex2Bin(crc)[-1] == '1':
                    crc >>= 1
                    crc ^= crc16
                # print('crc_D:{}\ncrc_B:{}'.format(crc, self.Binary.Dex2Bin(crc)))

        crc = hex(crc)
        crc_H = crc[2:4]
        crc_L = crc[-2:]

        return crc, crc_H, crc_L


if __name__ == '__main__':

    # 基础报文
    sendbytes = '01 06 04 87 00 0A'
    # 生成CRC16校验码
    CRC = CRC()
    crc, crc_H, crc_L = CRC.CRC16(sendbytes)
    print('======', crc, crc_H, crc_L)
    # 生成完整报文
    sendbytes = sendbytes + ' ' + crc_L + ' ' + crc_H
    print(sendbytes)

    # 连接端口 'com6', 超时0.8，比特率9600、8字节、无校验、停止位1
    com = serial.Serial(port="com15", baudrate=9600, timeout=0.8, bytesize=8, parity='E', stopbits=1)
    if com.is_open:
        print("port open success")
        # 将hexstr导入bytes对象  报文需要是字节格式
        sendbytes = bytes.fromhex(sendbytes)
        # 发送报文
        com.write(sendbytes)
        print(com.readall())