import json
import os


def get_para(dir_name, key_pri, key_sec=''):
    res = -1
    if os.path.isfile(dir_name):
        file = open(dir_name, )
        dic = json.load(file)
        if len(dic) > 0:
            if key_pri in dic.keys():
                if key_sec != '' and key_sec in dic[key_pri].keys():
                    res = dic[key_pri][key_sec]
                else:
                    res = dic[key_pri]
            else:
                print('{}不存在!!!'.format(key_pri))
        else:
            print('{}文件是空的!!!'.format(dir_name))
        file.close()
    else:
        print('{}不存在!!!'.format(dir_name))
    return res
