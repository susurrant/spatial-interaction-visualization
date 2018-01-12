# -*- coding: utf-8 -*-：

from func import readGids, computeRC, kmeans, computeCo, computeCen
from PIL import Image, ImageDraw, ImageFont

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


def readDrawingSetting(scale):
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 84, 'gridBorderWidth': 2, 'ox': 40, 'oy': 50, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 3, 'yoffset': 3, 'frameMargin': 5, 'legendWidth': 15, 'quality': 1000, 'dpi': (1200, 1200),
              'k_m': 30, 'k_d': 10, 'c_m': [], 'c_d': []}
    # color setting
    nscale = [(i + 1) / float(ia['k_m'] + 1) for i in range(ia['k_m'])]

    for i, n in enumerate(nscale):
        ia['c_m'].append('#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
    ia['c_m'][0] = '#ffffff'

    ia['c_d'] = ['#9fd4ff', '#00dd66', '#ffd700', '#ff8000', '#c70000']
    ia['c_d'] = ['#fefffe', '#ffe6e6', '#fecece', '#fbb5b5', '#f69d9d', '#f08585', '#e76c6c', '#de5252', '#d23434', '#c50000']


    return ia

def drawSIP_8DKmeans(grids, ia, saveFileName, dnum=6):
    mag = []
    dis = []
    for g in grids:
        for tm in grids[g].m:
            mag.append(tm)
        for td in grids[g].d:
            dis.append(td)
    k_m = ia['k_m']
    nk, nl = kmeans(mag, k_m)
    dk, dl = kmeans(dis, ia['k_d'])

    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']
    gridBorderWidth = ia['gridBorderWidth']
    c_m = ia['c_m']
    c_d = ia['c_d']

    # RGB
    image = Image.new('RGB', (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)
    xs, ys = computeCo(gridWidth, dnum // 6)
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo((gridWidth+gridBorderWidth) * 0.75, dnum // 6)

    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            nc = c_m[nl.index(nk.predict(grids[gid].m[i]))]
            draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                         fill=nc, outline=nc)

            dc = c_d[dl.index(dk.predict(grids[gid].d[i]))]
            draw.polygon(
                [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                 cenx + ixs[i + 1], ceny + iys[i + 1]], outline=dc, fill=dc)

            #draw.line([cenx + xs[i], ceny + ys[i], cenx + xs[i + 1], ceny + ys[i + 1]], width=gridBorderWidth,
            #          fill='#000000')


    if True:
        indicatorfont = ImageFont.truetype('./font/times.ttf', 60)
        indColor = '#ff2121'
        indWidth = 3
        cenx, ceny = computeCen(75, ia)
        draw.line([cenx+gridWidth/2, ceny-gridWidth/2, 350, 2450], width=indWidth, fill=indColor)
        draw.text((60, 2450), 'The 4th ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(329, ia)
        draw.line([cenx, ceny+gridWidth/4, 350, 2650], width=indWidth, fill=indColor)
        draw.text((60, 2650), 'The 3rd ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(343, ia)
        draw.line([cenx-gridWidth, ceny-gridWidth/4, 350, 2850], width=indWidth, fill=indColor)
        draw.text((60, 2850), 'The 2nd ring road', font=indicatorfont, fill=indColor)

        cenx, ceny = computeCen(213, ia)
        draw.line([cenx, ceny+gridWidth/4, 2600, 200], width=indWidth, fill=indColor)
        draw.text((2400, 100), 'The airport expressway', font=indicatorfont, fill=indColor)



    # ----draw legend----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 54)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 50)
    sy = iheight - 50
    lw = ia['legendWidth']
    if '500m' in saveFileName:
        gridWidth *= 2

    # magnitude
    mx = iwidth - 550
    for i, c in enumerate(c_m):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)
    draw.text((mx - gridWidth, sy - (k_m + 5) * lw), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth, sy - lw), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth, sy - lw * (k_m + 1)), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    mx = iwidth - 270
    for i, c in enumerate(c_d):
        draw.line([mx, sy - i * lw * 3, mx + gridWidth, sy - i * lw * 3], width=lw * 3, fill=c)
    draw.text((mx - gridWidth + 20, sy - (k_m + 5) * lw), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx + 1.5 * gridWidth, sy - lw), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx + 1.5 * gridWidth, sy - lw * (k_m + 1)), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    iquality = ia['quality']
    idpi = ia['dpi']
    image.save(saveFileName, quality=iquality, dpi=idpi)


if __name__ == '__main__':
    scale = '_1km'
    dnum = 6
    sjFile = './data/sj_ftt'+scale+'.csv'
    flowOpGridFile = './data/sj_op'+scale+'.csv'
    saveFileName = './figure/tp_051316_0509.jpg'

    dgids = readGids('./data/5th_rr_gid' + scale + '.csv')
    ia = readDrawingSetting(scale[1:])
    grids = readData(sjFile, flowOpGridFile, dgids, dnum, ia['hexParm'])

    drawSIP_8DKmeans(grids, ia, saveFileName)
