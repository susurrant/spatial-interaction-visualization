# -*- coding: utf-8 -*-：


from sklearn.cluster import KMeans
import operator
import numpy as np
import pysal as ps

# kmeans classifier
def kmeans(dn, cNum):
    X = np.sort(dn).reshape((-1, 1))
    k = KMeans(n_clusters=cNum, random_state=0).fit(X)
    labels = []
    for l in k.labels_:
        if l not in labels:
            labels.append(l)
    return k, labels

def fisher_jenks(d, cNum):
    X = np.array(d).reshape((-1, 1))
    fj = ps.esda.mapclassify.Fisher_Jenks(X, cNum)
    meanV = []
    for i in range(cNum):
        meanV.append(np.mean(X[np.where(i == fj.yb)]))
    return fj.bins, meanV

# compute row and column indexes
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


# compute edge point coordinates of a regular hexagon
def computeCo_hexagon(cenx, ceny, gridWidth):
    dx = gridWidth*np.cos(np.pi/3)
    dy = gridWidth*np.sin(np.pi/3)
    p = [(cenx+gridWidth, ceny), (cenx+dx, ceny-dy), (cenx-dx, ceny-dy), (cenx-gridWidth, ceny),
         (cenx-dx, ceny+dy), (cenx+dx, ceny+dy), (cenx+gridWidth, ceny)]

    co = []
    for i in range(6):
        co.append([cenx, ceny, p[i][0], p[i][1], p[i+1][0], p[i+1][1]])
    return co


# compute the coordinate offset of edge points from the center of a hexagon
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


# magnitude difference
def mdif(m1, m2):
    if operator.eq(m1, m2):
        return 0
    n = 0
    for n1, n2 in zip(m1, m2):
        n += abs(n2-n1)
    return n


# distance difference
def ddif(d1, d2, m1, m2):
    if operator.eq(d1, d2):
        return 0
    n = []
    w = []
    for i in range(len(d1)):
        w.append(abs(m2[i]-m1[i]))
        n.append(abs(d2[i]-d1[i]))
    if sum(w)==0:
        return sum(n)
    else:
        s = 0
        for i, tw in enumerate(w):
            s += tw*n[i]
        return float(s)/sum(w)


# comprehensive difference between two patterns
def cdif(grids1, grids2, flows1, flows2, alpha):
    d_difN = {}
    d_difD = {}
    gid_nodata = set()
    maxD = 0
    maxN = 0
    minD = float('inf')
    minN = float('inf')

    for gid in grids1:
        grids1[gid].calcOutAggregation(flows1)
        grids2[gid].calcOutAggregation(flows2)
        if sum(grids1[gid].wm) ==0 and sum(grids2[gid].wm)==0:
            gid_nodata.add(gid)
            continue
        difN = mdif(grids1[gid].wm, grids2[gid].wm)
        difD = ddif(grids1[gid].wd, grids2[gid].wd, grids1[gid].wm, grids2[gid].wm)
        d_difN[gid] = difN
        d_difD[gid] = difD
        minN = min(minN, difN)
        maxN = max(maxN, difN)
        minD = min(minD, difD)
        maxD = max(maxD, difD)

    dif = {}
    for gid in d_difN:
        dif[gid] = alpha*(d_difN[gid]-minN)/(maxN-minN) + (1-alpha)*(d_difD[gid]-minD)/(maxD-minD)

    return dif, gid_nodata


# comprehensive difference between several patterns and a specific pattern
def cdif_multi(lgrids, lflows, alpha):
    d_difN = {}
    d_difD = {}
    tNum = (len(lgrids) - 1)
    for gid in lgrids[0]:
        d_difN[gid] = [0] * tNum
        d_difD[gid] = [0] * tNum
    maxD = 0
    maxN = 0
    minD = float('inf')
    minN = float('inf')

    for i in range(tNum+1):
        for g in lgrids[i]:
            lgrids[i][g].calcOutAggregation(lflows[i])

    for gid in lgrids[0]:
        for i in range(1, tNum+1):
            difN = mdif(lgrids[0][gid].wm, lgrids[i][gid].wm)
            difD = ddif(lgrids[0][gid].wd, lgrids[i][gid].wd, lgrids[0][gid].wm, lgrids[i][gid].wm)
            d_difN[gid][i-1] = difN
            d_difD[gid][i-1] = difD
            minN = min(minN, difN)
            maxN = max(maxN, difN)
            minD = min(minD, difD)
            maxD = max(maxD, difD)

    dif = {}
    for gid in lgrids[0]:
        dif[gid] = [0] * tNum
        for i in range(tNum):
            dif[gid][i] = alpha*(d_difN[gid][i]-minN)/(maxN-minN) + (1-alpha)*(d_difD[gid][i]-minD)/(maxD-minD)

    return dif


# read grid id list
def readGids(fileName):
    dgids = set()
    with open(fileName, 'r') as f:
        lines = f.readlines()
        del lines[0]
        for line in lines:
            sl = line.strip().split(',')
            dgids.add(int(sl[-1]))
    return dgids


def processGrids_kmeans(grids, flows, ia):
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


def processGrids_fj(grids, flows, ia):
    mag = []
    dis = []
    for gid in grids:
        grids[gid].cenx, grids[gid].ceny = computeCen(gid, ia)
        grids[gid].calcOutAggregation(flows)
        mag.extend(grids[gid].wm)
        dis.extend(grids[gid].wd)

    nk, nl = fisher_jenks(mag, ia['k_m'])
    dk, dl = fisher_jenks(dis, ia['k_d'])

    for gid in grids:
        uptos = [np.where(value <= nk)[0] for value in grids[gid].wm]
        for i in [x.min() if x.size > 0 else len(nk) - 1 for x in uptos]:
            grids[gid].mcolor.append(ia['c_m'][i])

        uptos = [np.where(value <= dk)[0] for value in grids[gid].wd]
        for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
            grids[gid].dcolor.append(ia['c_d'][i])