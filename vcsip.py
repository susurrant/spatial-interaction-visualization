# -*- coding: utf-8 -*-：

from grid import *
from draw import *
from LL2UTM import LL2UTM_USGS
from style import readDrawingSetting
from func import readGids
import numpy as np

def calcMD(a, n):
    d = np.array([i * 2 * np.pi / n for i in range(n)]) + np.pi / n
    w = np.cos(d - a)
    idx = np.where(w == np.max(w))[0][0]
    return idx, w[idx]

def calcInteraction(flow):
    dx = flow[1][0] - flow[0][0]
    dy = flow[1][1] - flow[0][1]
    d = np.sqrt(dy ** 2 + dx ** 2)
    a = abs(np.arcsin(dy / d))
    if dx > 0:
        if dy < 0:
            a = 2 * np.pi - a
        elif dy == 0:
            a = 0
    elif dx < 0:
        if dy > 0:
            a = np.pi - a
        elif dy < 0:
            a += np.pi
        else:
            a = np.pi
    else:
        if dy > 0:
            a = 0.5 * np.pi
        elif dy < 0:
            a = 1.5 * np.pi
        else:
            a = -1

    return d / 1000.0, a  # return distance (km) and azimuth

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
    '''
    tag5 = 0
    tag3 = 0
    tag2 = 0
    rl = []
    al = []
    for fid in grids[342].outFlow:
        td, ta = calcInteraction(flows[fid])
        idx, tw = calcMD(ta, 6)
        if idx == 5:
            if tag5==4:
                tag5=0
            else:
                tag5+=1
                rl.append(fid)
        if idx == 2:
            if tag2==5:
                tag2=0
            else:
                tag2+=1
                rl.append(fid)
        if idx == 3:
            if tag3 == 3:
                tag3=0
            else:
                tag3+=1
                al.append(fid)
        if idx ==4:
            rl.append(fid)

    for fid in rl:
        grids[342].outFlow.remove(fid)
    for fid in al:
        grids[342].outFlow.append(fid)
    '''

    return grids, flows

# 读取五环内的交互
def readData_Inside(filename, dgids, dnum, minSpeed = 2, maxSpeed = 150):
    flows = {}
    grids = {}
    for gid in dgids:
        grids[gid] = Grid(gid, dnum)

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

                flows[fid] = [(ox, oy), (dx, dy)]

                assert ogid in grids and dgid in grids

                grids[ogid].addOutFlow(fid)
                grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows


# 交互模式可视化
def SIPatterns(dataFileName, dgids, ia, scale, mode, inside=False):
    if inside:
        grids, flows = readData_Inside(dataFileName+'.csv', dgids, ia['dnum'])
        saveFileName = './figure/p_' + dataFileName[10:] + '_' + mode + '_in.jpg'
    else:
        grids, flows = readData(dataFileName + '.csv', dgids, ia['dnum'])
        saveFileName = './figure/p_' + dataFileName[10:] + '_' + mode + '.jpg'

    if mode == 'pm_bs':
        drawPattern_bs(grids, flows, ia, scale, saveFileName)
    elif mode == 'pm_bc':
        drawPattern_bc(grids, flows, ia, saveFileName)


def SIPatterns_sp(fileName, dgids, ia, mode='bs'):
    grids, flows = readData(fileName + '.csv', dgids, ia['dnum'])
    saveFileName = './figure/p_' + fileName[-15:] + '_' + mode + '.jpg'

    if mode == 'pm_bs':
        drawPattern_bs_sp(grids, flows, ia, saveFileName)


# 模式差异可视化
def patternDifference(fileName1, fileName2, dgids, ia, alpha, inside=False):
    if inside:
        grids1, flows1 = readData_Inside(fileName1 + '.csv', dgids, ia['dnum'])
        grids2, flows2 = readData_Inside(fileName2 + '.csv', dgids, ia['dnum'])
        saveFileName = './figure/d_' + fileName1[-15:-4] + '-' + fileName2[-8:] + '_' + str(alpha) + '_in.jpg'
    else:
        grids1, flows1 = readData(fileName1 + '.csv', dgids, ia['dnum'])
        grids2, flows2 = readData(fileName2 + '.csv', dgids, ia['dnum'])
        saveFileName = './figure/d_' + fileName1[-15:-4] + '-' + fileName2[-8:] + '_' + str(alpha) + '.jpg'

    drawDif_fj(grids1, grids2, flows1, flows2, alpha, ia, saveFileName)

# 差异时变
def difVar(fs, dgids, gids, labels, colors, alpha, dnum):
    grids = []
    flows = []
    for fn in fs:
        g, f = readData(fn + '.csv', dgids, dnum)
        grids.append(g)
        flows.append(f)
    gdif = cdif_multi(grids, flows, alpha)
    drawCdifDistribution(gids, gdif, colors, labels)

def drawppp(dataFileName, dgids, ia, scale, mode, inside=False):
    grids, flows = readData(dataFileName + '.csv', dgids, ia['dnum'])
    saveFileName = './figure/p_' + dataFileName[10:] + '_' + mode + '_sss.jpg'
    drawsp(grids, flows, ia, scale, saveFileName)

if __name__ == '__main__':
    # -----------------------------data----------------------------------
    fileNames = ['./data/sj_051316_0105','./data/sj_051316_0509', './data/sj_051316_0913',
                 './data/sj_051316_1317', './data/sj_051316_1721', './data/sj_051316_2101']

    scale = '1km'#'500m'
    mode = 'pm_bs'
    dgids = readGids('./data/5th_rr_gid_'+scale+'.csv')
    ia = readDrawingSetting(mode, scale)

    # -----------------------------drawing--------------------------------
    #drawSingleGlyph(ia)
    SIPatterns(fileNames[3]+'_'+scale, dgids, ia, scale, mode, False) #True 表示只显示五环内的数据
    #SIPatterns_sp(fileNames[0]+'_'+scale, dgids, ia, mode)
    #drawppp(fileNames[3]+'_'+scale, dgids, ia, scale, mode, False)
    #drawglyph342(ia)
    #patternDifference(fileNames[1]+'_'+scale, fileNames[4]+'_'+scale, dgids, ia, 0.7, True)

    if False:
        labels = ['T', 'S', 'C', 'R']
        #gids = [124, 150, 437, 356]    #scale = 1km
        gids = [124, 150, 437, 165]    # scale = 1km   351 qing ta, 165 shi fo ying, 103 fangzhuang
        colors = ['#eaff56', '#44cef6', '#ff461f', '#bddd22']
        difVar([fileNames[i]+'_'+scale for i in [1,0,2,3,4,5]], dgids, gids, labels, colors, 0.7, 6)

    #userScore()