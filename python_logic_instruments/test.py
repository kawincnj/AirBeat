a = 0.010313
count = 0
for i in (str(a)).split('.')[1]:
    count += 1
    if i != '0':
        print(count)
        break
print(10 ** (-count))