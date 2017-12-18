# -*- coding: utf-8 -*-：
"""
Reference: Spatial generalisation and aggregation of massive movement data - Andrienko, Natalia and Andrienko, Gennady
Implemented by Xin Yao
"""

import csv, time
import numpy as np
from LL2UTM import *


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rid = -1


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
        print('Func- %s: %.3f mins' % (func.__name__, (time.clock() - startTime) / 60.0))
        return callback
    return wrapper


@timer
def redistribute_points(P, R):
    print('redistribute points...')
    for g in R:
        g.pts = []

    for pid in P:
        c = get_closest_centroid(P[pid], R, float('inf'))
        assert c != -1
        R[c].addPt((P[pid].x, P[pid].y), False)
        P[pid].rid = c


def processData(sl, P, R, max_radius):
    x, y = LL2UTM_USGS(float(sl[5]), float(sl[4]))
    p = Point(x, y)
    P[int(sl[3])] = p
    put_in_proper_group(p, R, max_radius)


@timer
def pointGroup(data_file, max_radius):
    print('group points...')
    R = []
    P = {}
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

    return optimize(P, R, max_radius)

@timer
def optimize(P, R, max_radius):
    print('optimize groups...')
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
            put_in_proper_group(Point(p[0], p[1]), newR, max_radius)

    redistribute_points(P, newR)

    return P, newR


@timer
def outPut(P, R, data_file, save_zone_file, save_data_file):
    print('output results...')
    with open(save_zone_file, 'w', newline='') as f:
        sheet = csv.writer(f)
        sheet.writerow(['rid', 'x', 'y'])
        for i, g in enumerate(R):
            sheet.writerow([i, g.cenx, g.ceny])

    with open(save_data_file, 'w', newline='') as f:
        sheet = csv.writer(f)
        with open(data_file, 'r') as rf:
            header = rf.readline().strip().split(',')
            sheet.writerow(header)
            while True:
                line1 = rf.readline().strip()
                line2 = rf.readline().strip()
                if line1 and line2:
                    sl1 = line1.split(',')
                    sl2 = line2.split(',')

                    if sl1[1] != '0' and sl2[1] != '0':
                        sl1[-1] = P[int(sl1[3])].rid
                        sl2[-1] = P[int(sl2[3])].rid
                    else:
                        sl1[-1] = -1
                        sl2[-1] = -1
                    sheet.writerow(sl1)
                    sheet.writerow(sl2)
                else:
                    break


if __name__ == '__main__':
    data_file = './data/sj_051316_1721_5rr.csv'
    max_radius = 3000
    P, R = pointGroup(data_file, max_radius)
    outPut(P, R, data_file, './data/group_051316_1721_r3km.csv', data_file[:-4]+'_gp.csv')
