# import pandas as pd
#
# # 读取CSV文件
# data = pd.read_csv('c2-2.2-1D LUT 202310231557.csv')
#
# # 删除指定行
# data = data.drop(index=1023)
#
# # 保存修改后的数据到新的CSV文件
# data.to_csv('c2-2.2-1D_LUT_202310231557.csv', index=False)

import csv

# 读取CSV文件
with open('c2-2.2-1D LUT 202310231557.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    print(len(data))
    print(data[1023])
    for i in range(3, len(data), 3):
        #print(i, data[i])
        del data[i]
        # if i%4 != 0:
        #     print(i)
        #     del data[i]

# for i in range(1, 1000):
#     # 删除指定行
#     del data[i]
    # print(i)
    # if i%4 != 0:
    #     # print(i)
    #     del data[i]

# 保存修改后的数据到新的CSV文件
with open('c2-2.2-1D_LUT_202310231557.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
