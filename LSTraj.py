# -*- coding: utf-8 -*-：

from func import readGids, computeRC, fisher_jenks, computeCo, computeCen
from PIL import Image, ImageDraw, ImageFont
from style import readDrawingSetting
import numpy as np

class Grid(object):
    def __init__(self, gid, dnum):
        # 格网ID
        self.gid = gid
        #东北、北、西北、西南、南、东南五个方向magnitude, 和distance
        self.m = [0]*dnum
        self.d = [0]*dnum
        self.num = [0]*dnum


def readData(sjFile, flowOpGridFile, dgids, dnum, hexParm):
    grids = {}
    for gid in dgids:
        grids[gid] = Grid(gid, dnum)

    flowOpGrid = {}
    with open(flowOpGridFile, 'r') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if int(sl[1]) == '0':
                    continue
                flowOpGrid[int(sl[3])] = int(sl[4])
            else:
                break

    mdi = {(1, 1): 0, (1, -1): 5, (0, 2): 1, (0, -2): 4, (-1, 1): 2, (-1, -1): 3}
    with open(sjFile, 'r') as f:
        f.readline()
        fid = -1
        gids = []
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if sl[1] != '1':
                    continue

                gid = int(sl[-1])
                if int(float(sl[4])) == fid:
                    gids.append(gid)
                else:
                    if len(set(gids)) > 1:
                        idx = []
                        for temgid in gids:
                            y, x = computeRC(temgid, hexParm)
                            idx.append([temgid, y, x])
                        idx.sort(key=lambda x:(x[2],x[1]))
                        if flowOpGrid[fid] != idx[0][0]:
                            idx.reverse()
                        for i in range(len(idx)-1):
                            if idx[i][0] in dgids:
                                dx = idx[i+1][2] - idx[i][2]
                                dy = idx[i+1][1] - idx[i][1]
                                if (dx, dy) in mdi:
                                    grids[idx[i][0]].m[mdi[(dx,dy)]] += 1
                                    grids[idx[i][0]].d[mdi[(dx,dy)]] += len(gids)-1
                                    grids[idx[i][0]].num[mdi[(dx,dy)]] += 1

                    fid = int(float(sl[4]))
                    gids = [gid]
            else:
                if len(set(gids)) > 1:
                    idx = []
                    for temgid in gids:
                        y, x = computeRC(temgid, hexParm)
                        idx.append([temgid, y, x])
                    idx.sort(key=lambda x: (x[2], x[1]))
                    if flowOpGrid[fid] != idx[0][0]:
                        idx.reverse()
                    for i in range(len(idx) - 1):
                        if idx[i][0] in dgids:
                            dx = idx[i + 1][2] - idx[i][2]
                            dy = idx[i + 1][1] - idx[i][1]
                            if (dx, dy) in mdi:
                                grids[idx[i][0]].m[mdi[(dx, dy)]] += 1
                                grids[idx[i][0]].d[mdi[(dx, dy)]] += len(gids) - 1
                                grids[idx[i][0]].num[mdi[(dx, dy)]] += 1
                break

    for gid in grids:
        for i in range(dnum):
            if grids[gid].num[i]:
                grids[gid].d[i] /= grids[gid].num[i]

    return grids


def drawTrajPattern(grids, ia, saveFileName, dnum=6):
    mag = []
    dis = []
    for g in grids:
        for tm in grids[g].m:
            mag.append(tm)
        for td in grids[g].d:
            dis.append(td)
    k_m = ia['k_m']
    nk, nl = fisher_jenks(mag, k_m)
    dk, dl = fisher_jenks(dis, ia['k_d'])

    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']
    gridBorderWidth = ia['gridBorderWidth']
    c_m = ia['c_m']
    c_d = ia['c_d']

    # RGB
    image = Image.new('RGB', (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo((gridWidth+gridBorderWidth) * 0.75, dnum // 6)

    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            x = np.where(grids[gid].m[i] <= nk)[0]
            j = x.min() if x.size > 0 else len(nk) - 1
            draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                         fill=c_m[j], outline=c_m[j])

            x = np.where(grids[gid].d[i] <= dk)[0]
            k = x.min() if x.size > 0 else len(dk) - 1
            draw.polygon(
                [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                 cenx + ixs[i + 1], ceny + iys[i + 1]], outline=c_d[k], fill=c_d[k])

    if True:
        indicatorfont = ImageFont.truetype('./font/times.ttf', 67)
        indColor = '#4286f4'#'#ff2121'
        indWidth = 3
        cenx, ceny = computeCen(75, ia)
        draw.line([cenx+gridWidth/2, ceny-gridWidth/2, 350, 2450], width=indWidth, fill=indColor)
        draw.text((20, 2450), 'The 4th ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(329, ia)
        draw.line([cenx, ceny+gridWidth/4, 350, 2650], width=indWidth, fill=indColor)
        draw.text((20, 2650), 'The 3rd ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(343, ia)
        draw.line([cenx-gridWidth, ceny-gridWidth/4, 350, 2850], width=indWidth, fill=indColor)
        draw.text((20, 2850), 'The 2nd ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(213, ia)
        draw.line([cenx, ceny+gridWidth, 2600, 200], width=indWidth, fill=indColor)
        draw.text((2330, 100), 'The airport expressway', font=indicatorfont, fill=indColor)



    # ----draw legend----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 64)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 60)
    sy = iheight - 50
    lw = ia['legendWidth']
    if '500m' in saveFileName:
        gridWidth *= 2

    # magnitude
    mx = iwidth - 550
    for i, c in enumerate(c_m):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)
    draw.text((mx - gridWidth-20, sy - (k_m + 6) * lw), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth-20, sy - lw), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth-20, sy - lw * (k_m + 1)), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    mx = iwidth - 270
    for i, c in enumerate(c_d):
        draw.line([mx, sy - i * lw * 3, mx + gridWidth, sy - i * lw * 3], width=lw * 3, fill=c)
    draw.text((mx - gridWidth + 20, sy - (k_m + 6) * lw), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx + 1.3 * gridWidth, sy - lw), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx + 1.3 * gridWidth, sy - lw * (k_m + 1)), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    iquality = ia['quality']
    idpi = ia['dpi']
    image.save(saveFileName, quality=iquality, dpi=idpi)


if __name__ == '__main__':
    scale = '_1km'
    dnum = 6
    sjFile = './data/sj_ftt'+scale+'.csv'
    flowOpGridFile = './data/sj_op'+scale+'.csv'
    saveFileName = './figure/tj_051316_0509.jpg'

    dgids = readGids('./data/5th_rr_gid' + scale + '.csv')
    ia = readDrawingSetting('tj', scale[1:])
    grids = readData(sjFile, flowOpGridFile, dgids, dnum, ia['hexParm'])

    drawTrajPattern(grids, ia, saveFileName)
