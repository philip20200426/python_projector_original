import json
import os

from utils.ParsePara import get_para
KST_FILE_CSV_NAME = 'asuFiles/kst_cal_data.csv'
AF_FILE_CSV_NAME = 'result/af_cal_data.csv'
CAL_DATA = 'result/cal_data.csv'

CAL_PROGRESS_STEP = 5
DIS_STEPS_0 = 1000
DIS_STEPS_1 = 1000
DEV_LOCATION_STEPS = 1399

ARM_KST_DELAY_AF = 0
ROTATE_DELAY = 2.1
DEV_AF_CAL_STEPS_OFFSET = 0
TOF_MAX_THR = 3000
TOF_MIN_THR = 1000
IMU_GAP = 10
AF_CAL_MOTOR_THRESHOLD = 0
KST_EVAL_EDGE = 2
KST_EVAL_ANGLE = 1
AF_CAL_EVAL = 1
LOG_ENABLE = False
PRO_PARA_FILE = 'res/para.json'

if os.path.isfile(PRO_PARA_FILE):
    file = open(PRO_PARA_FILE, )
    dic = json.load(file)
    if len(dic) > 0:
        if 'log_enable' in dic.keys():
            LOG_ENABLE = dic['log_enable']
        else:
            LOG_ENABLE = False
        if 'arm_kst_delay_af' in dic.keys():
            ARM_KST_DELAY_AF = dic['arm_kst_delay_af']
        else:
            ARM_KST_DELAY_AF = 0
        if 'delay1' in dic.keys():
            ROTATE_DELAY = dic['delay1']
        else:
            ROTATE_DELAY = 2.1
        if 'af_cal_offset' in dic.keys():
            DEV_AF_CAL_STEPS_OFFSET = dic['af_cal_offset']
        else:
            DEV_AF_CAL_STEPS_OFFSET = 0
        if 'tof_max_thr' in dic.keys():
            TOF_MAX_THR = dic['tof_max_thr']
        else:
            TOF_MAX_THR = 3000
        if 'tof_min_thr' in dic.keys():
            TOF_MIN_THR = dic['tof_min_thr']
        else:
            TOF_MIN_THR = 1000
        if 'imu_thr' in dic.keys():
            IMU_GAP = dic['imu_thr']
        else:
            IMU_GAP = 10
        # 投影自动对焦后马达位置至少是多少
        if 'af_cal_motor_thr' in dic.keys():
            AF_CAL_MOTOR_THRESHOLD = dic['af_cal_motor_thr']
        else:
            AF_CAL_MOTOR_THRESHOLD = 0
        if 'kst_eval_edge' in dic.keys():
            KST_EVAL_EDGE = dic['kst_eval_edge']
        else:
            KST_EVAL_EDGE = 2
        if 'kst_eval_angle' in dic.keys():
            KST_EVAL_ANGLE = dic['kst_eval_angle']
        else:
            KST_EVAL_ANGLE = 1
        if 'af_cal_eval' in dic.keys():
            AF_CAL_EVAL = dic['af_cal_eval']
        else:
            AF_CAL_EVAL = 1
        if 'dis_steps_0' in dic.keys():
            DIS_STEPS_0 = dic['dis_steps_0']
        else:
            DIS_STEPS_0 = 1000
        if 'dis_steps_1' in dic.keys():
            DIS_STEPS_1 = dic['dis_steps_1']
        else:
            DIS_STEPS_1 = 1000
        if 'dev_location_steps' in dic.keys():
            DEV_LOCATION_STEPS = dic['dev_location_steps']
        else:
            DEV_LOCATION_STEPS = 1399
    else:
        print('{}文件是空的!!!'.format(PRO_PARA_FILE))
    file.close()
else:
    print('{}不存在!!!'.format(PRO_PARA_FILE))

print(
    '初始化静态参数，云台延时：{}，对焦标定步数补偿：{}, Imu阈值：{}, Tof阈值：{} {}, 自动对焦阈值步数：{}, 评估标准：{} {}, Log开关：{}, 梯形校正与对焦之间延时 {}'.format(
        ROTATE_DELAY, DEV_AF_CAL_STEPS_OFFSET, IMU_GAP, TOF_MAX_THR, TOF_MIN_THR, AF_CAL_MOTOR_THRESHOLD, KST_EVAL_EDGE,
        KST_EVAL_ANGLE, LOG_ENABLE, ARM_KST_DELAY_AF))
