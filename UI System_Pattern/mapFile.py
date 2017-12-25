#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

import sys
sys.path.append('../')
from grid import *
from LL2UTM import LL2UTM_USGS
from func import kmeans, computeCen, readGids

def readData(filename, dgids, dnum, minSpeed=2, maxSpeed=150):
    grids = {}
    flows = {}

    for gid in dgids:
        grids[gid] = Grid(gid, dnum)

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            line2 = f.readline().strip()
            if line1 and line2:
                sl1 = line1.split(',')
                sl2 = line2.split(',')

                if float(sl1[-2]) < minSpeed or float(sl1[-2]) > maxSpeed:
                    continue
                if sl1[1] == '0' and sl2[1] == '0':
                    continue

                fid = int(sl1[-4])
                ogid = int(sl1[-1])
                dgid = int(sl2[-1])
                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))
                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))

                if fid not in flows:
                    flows[fid] = Flow(fid, [(ox, oy), (dx, dy)], ogid, dgid)

                if sl1[1] == '1':
                    grids[ogid].addOutFlow(fid)

                if sl2[1] == '1':
                    grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows

def processGrids(grids, flows, ia):
    mag = []
    dis = []
    for g in grids:
        grids[g].calcOutAggregation(flows)
        for tm in grids[g].wm:
            mag.append(tm)
        for td in grids[g].wd:
            dis.append(td)

    nk, nl = kmeans(mag, ia['k_m'])
    dk, dl = kmeans(dis, ia['k_d'])

    for gid in grids:
        grids[gid].cenx, grids[gid].ceny = computeCen(gid, ia)
        for i in range(ia['dnum']):
            grids[gid].mcolor.append(ia['c_m'][nl.index(nk.predict(grids[gid].wm[i]))])
            grids[gid].dcolor.append(ia['c_d'][dl.index(dk.predict(grids[gid].wd[i]))])


def relate2data(fileName, ia):
    dgids = readGids('../data/5th_rr_gid' + ia['scale'] + '.csv')
    grids, flows = readData(fileName+ ia['scale'] + '.csv', dgids, ia['dnum'])
    processGrids(grids, flows, ia)
    return grids, flows


