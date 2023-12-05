import json
import os

from utils.ParsePara import get_para
ARM_KST_DELAY_AF = 0
LOG_ENABLE = False
PRO_PARA_FILE = 'res/para.json'
if os.path.isfile(PRO_PARA_FILE):
    file = open(PRO_PARA_FILE, )
    dic = json.load(file)
    if len(dic) > 0:
        if 'arm_kst_delay_af' in dic.keys():
            ARM_KST_DELAY_AF = dic['arm_kst_delay_af']
        else:
            ARM_KST_DELAY_AF = 0
        if 'log_enable' in dic.keys():
            LOG_ENABLE = dic['log_enable']
        else:
            LOG_ENABLE = 0
    else:
        print('{}文件是空的!!!'.format(PRO_PARA_FILE))
    file.close()
else:
    print('{}不存在!!!'.format(PRO_PARA_FILE))

# 这里斜投和正投的步数不一致，需要注意
CAL_PROGRESS_STEP = 5
DIS_STEPS_0 = 1000
DIS_STEPS_1 = 1000
DEV_LOCATION_STEPS = 1399
# DEV_AF_CAL_STEPS_OFFSET = -68
# IMU_GAP = 10


KST_FILE_CSV_NAME = 'asuFiles/kst_cal_data.csv'

AF_FILE_CSV_NAME = 'result/af_cal_data.csv'
CAL_DATA = 'result/cal_data.csv'
# LOG_ENABLE = get_para('res/para.json', 'log_enable')
ROTATE_DELAY = get_para('res/para.json', 'delay1')
DEV_AF_CAL_STEPS_OFFSET = get_para('res/para.json', 'af_cal_offset')
IMU_GAP = get_para('res/para.json', 'imu_thr')
AF_CAL_MOTOR_THRESHOLD = get_para('res/para.json', 'af_cal_motor_thr')
TOF_MAX_THR = get_para('res/para.json', 'tof_max_thr')
TOF_MIN_THR = get_para('res/para.json', 'tof_min_thr')
KST_EVAL_EDGE = get_para('res/para.json', 'kst_eval_edge')
KST_EVAL_ANGLE = get_para('res/para.json', 'kst_eval_angle')
AF_CAL_EVAL = get_para('res/para.json', 'af_cal_eval')
# if LOG_ENABLE == -999:
#     LOG_ENABLE = True
if ROTATE_DELAY == -999:
    ROTATE_DELAY = 3.6
if DEV_AF_CAL_STEPS_OFFSET == -999:
    DEV_AF_CAL_STEPS_OFFSET = 0
if IMU_GAP == -999:
    IMU_GAP = 10
if AF_CAL_MOTOR_THRESHOLD == -999:
    AF_CAL_MOTOR_THRESHOLD = 1000
if TOF_MAX_THR == -999:
    TOF_MAX_THR = 1900
if TOF_MIN_THR == -999:
    TOF_MIN_THR = 1300
if KST_EVAL_EDGE == -999:
    KST_EVAL_EDGE = 2
if KST_EVAL_ANGLE == -999:
    KST_EVAL_ANGLE = 1
if AF_CAL_EVAL == -999:
    AF_CAL_EVAL = 50
print(
    '初始化参数，云台延时：{}，对焦标定步数补偿：{}, Imu阈值：{}, Tof阈值：{} {}, 自动对焦阈值步数：{}, 评估标准：{} {}, Log开关：{}, 延时 {}'.format(
        ROTATE_DELAY, DEV_AF_CAL_STEPS_OFFSET, IMU_GAP, TOF_MAX_THR, TOF_MIN_THR, AF_CAL_MOTOR_THRESHOLD, KST_EVAL_EDGE,
        KST_EVAL_ANGLE, LOG_ENABLE, ARM_KST_DELAY_AF))
