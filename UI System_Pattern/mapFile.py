#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

import sys
sys.path.append('../')
from grid import *
from LL2UTM import LL2UTM_USGS
from func import computeCen, readGids, computeCo, fisher_jenks
import numpy as np


def set_glyph_color(grids, flows, ia):
    for gid in grids:
        grids[gid].reset()
        grids[gid].cenx, grids[gid].ceny = computeCen(gid, ia)

    mag = []
    dis = []
    for gid in grids:
        grids[gid].calcOutAggregation(flows)
        mag.extend(grids[g].out_wm)
        dis.extend(grids[g].out_wd)

    nk, nl = fisher_jenks(mag, ia['k_m'])
    dk, dl = fisher_jenks(dis, ia['k_d'])

    for gid in grids:
        uptos = [np.where(value <= nk)[0] for value in grids[gid].out_wm]
        for i in [x.min() if x.size > 0 else len(nk) - 1 for x in uptos]:
            grids[gid].out_mcolor.append(ia['c_m'][i])

        uptos = [np.where(value <= dk)[0] for value in grids[gid].out_wd]
        for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
            grids[gid].out_dcolor.append(ia['c_d'][i])

    mag = []
    dis = []
    for gid in grids:
        grids[gid].calcInAggregation(flows)
        mag.extend(grids[g].in_wm)
        dis.extend(grids[g].in_wd)

    nk, nl = fisher_jenks(mag, ia['k_m'])
    dk, dl = fisher_jenks(dis, ia['k_d'])

    for gid in grids:
        uptos = [np.where(value <= nk)[0] for value in grids[gid].in_wm]
        for i in [x.min() if x.size > 0 else len(nk) - 1 for x in uptos]:
            grids[gid].in_mcolor.append(ia['c_m'][i])

        uptos = [np.where(value <= dk)[0] for value in grids[gid].in_wd]
        for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
            grids[gid].in_dcolor.append(ia['c_d'][i])


def set_glyph_coordinate(grids, flows, ia):
    # coordinate calculation - center
    for gid in grids:
        grids[gid].cenx, grids[gid].ceny = computeCen(gid, ia)

    # coordinate calculation - grids
    oxs, oys = computeCo(ia['gridWidth'], ia['dnum'] // 6)
    ixs, iys = computeCo(ia['gridWidth'] * ia['area_ratio'], ia['dnum'] // 6)
    fxs, fys = computeCo(ia['gridWidth'] + ia['margin'], ia['dnum'] // 6)
    for gid in grids:
        cx = grids[gid].cenx
        cy = grids[gid].ceny
        for i in range(ia['dnum']):
            grids[gid].oco.append([cx, cy, cx + ixs[i], cy + iys[i], cx + ixs[i + 1], cy + iys[i + 1]])
            grids[gid].ico.append([cx + ixs[i], cy + iys[i], cx + oxs[i], cy + oys[i], cx + oxs[i + 1], cy + oys[i + 1],
                                   cx + ixs[i + 1], cy + iys[i + 1]])
            grids[gid].border.append(cx + fxs[i])
            grids[gid].border.append(cy + fys[i])
        grids[gid].border.append(cx + fxs[0])
        grids[gid].border.append(cy + fys[0])

    # coordinate calculation - flows
    for fid in flows:
        if np.random.random() < ia['p']:
            flows[fid].select_tag = True
        co = flows[fid].co
        ox = (co[0][0] - ia['xoff']) / ia['trans_scale']
        oy = 800 - (co[0][1] - ia['yoff']) / ia['trans_scale']
        dx = (co[1][0] - ia['xoff']) / ia['trans_scale']
        dy = 800 - (co[1][1] - ia['yoff']) / ia['trans_scale']
        flows[fid].co = [(ox, oy), (dx, dy)]


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


def relate2data(filenames, ia):
    dgids = readGids('../data/5th_rr_gid_1km.csv')
    grid_data = []
    flow_data = []
    for fn in filenames:
        grids, flows = readData(fn, dgids, ia['dnum'])
        set_glyph_color(grids, flows, ia)
        set_glyph_coordinate(grids, flows, ia)
        grid_data.append(grids)
        flow_data.append(flows)

    return grid_data, flow_data