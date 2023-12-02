flag = True


def print_debug(*args, **kwargs):
    if flag:
        print(*args, **kwargs)
    else:
        pass
