import string


def check_hex(message):
    print("len : ", len(message))
    message_len = len(message)
    if message_len == 0 or message_len % 2 != 0:
        return False
    message = ''.join(message.split())  # 去除空格
    for c in message:
        if c not in string.hexdigits:
            print("Input Data must be hexadecimal")
            return False
    return True


# srcfile 需要复制、移动的文件
# dstpath 目的地址

import os
import shutil
from glob import glob

import shutil
from pathlib import Path

# parents = True: 创建中间级父目录
# exist_ok= True: 目标目录存在时不报错

def mv_dir(src_dir,  ):
    Path('copy').mkdir(parents=True, exist_ok=True)  # 直接创建集合文件
    # parents = True: 创建中间级父目录
    # exist_ok= True: 目标目录存在时不报错
    for file in Path('asuFiles').rglob("*"):  # 遍历所有目录下的文件和文件夹
        print(file)
        if file.is_file() and file.parent != Path("集合文件"):  # 判断是否是文件，以及文件所在目录是不是集合文件
            try:
                shutil.copy(file, Path(f"copy/{file.name}"))  # 拼接相对路径
            except Exception as exc:
                print(exc)

def copy_file(srcfile, dstpath):  # 复制函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstpath + fname))


def move_file(srcfile, dstpath):  # 移动函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.move(srcfile, dstpath + fname)  # 移动文件
        print("move %s -> %s" % (srcfile, dstpath + fname))