import copy
import os
test = {}
test2 = []
asdf = True
fdsa = [1, 2, 3, 4, 5]

'''
dsaf = copy.copy(fdsa)
for i in dsaf:
    del (fdsa[0])
    print(i)
# print(fdsa)
'''

dir = "C:/Users/seosangwon/Documents/백업 테스트용 폴더/Adobe Desktop Service/FBP_2022-08-11_22-09-34"
print(os.listdir(dir))
count = 0
for (root, directories, files) in os.walk(dir):
    '''
    for d in directories:
        dir = os.path.join(root, d)
        print(dir)
'''
    for file in files:
        # file_path = os.path.join(root, file)
        count = count + 1
print(count)