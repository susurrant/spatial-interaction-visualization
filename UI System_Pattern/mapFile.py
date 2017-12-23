#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

from grid import *
from LL2UTM import LL2UTM_USGS
from sklearn.cluster import KMeans
import operator
import numpy as np

def readData(filename, dgids, dnum, minSpeed=2, maxSpeed=150):
    flows_co = {}
    flows_id = {}
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

                if fid not in flows_co:
                    flows_co[fid] = [(), ()]
                    flows_id[fid] = [-1, -1]

                x, y = LL2UTM_USGS(float(sl[-5]), float(sl[-6]))
                if sl[-3] == '1':
                    flows_co[fid][0] = (x, y)
                    flows_id[fid][0] = gid
                elif sl[-3] == '0':
                    flows_co[fid][1] = (x, y)
                    flows_id[fid][1] = gid
            else:
                break

    for fid in flows_id:
        og = flows_id[fid][0]
        dg = flows_id[fid][1]

        if og in dgids:
            grids[og].addOutFlow(fid)
            if dg not in grids[og].toGrid:
                if dg == 0:
                    grids[og].toGrid[dg] = []
                else:
                    grids[og].toGrid[dg] = 0
            if dg == 0:
                grids[og].toGrid[dg].append(flows_co[fid])
            else:
                grids[og].toGrid[dg] += 1

        if dg in dgids:
            grids[dg].addInFlow(fid)
            if og not in grids[dg].fromGrid:
                if og == 0:
                    grids[dg].fromGrid[og] = []
                else:
                    grids[dg].fromGrid[og] = 0
            if og == 0:
                grids[dg].fromGrid[og].append(flows_co[fid])
            else:
                grids[dg].fromGrid[og] += 1

    return grids, flows_co

# kmeans classifier
def kmeans(dn, cNum):
    n = sorted(dn, key = operator.itemgetter(0), reverse = False)
    X = np.array(n)
    k = KMeans(n_clusters=cNum, random_state=0).fit(X)
    labels = []
    for l in k.labels_:
        if l not in labels:
            labels.append(l)
    return k, labels

def computeRC(gid, hexParm):
    if gid < hexParm[1]:
        y = int(gid/hexParm[0])*2
        x = (gid % hexParm[0])*2 + 1
    else:
        y = int((gid-hexParm[1])/hexParm[0])*2 + 1
        x = ((gid-hexParm[1]) % hexParm[0])*2
    return y, x

# compute central point coordinates
def computeCen(gid, ia):
    hexParm = ia['hexParm']
    totalY = computeRC(hexParm[1]-1, hexParm)[0] + 2
    y, x = computeRC(gid, hexParm)

    a = (ia['gridWidth'] + ia['margin']) * 3 / 2
    b = (ia['gridWidth'] + ia['margin']) * np.sqrt(3) / 2
    cenx = ia['ox'] + (x - ia['xoffset'] + 1) * a
    ceny = ia['oy'] + (totalY - y - ia['yoffset'] + 1) * b
    return cenx, ceny

def computeCo(gridWidth, n):
    dx = gridWidth * np.cos(np.pi / 3)
    dy = gridWidth * np.sin(np.pi / 3)
    a = np.array(range(0, n))*np.pi/(3*n)
    x = dx - gridWidth * np.sin(a) / np.sin(2*np.pi/3 - a)
    y = np.array([-dy] * len(a))
    xs = []
    ys = []
    for rotate in [np.pi/3, 0, 5*np.pi/3, 4*np.pi/3, np.pi, 2*np.pi/3]:
        xs.extend(np.round(x * np.cos(rotate) - y * np.sin(rotate)))
        ys.extend(np.round(x * np.sin(rotate) + y * np.cos(rotate)))

    xs.append(xs[0])
    ys.append(ys[0])
    return xs, ys

def computeCo_hexagon(cenx, ceny, gridWidth):
    dx = gridWidth*np.cos(np.pi/3)
    dy = gridWidth*np.sin(np.pi/3)
    p = [(cenx+gridWidth, ceny), (cenx+dx, ceny-dy), (cenx-dx, ceny-dy), (cenx-gridWidth, ceny),
         (cenx-dx, ceny+dy), (cenx+dx, ceny+dy), (cenx+gridWidth, ceny)]

    co = []
    for i in range(6):
        co.append([cenx, ceny, p[i][0], p[i][1], p[i+1][0], p[i+1][1]])
    return co

def processGrids(grids, flows_co, ia):
    mag = []
    dis = []
    gm = []
    for g in grids:
        grids[g].calcOutAggregation(flows_co)
        for tm in grids[g].wm:
            mag.append([tm, 0])
        for td in grids[g].wd:
            dis.append([td, 0])
        for tm in grids[g].toGrid.values():
            if not isinstance(tm, list):
                gm.append([tm, 0])
        for i in range(len(grids[g].toOutFlowCo)):
            gm.append([1, 0])

    nk, nl = kmeans(mag, ia['k_m'])
    dk, dl = kmeans(dis, ia['k_d'])
    gk, gl = kmeans(gm, ia['k_m'])

    for gid in grids:
        grids[gid].cenx, grids[gid].ceny = computeCen(gid, ia)
        if ia['scale'] == '_1km':
            grids[gid].calcOutFlow_outside(ia['gridWidth']+ia['margin'])
        elif ia['scale'] == '_500m':
            grids[gid].calcOutFlow_outside((ia['gridWidth']+ia['margin'])*2)

        for i in range(ia['dnum']):
            grids[gid].mcolor.append(ia['c_m'][nl.index(nk.predict([[grids[gid].wm[i], 0]])[0])])
            grids[gid].dcolor.append(ia['c_d'][dl.index(dk.predict([[grids[gid].wd[i], 0]])[0])])

        for tgid in grids[gid].toGrid:
            if tgid in grids:
                grids[gid].width[tgid] =(gl.index(gk.predict([[grids[gid].toGrid[tgid], 0]])[0])+1)*0.5

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


def relate2data(fileName, ia):
    dgids = readGids('../data/5th_rr_gid' + ia['scale'] + '.csv')
    grids, flows_co = readData(fileName+ ia['scale'] + '.csv', dgids, ia['dnum'])
    processGrids(grids, flows_co, ia)
    return grids


