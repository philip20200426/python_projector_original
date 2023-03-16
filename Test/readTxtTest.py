

f = open('LGM_DATA_20230313_1629.txt')
f1 = open('CXD3554_LGM.txt')
line = f.readline().strip() #读取第一行
line = f1.readline().strip() #读取第一行
#txt=[]
#txt.append(line)
count = 0
while line:  # 直到读取完文件
   line = f.readline().strip()  # 读取一行文件，包括换行符
   data = line.split(':')
   line1 = f1.readline().strip()  # 读取一行文件，包括换行符
   data1 = line1.split(':')
   if data[0].upper() != data1[0].upper():
      print(data[0].upper(), data1[0].upper())
   count += 1
   print(count)
   #txt.append(line)
f.close()  # 关闭文件
f1.close()  # 关闭文件