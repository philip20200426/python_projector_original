import Constants


def print_debug(*args, **kwargs):
    if Constants.LOG_ENABLE:
        print(*args, **kwargs)
    else:
        pass
