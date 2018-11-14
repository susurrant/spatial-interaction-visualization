# -*- coding: utf-8 -*-：

# dnum = 8

from PIL import Image, ImageDraw, ImageFont
from func import *
from grid import Square
from LL2UTM import LL2UTM_USGS
from style import readDrawingSetting


def computeCo_square(gridwidth):
    l = gridwidth/2
    xs = [l, l, 0, -l, -l, -l, 0, l, l]
    ys = [0, -l, -l, -l, 0, l, l, l, 0]
    return xs, ys


# compute central point coordinates for a square
def computeCen_square(gid, ia):
    ox = ia['ox']
    oy = ia['oy']
    x = gid % ia['shape'][1]
    y = ia['shape'][0] - 1 - gid // ia['shape'][1]
    cenx = ox + (x - ia['xoffset']) * (ia['gridWidth'] + ia['margin'])
    ceny = oy + (y - ia['yoffset']) * (ia['gridWidth'] + ia['margin'])

    return cenx, ceny


def drawHexagons_bs(draw, grids, gridWidth, area_scale, margin, dnum):
    oxs, oys = computeCo_square(gridWidth)
    ixs, iys = computeCo_square(gridWidth * area_scale)
    fxs, fys = computeCo_square(gridWidth + margin)
    for gid in grids:
        cenx, ceny = grids[gid].cenx, grids[gid].ceny
        fco = []
        for i in range(dnum):
            draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                         fill=grids[gid].mcolor[i], outline=grids[gid].mcolor[i])
            draw.polygon(
                [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                 cenx + ixs[i + 1], ceny + iys[i + 1]], outline=grids[gid].dcolor[i], fill=grids[gid].dcolor[i])
            fco.append(cenx + fxs[i])
            fco.append(ceny + fys[i])
        draw.polygon(fco, fill=None, outline='#000000')


def drawLabels(draw, grids, ia, scale):
    labelfont = ImageFont.truetype('./font/times.ttf', 64)
    labelColor = '#0000ff'  # '#003371'
    textColor = '#871F78'

    if scale == '1km':
        indicatorfont = ImageFont.truetype('./font/calibril.ttf', 80)
        dx = 20
        dy = 40

        draw.text((grids[150].cenx - dx - 4, grids[150].ceny - dy - 6), 'B',
                  font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
        draw.text((grids[150].cenx - dx, grids[150].ceny - dy), 'B', font=indicatorfont, fill=labelColor)

        draw.text((grids[139].cenx - dx - 4, grids[139].ceny - dy - 6), 'C',
                  font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')

        draw.text((grids[124].cenx - dx - 4, grids[124].ceny - dy - 6), 'D',
                  font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')

        draw.text((grids[356].cenx - dx - 4, grids[356].ceny - dy - 6), 'A',
                  font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
        draw.text((grids[356].cenx - dx, grids[356].ceny - dy), 'A', font=indicatorfont, fill=labelColor)

        draw.text((30, ia['height'] - 250), 'A: Shuangjin', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 190), 'B: The Forbidden City', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 130), 'C: Beijing Railway Station', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 70), 'D: Beijing West Railway Station', font=labelfont, fill=textColor)

    elif scale == '500m':
        indicatorfont = ImageFont.truetype('./font/calibril.ttf', 52)
        dx = 13
        dy = 20
        draw.text((grids[563].cenx - dx, grids[563].ceny - dy), 'A', font=indicatorfont, fill=labelColor)
        draw.text((grids[517].cenx - dx, grids[517].ceny - dy), 'C', font=indicatorfont, fill='#ffffff')
        draw.text((grids[487].cenx - dx, grids[487].ceny - dy), 'D', font=indicatorfont, fill='#ffffff')
        draw.text((grids[1716].cenx - dx, grids[1716].ceny - dy), 'B', font=indicatorfont, fill=labelColor)

        draw.text((30, ia['height'] - 260), 'A: The Forbidden City', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 200), 'B: Olympic Forest Park', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 140), 'C: Beijing Railway Station', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 80), 'D: Beijing West Railway Station', font=labelfont, fill=textColor)


def drawPattern_bs(grids, flows, ia, scale, saveFileName):
    max_mag, max_dis = processGrids_fj(grids, flows, ia)
    for gid in grids:
        grids[gid].cenx, grids[gid].ceny = computeCen_square(gid, ia)

    iwidth = ia['width']
    iheight = ia['height']

    # RGB
    image = Image.new('RGB', (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])

    #drawLabels(draw, grids, ia, scale)

    # ----draw legend----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 64)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 60)
    sy = iheight - 50
    lh = ia['legend_height']
    lw = ia['legend_width']

    # magnitude
    mx = iwidth - 530
    for i, c in enumerate(ia['c_m']):
        draw.line([mx, sy - i * lh, mx + lw, sy - i * lh], width=lh, fill=c)
    draw.text((mx-lw*1.2, sy-(ia['k_m']+5)*lh), 'Magnitude', font=imageTitlefont, fill=(0,0,0))
    draw.text((mx-lw/1.7, sy-lh), '0', font=imageMeasureFont, fill=(0,0,0))
    draw.text((mx-1.1*lw, sy-lh*(ia['k_m']+1)), str(max_mag), font=imageMeasureFont, fill=(0,0,0))

    # distance
    disx = iwidth - 260
    s = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy-(i+0.35)*lh*s, disx+lw, sy-(i+0.35)*lh*s], width=int(round(lh*s)), fill=n)
    draw.text((disx-lw*0.8, sy-(ia['k_m']+5)*lh), 'Distance/km', font=imageTitlefont, fill=(0,0,0))
    draw.text((disx+1.2*lw, sy-lh), '0', font=imageMeasureFont, fill=(0,0,0))
    draw.text((disx+1.2*lw, sy-lh*ia['k_m']-lh), str('%.2f'%max_dis), font=imageMeasureFont, fill=(0,0,0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


# 读取数据
def readData(filename, dgids, dnum, minSpeed = 2, maxSpeed = 150):
    flows = {}
    grids = {}
    for gid in dgids:
        grids[gid] = Square(gid, dnum)

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
def readData_Inside(filename, dgids, dnum, minSpeed = 2, maxSpeed = 150):
    flows = {}
    grids = {}
    for gid in dgids:
        grids[gid] = Square(gid, dnum)

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

    drawPattern_bs(grids, flows, ia, scale, saveFileName)


if __name__ == '__main__':
    scale = '1km'
    mode = 'sq'
    dgids = readGids('./data/5th_rr_square_' + scale + '.csv')
    ia = readDrawingSetting(mode, scale)

    SIPatterns('./data/sj_051316_1721_1.6km_square', dgids, ia, scale, mode, True)  # True 表示只显示五环内的数据
