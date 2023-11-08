import os
import time

import globalVar
from pro_correct_wrapper import get_sn

PRO_SYS_APP = True
MOTOR_ABNORMAL = -9999
TIME_OUT = 8
MOTOR_FORWARD = 2
MOTOR_BACKUP = 5
STEPS_GAP = 5
MAX_STEPS_RANGE = 2960
MIN_MOTOR_TIME = 0.38
# motor_speed = 3.6 / 2589  # s/step
motor_speed = 7.6 / 2589  # s/step
motor_steps_pos = 0

# 0: hisi, 1: amlogic
PLATFORM_HISI = 0
PLATFORM_AMLOGIC = 1
PLATFORM_HW = PLATFORM_HISI
PRO_MOTOR_RES = True


def pro_kst_cal_service():
    os.system("adb shell am broadcast -a asu.intent.action.RemovePattern")
    os.system('adb shell am startservice com.nbd.autofocus/com.nbd.autofocus.TofService')


def pro_pull_data():
    localSN = get_sn()
    dir_pro_path = globalVar.get_value('DIR_NAME')
    distDirName = dir_pro_path + '/' + localSN
    cmd = 'adb pull /sdcard/DCIM/projectionFiles ' + distDirName
    print('Pull files from PC : ', cmd)
    os.system(cmd)


def pro_save_pos_data(flag=0, pos=0, rois="0a15a15a12,0a15a3a0,12a15a15a0,0a3a15a0", mode=1, loop=2,
                      timing_budget=160000):
    cmd0 = "adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a " \
           "com.nbd.autofocus.TofService --ei type 2 --ei flag "
    cmd1 = str(flag)
    cmd2 = " --ei pos "
    cmd3 = str(pos)
    cmd4 = ' --es rois "'
    cmd5 = str(rois)
    cmd6 = '"'
    cmd = cmd0 + cmd1 + cmd2 + cmd3 + cmd4 + cmd5 + cmd6
    # print(cmd)
    os.system(cmd)
    # cmd0 = "adb shell am broadcast -a asu.intent.action.SaveData --ei position "
    # cmd1 = '11'
    # cmd = cmd0 + cmd1
    # os.system(cmd)


def pro_mtf_test_activity():
    os.system('adb shell am start -n com.nbd.autofocus/com.nbd.autofocus.KeystoneCalibration')


def pro_show_pattern_af():
    # os.system('adb shell am broadcast -a asu.intent.action.ShowBlankPattern')
    os.system(
        'adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a '
        '"com.nbd.autofocus.TofService" --ei type 7 --ei flag 1')


def pro_show_pattern(mode=1):
    cmd0 = 'adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a com.nbd.autofocus.TofService" --ei type 7 --ei flag '
    cmd1 = str(mode)
    os.system(cmd0 + cmd1)


def pro_tof_cal():
    cmd0 = 'adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a ' \
           'com.nbd.autofocus.TofService" --ei type 7 --ei flag 6'
    os.system(cmd0)


def pro_get_motor_position():
    location = os.popen('adb shell cat sys/devices/platform/customer-AFmotor/location').read()
    # print('Read projector motor location:', location)
    if location != '':
        location = int(location[9:-1])
    else:
        location = MOTOR_ABNORMAL
        print('马达异常！！！！！！！！！！！！！！！！！！')
    # print('Read projector motor location:', location)
    return location


# 这个函数一定会让马达走到指定位置，除非马达坏了
# 返回值：实际走的步数
def pro_motor_forward2(direction, steps):
    if not PRO_MOTOR_RES:
        motor_forward(direction, steps)
        return steps
    else:
        location = pro_get_motor_position()
        ret_steps = pro_motor_forward(direction, steps)
        while abs(ret_steps - steps) > STEPS_GAP:
            if pro_motor_forward(direction, steps) < STEPS_GAP * 2:
                print('>>>>>>>>>>>>>>>>>>>> 马达到头了,当前位置:' + str(
                    pro_get_motor_position()) + ',实际执行步数:' + str(
                    ret_steps))
                break
            else:
                print('!!!!!!!!!!!!!!!!!!!! 马达丢步了，需要重新复位')
                if direction == MOTOR_BACKUP:
                    location -= steps
                    if location < 0:
                        location = 0
                elif direction == MOTOR_FORWARD:
                    location += steps
                ret_steps = abs(pro_motor_reset_steps(location) - location)
                print('>>>>>>>>>>>>>>>>>>>> 当前位置:' + str(pro_get_motor_position()) + ',实际执行步数:' + str(
                    ret_steps))
        return ret_steps


def pro_motor_forward(direction, steps):
    global motor_steps_pos
    if steps > 2800:
        print('!!!!!!!!!! 调用当前接口会有问题，请调用其他接口', steps)
        return MOTOR_ABNORMAL
    time_out = motor_speed * steps
    if time_out < MIN_MOTOR_TIME:
        time_out = MIN_MOTOR_TIME
    ret_steps = MOTOR_ABNORMAL
    location = pro_get_motor_position()
    motor_steps_pos = location
    if direction == MOTOR_FORWARD:
        motor_steps_pos += steps
    else:
        motor_steps_pos -= steps
    if location >= 0 or location < MAX_STEPS_RANGE:
        motor_forward(direction, steps)
        sta = time.time()
        while True:
            cur = time.time()
            cur_location = pro_get_motor_position()
            ret_steps = abs(cur_location - location)
            if cur_location == 0 or abs(ret_steps - steps) < STEPS_GAP:
                print('马达执行' + str(ret_steps) + '步' + ',当前位置:' + str(cur_location))
                time.sleep(0.2)
                break
            if abs(cur - sta) > time_out:
                print('马达故障或到头！！！，马达执行' + str(steps) + '步失败' + '超时：' + str(cur - sta) + ',' + str(
                    time_out) + ',实际步数:' + str(ret_steps))
                break
    else:
        print('马达异常，需要立刻复位 !!!!!!!!!!, location:', location)
    return ret_steps


def pro_motor_reset_steps(steps):
    global motor_steps_pos
    count = 0
    location = 0
    while count < 3:
        motor_reset()
        start = time.time()
        while True:
            cur = time.time()
            if abs(cur - start) > TIME_OUT:
                print('马达复位超时')
                count += 1
                if count == 3:
                    return MOTOR_ABNORMAL
            cur_location = pro_get_motor_position()
            if (int(cur_location)) == 0:
                print('马达复位完成', location)
                motor_steps_pos = 0
                count = 3
                break
    time.sleep(0.3)
    motor_steps_pos += steps
    motor_steps = pro_motor_forward(MOTOR_FORWARD, steps)
    if abs(motor_steps - steps) < STEPS_GAP:
        print('马达运行到位置:', steps, motor_steps, motor_steps_pos)
    else:
        print('马达运行到位置:' + str(steps) + '时,发生错误')
    return motor_steps


def motor_reset():
    if PRO_SYS_APP:
        # os.system("adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value 3000")
        cmd = 'adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a ' \
              'com.nbd.autofocus.TofService --ei type 8 --es operate 5 --ei value 3000'
        os.system(cmd)
    else:
        os.system('adb shell "echo 5 3000 > /sys/devices/platform/customer-AFmotor/step_set"')


def motor_forward(dir, steps):
    if PRO_SYS_APP:
        # cmd1 = 'adb shell am broadcast -a asu.intent.action.Motor --es operate '
        cmd0 = 'adb shell am startservice -n com.nbd.autofocus/com.nbd.autofocus.TofService -a ' \
               'com.nbd.autofocus.TofService --ei type 8 --es operate '
        cmd1 = str(dir)
        cmd2 = ' --ei value '
        cmd3 = str(int(steps))
        cmd = cmd0 + cmd1 + cmd2 + cmd3
        # print(cmd)
    else:
        cmd1 = "adb shell "
        cmd2 = 'echo 5 '
        cmd3 = str(steps)
        cmd4 = ' > /sys/devices/platform/customer-AFmotor/step_set"'
        cmd = cmd1 + cmd2 + cmd3 + cmd4
        os.system(cmd)
        # 5 2
    os.system(cmd)


def pro_trigger_auto_ai():
    # 触发自动梯形和自动对焦
    # 触发全向
    # os.system(
    #    'adb shell am startservice -n com.asu.asuautofunction/com.asu.asuautofunction.AsuSessionService -a "com.asu.projector.focus.AUTO_FOCUS" --ei type 0 flag 0')
    # 触发对焦
    os.system(
        'adb shell am startservice -n com.asu.asuautofunction/com.asu.asuautofunction.AsuSessionService -a "com.asu.projector.focus.AUTO_FOCUS" --ei type 2 flag 0')
    # # 触发自动梯形和自动对焦
    # # 触发全向
    # os.system(
    #     'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 2 flag 0')
    # # 触发对焦
    # os.system(
    #     'adb shell am startservice -n com.cvte.autoprojector/com.cvte.autoprojector.CameraService --ei type 0 flag 1')


def connect_dev(ip_addr):
    cmd0 = 'adb connect '
    cmd1 = ip_addr
    cmd2 = ':5555'
    cmd = cmd0 + cmd1 + cmd2
    os.system(cmd)
    print(cmd)
    os.system('adb root')
    time.sleep(1)
    os.system('adb remount')


def pro_get_kst_point():
    points = []
    if PLATFORM_HW == PLATFORM_HISI:
        lb = os.popen('adb shell getprop persist.hisi.keystone.lb').read().strip()
        rb = os.popen('adb shell getprop persist.hisi.keystone.rb').read().strip()
        rt = os.popen('adb shell getprop persist.hisi.keystone.rt').read().strip()
        lt = os.popen('adb shell getprop persist.hisi.keystone.lt').read().strip()
        if len(lb) > 0 and len(rb) > 0 and len(rt) > 0 and len(lt) > 0:
            lb = list(lb.split(','))
            rb = list(rb.split(','))
            rt = list(rt.split(','))
            lt = list(lt.split(','))
            points = list(map(float, lb + rb + rt + lt))
            # print(lb, rb, rt, lt)
            print('ori:', points)
    elif PLATFORM_HW == PLATFORM_AMLOGIC:
        points = os.popen("adb shell getprop persist.vendor.hwc.keystone").read()
        if len(points) > 0:
            source_points = points.strip().split(',')
            source_points = list(map(float, source_points))
            source_points = list(map(int, source_points))
        else:
            print('>>>>>>>>>>>>>>>>>>>> 未获取到投影仪的原始坐标')
            source_points = [0, 0, 1920, 0, 1920, 1080, 0, 1080]
        print('原始坐标 ', source_points)

    return points


def pro_set_kst_point(point):
    for i in range(len(point)):
        if point[i] < 0:
            point[i] = 0
        if i % 2 == 0:
            if point[i] > 1919:
                point[i] = 1919
        if i % 2 == 1:
            if point[i] > 1079:
                point[i] = 1079
    pro_get_kst_point()
    print('set point : ', point)
    if PLATFORM_HW == 0:
        N = 2
        dst = ['lb ', 'rb ', 'rt ', 'lt ']
        sub_list = [point[i:i + N] for i in range(0, len(point), N)]
        print(sub_list)
        for i in range(4):
            cmd0 = 'adb shell setprop persist.hisi.keystone.'
            cmd1 = dst[i]
            cmd2 = ','.join(map(str, sub_list[i]))
            cmd = cmd0 + cmd1 + cmd2
            print(cmd)
            os.system(cmd)

            cmd0 = 'adb shell setprop persist.sys.keystone.'
            cmd1 = dst[i]
            cmd2 = ','.join(map(str, sub_list[i]))
            cmd = cmd0 + cmd1 + cmd2
            print(cmd)
            os.system(cmd)
        cmd = 'adb shell setprop persist.sys.keystone.update true'
        print(cmd)
        os.system(cmd)

    elif PLATFORM_HW == 1:
        # int列表转字符串列表
        point = ','.join(map(str, point))
        print('set point : ', point)
        # cmd = "adb shell setprop persist.vendor.hwc.keystone 0,0,1920,0,1920.1080,0,1080"
        cmd = "adb shell setprop persist.vendor.hwc.keystone "
        cmd = cmd + point
        print('set point : ', cmd)
        os.system(cmd)
        # time.sleep(1)

        cmd0 = 'adb shell am broadcast -a asu.intent.action.SetKstPoint --es point '
        cmd1 = '"' + point + '"'
        cmd = cmd0 + cmd1
        print(cmd)
        os.system(cmd)
    os.system("adb shell service call SurfaceFlinger 1006")
    os.system("adb shell service call SurfaceFlinger 1006")
