import logging

import Constants
# import logging.config
#
# # 1. Logger
# ## 1.1 实例化 Logger 对象
# # logger = logging.getLogger(name=__name__)
# logger = logging.getLogger()
# ## 1.2 设置 Logger 对象的日志级别
# logger.setLevel(level=logging.DEBUG)
#
# # 2. Handler
# ## 2.1 创建 Handler 对象
# stream_handler = logging.StreamHandler()
# file_handler = logging.FileHandler(filename="log/temp.log", mode='a')
#
# ## 2.2 设置Handler级别
# stream_handler.setLevel(logging.WARNING)
# file_handler.setLevel(logging.INFO)
#
# ## 2.3 将 Handler 添加到 Logger 中
# logger.addHandler(hdlr=stream_handler)
# logger.addHandler(hdlr=file_handler)
#
# # 3. Formatter
# ## 3.1 创建格式器
# formatter_full = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - [%(lineno)d] %(message)s",
#                                    datefmt="%Y-%m-%d %H:%M:%S")  # 复杂的格式
# formatter_simple = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")  # 简单的格式
#
# ## 3.2 应用Formatter(我们一般只给Handler添加Formatter, Logger 就不设置了)
# stream_handler.setFormatter(formatter_simple)
# file_handler.setFormatter(formatter_full)

# 1. 加载配置文件
# logging.config.fileConfig("res/log.cfg")
# # 2. 创建 logger
# logger = logging.getLogger()

def print_debug(*args, **kwargs):
    # print('>>>>>>>>>>>>>>>>>>>>>>>!!!!!!!!!!!!!!!!!!!!!!!!')
    # logger.debug("这是一条[debug]日志!")
    # logger.info("这是一条[info]日志!")
    # logger.warning("这是一条[warning]日志!")
    # logger.error("这是一条[error]日志!")
    #
    # logger.critical("这是一条[critical]日志!")
    if Constants.LOG_ENABLE:
        print(*args, **kwargs)
        # logger.error(args)
    else:
        pass
