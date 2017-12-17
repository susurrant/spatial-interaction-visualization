# -*- coding: utf-8 -*-：
"""
Reference: Spatial generalisation and aggregation of massive movement data - Andrienko, Natalia and Andrienko, Gennady
Implemented by Xin Yao
"""

import csv, time
import numpy as np
from LL2UTM import *


class Point(object):
    def __init__(self, x, y, pid):
        self.x = x
        self.y = y
        self.pid = pid
        self.rid = -1


class Grid(object):
    def __init__(self, gid):
        self.gid = gid
        self.groups = []


class Group(object):
    def __init__(self, cenx=-1, ceny=-1):
        self.pts = []
        self.cenx = cenx
        self.ceny = ceny

    def calCentroid(self):
        self.cenx, self.ceny = np.mean(np.array(self.pts), axis=0)

    def addPt(self, p, recalc_cen):
        self.pts.append(p)
        if recalc_cen:
            self.calCentroid()


def get_closest_centroid(p, R, max_radius):
    min_dis = float('inf')
    c = -1
    for i, g in enumerate(R):
        dis = np.sqrt((p.x-g.cenx)**2+(p.y-g.ceny)**2)
        if dis <= max_radius and dis < min_dis:
            min_dis = dis
            c = i
    return c


def put_in_proper_group(p, R, max_radius):
    c = get_closest_centroid(p, R, max_radius)
    if c == -1:
        R.append(Group())
    R[c].addPt((p.x, p.y), True)


# decorator: compute time cost
def timer(func):
    def wrapper(*args, **kw):
        startTime = time.clock()
        callback =  func(*args, **kw)
        print('Func: %s: %.3f mins' % (func.__name__, (time.clock() - startTime) / 60.0))
        return callback
    return wrapper


@timer
def redistribute_points(P, R):
    print('redistribute points...')
    for g in R:
        g.pts = []

    for p in P:
        c = get_closest_centroid(p, R, float('inf'))
        assert c != -1
        R[c].addPt((p.x, p.y), False)
        p.rid = c


def processData(sl, P, R, max_radius):
    x, y = LL2UTM_USGS(float(sl[5]), float(sl[4]))
    p = Point(x, y, int(sl[3]))
    P.append(p)
    put_in_proper_group(p, R, max_radius)


@timer
def pointGroup(data_file, max_radius):
    print('group points...')
    R = []
    P = []
    with open(data_file, 'r') as f:
        f.readline()
        count = 0
        st = time.clock()
        while True:
            if count % 20000 == 0:
                print('   %d: %.2f mins' % (count, (time.clock() - st) / 60.0))
                st = time.clock()
            count += 1

            line1 = f.readline().strip()
            line2 = f.readline().strip()
            if line1 and line2:
                sl1 = line1.split(',')
                sl2 = line2.split(',')
                if sl1[1] == '0' or sl2[1] == '0':
                    continue
                processData(sl1, P, R, max_radius)
                processData(sl2, P, R, max_radius)
            else:
                break

    redistribute_points(P, R)
    return R
    #return optimize(P, R, max_radius)

@timer
def optimize(P, R, max_radius):
    print('Optimize groups...')
    glist = []
    mDens = 0
    for i, g in enumerate(R):
        medXY = np.mean(np.array(g.pts), axis=0)
        dis = np.sqrt(np.sum((np.array(g.pts)-medXY)**2, axis=1))
        dens = len(g.pts)/np.mean(dis)**2
        glist.append([dens, g.pts[np.argmin(dis)], i])
        mDens += dens
    mDens /= len(R)
    glist.sort(key=lambda x: x[0], reverse=True)

    newR = []
    for dens, pMed, _ in glist:
        if dens < mDens:
            break
        g = Group()
        g.cenx, g.ceny = pMed
        newR.append(g)

    for _, _, i in glist:
        for p in R[i].pts:
            put_in_proper_group(Point(p[0], p[1], -1), newR, max_radius)

    redistribute_points(P, newR)

    return newR


def outPut(R, save_fname):
    print('output results...')
    with open(save_fname, 'w', newline='') as f:
        sheet = csv.writer(f)
        sheet.writerow(['rid', 'x', 'y'])
        for i, g in enumerate(R):
            lat, lon = UTM2LL_USGS(g.cenx, g.ceny)
            sheet.writerow([i, lon, lat])


if __name__ == '__main__':
    data_file = './data/sj_2kmsq_051316_1721.csv'
    max_radius = 2000
    R = pointGroup(data_file, max_radius)
    outPut(R, './data/group_2kmsq_051316_1721_r2km.csv')
