
import csv

grids = {}
for i in range(361):
    grids[i] = 0

with open('./data/sj_1600msq_051316_1721.csv', 'r') as f:
    f.readline()
    while True:
        line1 = f.readline().strip()
        if line1:
            sl1 = line1.split(',')
            sl2 = f.readline().strip().split(',')
            if sl1[1] == '0':
                continue
            gid = int(sl1[-1])
            grids[gid] += 1
        else:
            break

with open('sta.csv', 'w', newline='') as f:
    sheet = csv.writer(f)
    sheet.writerow(['gid', 'c'])
    for gid in grids:
        sheet.writerow([gid, grids[gid]])