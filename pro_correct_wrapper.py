import csv
import os
import time
from ctypes import *
import cv2
import numpy as np

DIR_NAME = 'asuFiles'
DIR_NAME_COPY = 'asuFiles/copy'

dirExists = os.path.isdir(DIR_NAME)
if not dirExists:
    os.makedirs(DIR_NAME)
dirExists = os.path.isdir(DIR_NAME_COPY)
if not dirExists:
    os.makedirs(DIR_NAME_COPY)
SN = os.popen("adb shell cat /sys/devices/platform/asukey/sn").read()
SN = SN.strip()
print(len(SN), SN)
if len(SN) < 3:
    SN = 'ASU0123456789'

# IMG_AUTO_KEYSTONE = 'asuFiles/auto_keystone.png'
IMG_AUTO_KEYSTONE = 'asuFiles/' + SN + '/projectionFiles/auto_keystone_pattern.png'
FILE_AUTO_KEYSTONE = 'asuFiles/' + SN + '/projectionFiles/keystone.txt'
DIR_NAME_REF = 'asuFiles/' + SN + '/refFiles/'
DIR_NAME_PRO = 'asuFiles/' + SN + '/projectionFiles/'
FILE_NAME_CSV = 'asuFiles/' + SN + '/projectionFiles/test.csv'
CALIB_CONFIG_PARA = 'asuFiles/' + SN + '/config_para.yml'
CALIB_DATA_PATH = 'asuFiles/' + SN + '/calib_data_' + SN + '.yml'
DIR_NAME_INTER_REF = 'asuFiles/interRefFiles/'

dirExists = os.path.isdir(DIR_NAME_REF)
print(DIR_NAME_REF)
if not dirExists:
    os.makedirs(DIR_NAME_REF)
    print('创建目录：', DIR_NAME_REF)
dirExists = os.path.isdir(DIR_NAME_INTER_REF)
if not dirExists:
    os.makedirs(DIR_NAME_INTER_REF)
    print('创建目录：', DIR_NAME_INTER_REF)
dirExists = os.path.isdir(DIR_NAME_PRO)
if not dirExists:
    os.makedirs(DIR_NAME_PRO)
    print('创建目录：', DIR_NAME_PRO)

# 对应标定的姿态数量
NUM_POSTURE = 6
# 投影仪生成的csv数据
CSV_ITEM_NUM = 4  # 4
CSV_TOF = 1
CSV_IMU = 3
CSV_IMG = 4

try:
    dll = CDLL("pro_correction.dll", winmode=0)
    print('load pro_correction.dll')
except OSError:
    print('Cannot find pro_correction.dll.')


def get_sn():
    global SN
    SN = os.popen("adb shell cat /sys/devices/platform/asukey/sn").read()
    SN = SN.strip()
    if len(SN) < 3:
        SN = 'ASU0123456789'
    print('投影设备SN: ', len(SN), SN)
    return SN


def create_dir_file():
    global SN, DIR_NAME_REF, DIR_NAME_PRO, DIR_NAME_INTER_REF,\
        IMG_AUTO_KEYSTONE, FILE_AUTO_KEYSTONE, FILE_NAME_CSV, CALIB_CONFIG_PARA, CALIB_DATA_PATH
    ex = os.path.isdir(DIR_NAME)
    if not ex:
        os.makedirs(DIR_NAME)
    ex = os.path.isdir(DIR_NAME_COPY)
    if not ex:
        os.makedirs(DIR_NAME_COPY)
    get_sn()

    # IMG_AUTO_KEYSTONE = 'asuFiles/auto_keystone.png'
    IMG_AUTO_KEYSTONE = 'asuFiles/' + SN + '/projectionFiles/auto_keystone_pattern.png'
    FILE_AUTO_KEYSTONE = 'asuFiles/' + SN + '/projectionFiles/keystone.txt'
    DIR_NAME_REF = 'asuFiles/' + SN + '/refFiles/'
    DIR_NAME_PRO = 'asuFiles/' + SN + '/projectionFiles/'
    FILE_NAME_CSV = 'asuFiles/' + SN + '/projectionFiles/test.csv'
    CALIB_CONFIG_PARA = 'asuFiles/' + SN + '/config_para.yml'
    CALIB_DATA_PATH = 'asuFiles/' + SN + '/calib_data_' + SN + '.yml'
    DIR_NAME_INTER_REF = 'asuFiles/interRefFiles/'

    ex = os.path.isdir(DIR_NAME_REF)
    if not ex:
        os.makedirs(DIR_NAME_REF)
        print('创建目录：', DIR_NAME_REF)
    ex = os.path.isdir(DIR_NAME_INTER_REF)
    if not ex:
        os.makedirs(DIR_NAME_INTER_REF)
        print('创建目录：', DIR_NAME_INTER_REF)
    ex = os.path.isdir(DIR_NAME_PRO)
    if not ex:
        os.makedirs(DIR_NAME_PRO)
        print('创建目录：', DIR_NAME_PRO)


def make_charpp(arr):
    return (c_char_p * len(arr))(*(s.encode() for s in arr))


def set_point(point):
    # int列表转字符串列表
    point = ','.join(map(str, point))
    # cmd = "adb shell setprop persist.vendor.hwc.keystone 0,0,1920,0,1920.1080,0,1080"
    cmd = "adb shell setprop persist.vendor.hwc.keystone "
    cmd = cmd + point
    print('keystone : ', cmd)
    os.system(cmd)
    time.sleep(1)
    os.system("adb shell service call SurfaceFlinger 1006")


# dll.doubleTest.argtypes = [c_double]
# dll.doubleTest.restype = c_double
# d1 = c_double(10.0)
# rst = dll.doubleTest(d1)
# print("doubleTest return value ", rst)

# if hasattr(dll, 'doublePointTest'):
#     def doublePointTest():
#         d1 = c_double(10)
#         d2 = c_double(10)
#         dll.doublePointTest.argtypes = [POINTER(c_double), POINTER(c_double)]
#         dll.doublePointTest.restype = c_double
#         rst = dll.doublePointTest(byref(d1), byref(d2))
#         print("doublePointTest return value ", rst)

# if hasattr(dll, 'charPointpointTest'):
#     def charPointpointTest():
#         global dll
#         dll.charPointpointTest.argtypes = [POINTER(c_char_p),
#                                            POINTER(c_char_p),
#                                            c_int]
#
#         dll.charPointpointTest.restype = c_int
#         arr0 = ['n00_4106404.png', 'n00_4106404.png', 'test1', 'test2']
#         arr1 = ['n00_4106404.bmp', 'n00_4106404.png', 'test1', 'test2']
#         val = c_int(4)
#         dll.charPointpointTest(make_charpp(arr0), make_charpp(arr0), val)


if hasattr(dll, 'ReferenceCamCalib'):
    def reference_cam__calib_api(calib_config_para, calib_data_path,
                                 list_size,
                                 img_size,
                                 img,
                                 error_list):
        dll.ReferenceCamCalib.argtypes = [c_char_p,
                                          c_char_p,
                                          c_int,
                                          c_int, c_int,
                                          POINTER(c_ubyte),
                                          POINTER(c_double)]
        dll.ReferenceCamCalib.restype = c_int
        calib_config_para = create_string_buffer(calib_config_para.encode('utf-8'))
        calib_data_path = create_string_buffer(calib_data_path.encode('utf-8'))
        list_size = c_int(list_size)
        img_r = c_int(img_size[0])
        img_c = c_int(img_size[1])
        error_list = (c_double * len(error_list))(*error_list)
        print('>>>>>>>>>>>>>>>>>>>> Call ReferenceCamCalib')
        ret = dll.ReferenceCamCalib(calib_config_para, calib_data_path,
                                    list_size,
                                    img_r, img_c,
                                    img.ctypes.data_as(POINTER(c_ubyte)),
                                    error_list)
        return error_list

if hasattr(dll, 'KeystoneCorrectTOF'):
    def keystone_correct_tof_api(calib_data_path,
                                 tof_data_size, imu_data_size,
                                 source_points,
                                 depth_data, imu_data,
                                 correct_points):
        dll.KeystoneCorrectTOF.argtypes = [c_char_p,
                                           c_int, c_int,
                                           POINTER(c_int),
                                           POINTER(c_double),
                                           POINTER(c_double),
                                           POINTER(c_int)]
        dll.KeystoneCorrectTOF.restype = c_int

        calib_data_path = create_string_buffer(calib_data_path.encode('utf-8'))
        tof_data_size = c_int(tof_data_size)
        imu_data_size = c_int(imu_data_size)
        source_points = (c_int * len(source_points))(*source_points)
        depth_data = (c_double * len(depth_data))(*depth_data)
        imu_data = (c_double * len(imu_data))(*imu_data)
        correct_points = (c_int * len(correct_points))(*list(map(int, correct_points)))
        print('>>>>>>>>>>>>>>>>>>>> Call KeystoneCorrectTOF')
        ret = dll.KeystoneCorrectTOF(calib_data_path,
                                     tof_data_size, imu_data_size,
                                     source_points,
                                     depth_data, imu_data,
                                     correct_points)
        for i in range(8):
            print(correct_points[i])
        return correct_points

if hasattr(dll, 'KeystoneCorrectCam'):
    def keystone_correct_cam_api(calib_data_path,
                                 imu_data_size,
                                 img_size,
                                 source_points,
                                 img,
                                 imu_data_list,
                                 correct_points):
        print('>>>>>>>>>>>>>>>>>>>> Load KeystoneCorrectCam')
        dll.KeystoneCorrectCam.argtypes = [c_char_p,
                                           c_int,
                                           c_int, c_int,
                                           POINTER(c_int),
                                           POINTER(c_ubyte),
                                           POINTER(c_double),
                                           POINTER(c_int)]
        dll.KeystoneCorrectCam.restype = c_int
        calib_data_path = create_string_buffer(calib_data_path.encode('utf-8'))
        imu_data_size = c_int(imu_data_size)
        img_r = c_int(img_size[0])
        img_c = c_int(img_size[1])
        source_points = (c_int * len(source_points))(*list(map(int, source_points)))
        imu_data_list = (c_double * len(imu_data_list))(*list(map(int, imu_data_list)))
        correct_points = (c_int * len(correct_points))(*list(map(int, correct_points)))

        dll.KeystoneCorrectCam(calib_data_path, imu_data_size,
                               img_r, img_c,
                               source_points,
                               img.ctypes.data_as(POINTER(c_ubyte)),
                               imu_data_list,
                               correct_points)
        return correct_points

# PRO_CORRECTION_LIB_API  int KeystoneCorrectCam(
#     const char* calib_data_path,int imu_data_size, int img_r, int img_c,
#     const int* source_points, unsigned char* pattern_img,
#     double* imu_data,
#     int* correct_points);
if hasattr(dll, 'KeystoneCorrectCalibS'):
    # 输入：内部相机图片，外部相机图片，图像尺寸
    def keystone_correct_cam_libs(calib_config_para, calib_data_path,
                                  list_size,
                                  ref_img_size, pro_img_size,
                                  tof_data_size, imu_data_size,
                                  ref_imgs,
                                  pro_imgs,
                                  depth_data_list,
                                  imu_data_list,
                                  robot_pose_list,
                                  error):
        dll.KeystoneCorrectCalibS.argtypes = [c_char_p, c_char_p,
                                              c_int,
                                              c_int, c_int, c_int, c_int,
                                              c_int, c_int,
                                              POINTER(c_char_p),
                                              POINTER(c_char_p),
                                              POINTER(c_double),
                                              POINTER(c_double)]
        dll.KeystoneCorrectCalibS.restype = c_int
        print('ref_imgs ', len(ref_imgs), ref_imgs)
        print('pro_imgs ', len(pro_imgs), pro_imgs)
        print('depth_data_list ', len(depth_data_list), depth_data_list)
        print('imu_data_list ', len(imu_data_list), imu_data_list)
        print('robot_pose_list ', len(robot_pose_list), robot_pose_list)
        calib_config_para = create_string_buffer(calib_config_para.encode('utf-8'))
        calib_data_path = create_string_buffer(calib_data_path.encode('utf-8'))
        list_size = c_int(list_size)
        ref_img_r = c_int(ref_img_size[0])
        ref_img_c = c_int(ref_img_size[1])
        pro_img_r = c_int(pro_img_size[0])
        pro_img_c = c_int(pro_img_size[1])
        tof_data_size = c_int(tof_data_size)
        imu_data_size = c_int(imu_data_size)
        ref_cam_pattern_imgs_name = make_charpp(ref_imgs)
        pro_cam_pattern_imgs_name = make_charpp(pro_imgs)
        depth_data = (c_double * len(depth_data_list))(*list(map(float, depth_data_list)))
        imu_data = (c_double * len(imu_data_list))(*list(map(float, imu_data_list)))
        robot_pose = (c_double * len(robot_pose_list))(*list(map(float, robot_pose_list)))
        error = (c_double * len(error))(*error)
        print('>>>>>>>>>>>>>>>>>>>> Load KeystoneCorrectCalibS')
        status = dll.KeystoneCorrectCalibS(calib_config_para, calib_data_path,
                                           list_size,
                                           ref_img_r, ref_img_c, pro_img_r, pro_img_c,
                                           tof_data_size, imu_data_size,
                                           ref_cam_pattern_imgs_name, pro_cam_pattern_imgs_name,
                                           depth_data,
                                           imu_data,
                                           robot_pose,
                                           error)
        return error


def reference_cam_calib():
    files = os.listdir(DIR_NAME_INTER_REF)  # 读入文件夹
    list_size = len(files)
    if list_size == 12:
        img = [0] * list_size
        # (rows, cols) = (img.shape[0], img.shape[1])
        pro_file_list = []
        img_size = ()
        count = 0
        for root, dirs, files in os.walk(DIR_NAME_INTER_REF):
            for file in files:
                ext = os.path.splitext(file)[-1].lower()
                head = os.path.splitext(file)[0].lower()[:2]
                if ext == '.bmp':
                    pro_file_list.append(file)
                    name = DIR_NAME_INTER_REF + file
                    print('name ', name, count)
                    img[count] = cv2.imread(name, cv2.IMREAD_GRAYSCALE)
                    count += 1
                if ext == ".png":
                    pass
        # img = img[0]
        # for i in range(1, list_size):
        #     img = np.append(img, img[i], axis=0)
        img_size = (img[0].shape[0], img[0].shape[1])
        image_list = np.concatenate(
            [img[0], img[1], img[2], img[3], img[4], img[5], img[6], img[7], img[8], img[9], img[10], img[11]], axis=0)
        error_list = [0] * list_size
        ret = reference_cam__calib_api(CALIB_CONFIG_PARA, CALIB_DATA_PATH,
                                       list_size,
                                       img_size,
                                       image_list,
                                       error_list)
        for i in range(list_size):
            error_list[i] = ret[i]
        print('>>>>>>>>>>>>>>>>>>>> 内参标定算法返回状态 ', error_list)
        return True
    else:
        print('>>>>>>>>>>>>>>>>>>>> 内参标定所需要的图片不存在', list_size)
        return False


def keystone_correct_tof():
    imu_data_list = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    correct_points = [0] * 8
    source_points = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
    if len(source_points) > 0:
        source_points = source_points.strip().split(',')
        source_points = list(map(float, source_points))
        source_points = list(map(int, source_points))
    else:
        print('>>>>>>>>>>>>>>>>>>>> 未获取到投影仪的原始坐标')
        source_points = [0, 0, 1920, 0, 1920, 1080, 0, 1080]
    print('原始坐标 ', source_points)

    lastTime = time.time()
    while not os.path.exists(FILE_AUTO_KEYSTONE):
        currentTime = time.time()
        if (currentTime - lastTime) > 6:
            print('>>>>>>>>>>>>>>>>>>>> 未生成文件 ', FILE_AUTO_KEYSTONE)
            return False

    if os.path.exists(FILE_AUTO_KEYSTONE):
        tof_data = []
        file = open(FILE_AUTO_KEYSTONE)
        line = file.readline().strip()  # 读取第一行
        tof_data.append(line)
        while line:  # 直到读取完文件
            line = file.readline().strip()  # 读取一行文件，包括换行符
            tof_data.append(line)
        file.close()  # 关闭文件
        depth_data = tof_data[1].split(',')
        del depth_data[-1]
        depth_data = list(map(float, depth_data))
        print(depth_data)
    else:
        print(IMG_AUTO_KEYSTONE, ' 标定所需要的文件不存在')

    points = keystone_correct_tof_api(CALIB_DATA_PATH,
                                      len(depth_data), len(imu_data_list),
                                      source_points,
                                      depth_data, imu_data_list,
                                      correct_points)
    for i in range(len(correct_points)):
        correct_points[i] = points[i]
    print('>>>>>>>>>>>>>>>>>>>> correct points ', correct_points)
    return True


def auto_keystone_cam():
    imu_data_list = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    correct_points = [0] * 8
    source_points = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
    if len(source_points) > 0:
        source_points = source_points.strip().split(',')
        source_points = list(map(float, source_points))
        source_points = list(map(int, source_points))
    else:
        print('>>>>>>>>>>>>>>>>>>>> 未获取到投影仪的原始坐标')
        source_points = [0, 0, 1920, 0, 1920, 1080, 0, 1080]
    print('原始坐标 ', source_points)
    # source_points = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
    lastTime = time.time()
    while not os.path.exists(IMG_AUTO_KEYSTONE):
        currentTime = time.time()
        if (currentTime - lastTime) > 6:
            print('>>>>>>>>>>>>>>>>>>>> 投影仪未采集到图片 ', IMG_AUTO_KEYSTONE)
            return False
    print('>>>>>>>>>>>>>>>>>>>> 启动相机校正')
    if os.path.exists(IMG_AUTO_KEYSTONE):
        img = cv2.imread(IMG_AUTO_KEYSTONE, cv2.IMREAD_GRAYSCALE)
        # (rows, cols) = (img.shape[0], img.shape[1])
        img_size = (img.shape[0], img.shape[1])
        print(img.shape)
        ret = keystone_correct_cam_api(CALIB_DATA_PATH,
                                       len(imu_data_list),
                                       img_size,
                                       source_points,
                                       img,
                                       imu_data_list,
                                       correct_points)
        for i in range(8):
            correct_points[i] = ret[i]
        print('>>>>>>>>>>>>>>>>>>>> 校正算法返回坐标 ', correct_points)
        return True
    else:
        print(IMG_AUTO_KEYSTONE, ' 标定所需要的图片不存在')


def auto_keystone_calib():
    # 拿到所有数据 n组，每组两个照片，imu，tof
    # file_list_ref = os.listdir(DIR_NAME_E)
    # file_list_pro = os.listdir(DIR_NAME_P)
    # print(len(file_list_ref), file_list_ref, len(file_list_pro), file_list_pro)
    imu_data_list = [0.0, 1.0, 2.0, 3.0, 4.0]
    robot_pose_list = [0, 0, 0]
    # error_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 10, 11, 12, 13]
    files = os.listdir(DIR_NAME_PRO)  # 读入文件夹
    lastTime = time.time()
    while not len(files) >= NUM_POSTURE:
        currentTime = time.time()
        if (currentTime - lastTime) > 6:
            print('>>>>>>>>>>>>>>>>>>>> 投影仪采集的数据不够 ', DIR_NAME_PRO)
            return False

    print('>>>>>>>>>>>>>>>>>>>> 启动全向自动标定')
    # 分析图片
    ref_file_list = []
    pro_file_list = []
    ret = {"jpg": 0, "png": 0, "bmp": 0}
    for root, dirs, files in os.walk(DIR_NAME_REF):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            head = os.path.splitext(file)[0].lower()[:3]
            if ext == '.png':
                ret["jpg"] = ret["jpg"] + 1
            if ext == ".bmp" and head == 'ref':
                ref_file_list.append(file)
                ret["bmp"] = ret["bmp"] + 1

    ret = {"jpg": 0, "png": 0, "bmp": 0}
    for root, dirs, files in os.walk(DIR_NAME_PRO):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            head = os.path.splitext(file)[0].lower()[:2]
            if ext == '.bmp' and head == 'n0':
                ret["jpg"] = ret["jpg"] + 1
            if ext == ".png" and head == 'n0':
                pro_file_list.append(file)
                ret["png"] = ret["png"] + 1
    print('参考图片 ', len(ref_file_list), ref_file_list)
    print('相机图片 ', len(pro_file_list), pro_file_list)
    if len(ref_file_list) == len(pro_file_list):
        print('>>>>>>>>>>>>>>>>>>>> 图片数量正确')
    else:
        print('>>>>>>>>>>>>>>>>>>>> 外部相机与投影内部相机照片数量不一致')
        return False

    ref_img = cv2.imread(DIR_NAME_REF + ref_file_list[0])
    ref_img_size = (ref_img.shape[0], ref_img.shape[1])
    print('行Row: ', ref_img_size[0], ' 列Col:', ref_img_size[1])

    pro_img = cv2.imread(DIR_NAME_PRO + pro_file_list[0])
    pro_img_size = (pro_img.shape[0], pro_img.shape[1])
    print(pro_img_size[0], pro_img_size[1])
    # 分析csv
    if os.path.exists(FILE_NAME_CSV):
        # with 自动关闭文件
        with open(FILE_NAME_CSV, mode='r', encoding='GBK', newline='') as file:
            # 使用csv.reader()将文件中的每行数据读入到一个列表中
            # reader = csv.reader(file, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            # 每一行用一个字典存储
            reader = csv.DictReader(file)
            count = 0
            data_list = [] * 30
            for line in reader:
                # print(line)
                data_list.append(line)
                count += 1

            depth_data_list = []
            for i in range(CSV_TOF, count, CSV_ITEM_NUM):
                del data_list[i]['']
                del data_list[i][None]
                for key in data_list[i].keys():
                    depth_data_list.append(data_list[i][key])
            print(len(depth_data_list), depth_data_list)

            imu_data_list = []
            for i in range(CSV_IMU, count, CSV_ITEM_NUM):
                # print('IMU: ', data_list[i])
                del data_list[i]['']
                for j in range(5, 64):
                    del data_list[i][str(j)]
                for key in data_list[i].keys():
                    imu_data_list.append(data_list[i][key])
            print(len(imu_data_list), imu_data_list)
            #     del data_list[i]['']
            #     del data_list[i][None]
            #     for key in data_list[i].keys():
            #         depth_data_list.append(data_list[i][key])
            # print(len(depth_data_list), depth_data_list)

            # csv.DictWriter() #以字典的形式读写数据
            # 遍历列表将数据按行输出
            # result = list(reader)
            # print('csv文件总行数', len(result), 'csv文件总项目数', (len(result) - 1)/CSV_ITEM_NUM)
            # depth_data_list = []
            # csv_img_name_list = []
            # for i in range(CSV_TOF, len(result), CSV_ITEM_NUM):
            #     depth_data_list = depth_data_list + result[i]
            # print('Tof', len(depth_data_list), depth_data_list)
            # for i in range(CSV_IMU, len(result), CSV_ITEM_NUM):
            #     del result[][]
            #     imu_data_list = imu_data_list + result[i]
            # print('Tof', len(depth_data_list), depth_data_list)
            # for i in range(CSV_IMG, len(result), CSV_ITEM_NUM):
            #     if len(result[i]) > 1:
            #         del result[i][1]
            #     csv_img_name_list = csv_img_name_list + result[i]
            # print('csv img name', len(csv_img_name_list), csv_img_name_list)
        # file.close() with会自动close文件

        # if (len(result) - 1) / 4 == len(ref_file_list):
        #     if csv_img_name_list == pro_file_list:
        #         print('>>>>>>>>>>>>>>>>>>>> 图片数据与CSV中图片文字一致')
        #     else:
        #         print('>>>>>>>>>>>>>>>>>>>> 图片数据与CSV中图片文字不一致')
        #         return False
        # else:
        #     print('>>>>>>>>>>>>>>>>>>>>', FILE_NAME_CSV + '中项目数与图片数量不一致', len(ref_file_list),
        #           len(result) -
    else:
        print('>>>>>>>>>>>>>>>>>>>>', FILE_NAME_CSV + ' 文件不存在')
    error_list = [0] * len(ref_file_list)
    ret = keystone_correct_cam_libs(CALIB_CONFIG_PARA, CALIB_DATA_PATH,
                                    len(ref_file_list), ref_img_size, pro_img_size,
                                    len(depth_data_list), len(imu_data_list),
                                    ref_file_list, pro_file_list, depth_data_list, imu_data_list, robot_pose_list,
                                    error_list)
    for i in range(len(ret)):
        error_list[i] = ret[i]
    print('>>>>>>>>>>>>>>>>>>>> 标定算法返回状态 ', error_list)
    if os.path.exists(CALIB_DATA_PATH):
        print('>>>>>>>>>>>>>>>>>>>> 标定算法生成文件 ', CALIB_DATA_PATH)
    else:
        print('xxxxxxxxxxxxxxxxxxxx 标定算法未生成', CALIB_DATA_PATH, '文件')
    return True

# auto_keystone_calib()
# auto_keystone_cam()
# keystone_correct_tof()
