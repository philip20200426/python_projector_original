import Constants


def print_debug(*args, **kwargs):
    if Constants.LOG_ENABLE:
        print('99999999999999999999999999999999999999999')
        print(*args, **kwargs)
    else:
        pass
