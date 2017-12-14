# -*- coding: utf-8 -*-：

from grid import *
from draw import *
from LL2UTM import LL2UTM_USGS
from style import readDrawingSetting

# 读取数据
def readData(filename, dgids, dnum, minSpeed = 2, maxSpeed = 150):
    flows = {}
    grids = {}
    for gid in dgids:
        grids[gid] = Grid(gid, dnum)

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if float(sl[-2]) < minSpeed or float(sl[-2]) > maxSpeed:
                    continue

                fid = int(sl[-4])
                gid = int(sl[-1])

                if fid not in flows:
                    flows[fid] = [(), ()]

                x, y = LL2UTM_USGS(float(sl[-5]), float(sl[-6]))
                if sl[-3] == '1':
                    flows[fid][0] = (x, y)
                    if gid in dgids:
                        grids[gid].addOutFlow(fid)
                elif sl[-3] == '0':
                    flows[fid][1] = (x, y)
                    if gid in dgids:
                        grids[gid].addInFlow(fid)
            else:
                break

    return grids, flows

# 读取五环内的交互
def readData_Inside(filename, dnum, minSpeed = 2, maxSpeed = 150):
    flows_co = {}
    grids = {}

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            if line1:
                line2 = f.readline().strip()
                sl1 = line1.split(',')
                sl2 = line2.split(',')
                if int(sl1[1]) == 0 or int(sl2[1]) == 0:
                    continue
                if float(sl1[-2]) < minSpeed or float(sl1[-2]) > maxSpeed:
                    continue

                fid = int(sl1[-4])
                ogid = int(sl1[-1])
                dgid = int(sl2[-1])

                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))
                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))

                flows_co[fid] = [(ox, oy), (dx, dy)]

                if ogid not in grids:
                    grids[ogid] = Grid(ogid, dnum)
                if dgid not in grids:
                    grids[dgid] = Grid(dgid, dnum)

                grids[ogid].addOutFlow(fid)
                grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows_co

# 读取要绘制的网格编号
def readGids(fileName):
    dgids = set()
    with open(fileName, 'r') as f:
        lines = f.readlines()
        del lines[0]
        for line in lines:
            sl = line.strip().split(',')
            dgids.add(int(sl[-1]))
    return dgids

# 交互模式可视化
def drawSIPattern(fileName, dgids, dnum, ia, mode='bs', inside=False):
    if inside:
        grids, flows = readData_Inside(fileName+'.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '_' + mode + '_in.jpg'
    else:
        grids, flows = readData(fileName + '.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '_' + mode + '.jpg'

    if mode == 'bs':
        drawPattern_bs(grids, flows, dnum, ia, saveFileName)
    elif mode == 'bc':
        drawPattern_bc(grids, flows, dnum, ia, saveFileName)


# 模式差异可视化
def drawDifference(fileName1, fileName2, dgids, dnum, ia, alpha):
    ia['legendWidth'] = 15
    grids1, flows1 = readData(fileName1 + '.csv', dgids, dnum)
    grids2, flows2 = readData(fileName2 + '.csv', dgids, dnum)
    saveFileName = './figure/d_' + fileName1[-15:-4]+'-'+fileName2[-8:]+'_'+str(alpha)+'.jpg'
    drawCdif_Kmeans(grids1, grids2, flows1, flows2, alpha, ia, saveFileName)

# 差异时变
def drawDifVar(fs, dgids, gids, labels, colors, alpha, dnum):
    grids = []
    flows = []
    for fn in fs:
        g, f = readData(fn + '.csv', dgids, dnum)
        grids.append(g)
        flows.append(f)
    gdif = cdif_multi(grids, flows, alpha)
    drawCdifDistribution(gids, gdif, colors, labels)



if __name__ == '__main__':
    # -----------------------------data----------------------------------
    fileNames = ['./data/sj_051316_0105','./data/sj_051316_0509', './data/sj_051316_0913',
                 './data/sj_051316_1317', './data/sj_051316_1721', './data/sj_051316_2101']

    scale = '_1km'
    mode = 'bs'
    dnum = 6
    dgids = readGids('./data/5th_rr_gid'+scale+'.csv')
    ia = readDrawingSetting(mode, scale[1:])

    # -----------------------------drawing--------------------------------
    #drawGridSymbol_hexagon(ia['c_d'])False

    drawSIPattern(fileNames[1]+scale, dgids, dnum, ia, mode,  False) #True 表示只显示五环内的数据

    #drawDifference(fileNames[1]+scale, fileNames[4]+scale, dgids, dnum, ia, 0.7)

    if False:
        labels = ['T', 'S', 'C', 'R']
        gids = [487, 563, 800, 1455]   #scale = 500m
        gids = [124, 150, 437, 356]    #scale = 1km
        colors = ['#eaff56', '#44cef6', '#ff461f', '#bddd22']
        drawDifVar([fileNames[i]+scale for i in [1,0,2,3,4,5]], dgids, gids, labels, colors, 0.7, dnum)