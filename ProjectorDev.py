import os
import time

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


def pro_show_pattern_af():
    os.system('adb shell am broadcast -a asu.intent.action.ShowBlankPattern')


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
    location = pro_get_motor_position()
    ret_steps = pro_motor_forward(direction, steps)
    while abs(ret_steps - steps) > STEPS_GAP:
        if pro_motor_forward(direction, steps) < STEPS_GAP*2:
            print('>>>>>>>>>>>>>>>>>>>> 马达到头了,当前位置:' + str(pro_get_motor_position()) + ',实际执行步数:' + str(ret_steps))
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
            print('>>>>>>>>>>>>>>>>>>>> 当前位置:' + str(pro_get_motor_position()) + ',实际执行步数:' + str(ret_steps))
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
        os.system("adb shell am broadcast -a asu.intent.action.Motor --es operate 5 --ei value 3000")
    else:
        os.system('adb shell "echo 5 3000 > /sys/devices/platform/customer-AFmotor/step_set"')


def motor_forward(dir, steps):
    if PRO_SYS_APP:
        cmd1 = 'adb shell am broadcast -a asu.intent.action.Motor --es operate '
        cmd2 = str(dir)
        cmd3 = ' --ei value '
        cmd4 = str(int(steps))
        cmd = cmd1 + cmd2 + cmd3 + cmd4
        print(cmd)
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
