import os

a = list(range(119,150))
print(a)

kms = []
for i in a:
    k = str(i)
    uc_name = 'uc' + k
    kms.append(uc_name)
print(kms)
newpath = r'G:\Bộ Nội vụ\Test case\LGSP\test_data_service'
for km in kms:
    path = newpath + '\\' + km
    if not os.path.exists(path):
        os.makedirs(path)

     
