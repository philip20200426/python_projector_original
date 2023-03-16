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
