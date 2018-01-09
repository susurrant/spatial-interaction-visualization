# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns
from func import *

def drawGridSymbol_hexagon(dnum=6):
    mc = []
    nscale = [(i + 1) / float(dnum + 1) for i in range(dnum)]
    for n in nscale:
        mc.append('#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
    dc = ['#9fd4ff', '#00dd66', '#ffd700', '#ff8000', '#c70000', '#ffd700']

    gridWidth = 240
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * 0.9, dnum // 6)

    image = Image.new('RGB', (500, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    cenx = 250
    ceny = 225
    for i in range(dnum):
        draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                      fill=mc[i%dnum], outline=mc[i])
        draw.polygon(
            [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                cenx + ixs[i + 1], ceny + iys[i + 1]], outline=dc[i%dnum], fill=dc[i%dnum])

    image.save('./figure/glyph.jpg', quality=95, dpi=(1200, 1200))


def drawPattern_bc(grids, flows, ia, saveFileName):
    # -------------------------------classify data----------------------------------
    mag = []
    dis = []
    for g in grids:
        grids[g].calcOutAggregation(flows)
        for tm in grids[g].wm:
            mag.append(tm)
        for td in grids[g].wd:
            dis.append(td)

    nk, nl = kmeans(mag, ia['mag_class_number'])
    dk, dl = kmeans(dis, ia['dis_class_number'])

    # -----------------------------draw visual glyphs-------------------------------
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    gridWidth = ia['gridWidth']
    xs, ys = computeCo(gridWidth, ia['dnum']//6)
    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        border = []
        for i in range(ia['dnum']):
            border.append(cenx + xs[i])
            border.append(ceny + ys[i])
            j = nl.index(nk.predict(grids[gid].wm[i]))
            k = dl.index(dk.predict(grids[gid].wd[i]))
            nc = ia['color_scheme'][j][k]
            draw.polygon([cenx,ceny,cenx+xs[i], ceny+ys[i], cenx+xs[i+1], ceny+ys[i+1]], fill=nc, outline=nc)
        draw.polygon(border, outline = ia['border_color'])

    # ----------------------------mark locations------------------------------
    indicatorfont = ImageFont.truetype('./font/times.ttf', 90)
    if False:
        cenx, ceny = computeCen(128, ia)
        draw.line([cenx, ceny, 2850, 750], width=2, fill='#000000')
        draw.text((2870, 700), 'B', font=indicatorfont, fill='#000000')
        cenx, ceny = computeCen(100, ia)
        draw.line([cenx, ceny, 300, 2500], width=2, fill='#000000')
        draw.text((230, 2460), 'A', font=indicatorfont, fill='#000000')
    '''
    labelfont = ImageFont.truetype('./font/times.ttf', 50)
    labelColor = '#0000ff'#'#003371'
    textColor = '#871F78'
    if '1km' in saveFileName:
        if '0105' in saveFileName:
            cenx, ceny = computeCen(150, ia)
            draw.text((cenx-24, ceny+30), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(164, ia)
            draw.text((cenx-87, ceny+10), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(437, ia)
            draw.text((cenx-20, ceny+45), 'C', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height']-180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height']-120), 'B: Sanlitun', font=labelfont, fill=textColor)
            draw.text((30, ia['height']-60), 'C: Wudaokou', font=labelfont, fill=textColor)
        elif '0509' in saveFileName:
            cenx, ceny = computeCen(150, ia)
            draw.text((cenx - 24, ceny + 30), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(176, ia)
            draw.text((cenx - 105, ceny - 40), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(124, ia)
            draw.text((cenx + 10, ceny - 115), 'C', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(356, ia)
            draw.text((cenx + 50, ceny - 85), 'D', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao (A transfer station)', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)
            draw.text((800, ia['height'] - 60), 'D: Shuangjin', font=labelfont, fill=textColor)
    elif '500m' in saveFileName:
        if '0509' in saveFileName:
            cenx, ceny = computeCen(563, ia)
            draw.text((cenx - 24, ceny), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(1647, ia)
            draw.text((cenx - 65, ceny - 40), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(487, ia)
            draw.text((cenx + 5, ceny - 70), 'C', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)
    '''

    # -----------------------------draw legends-------------------------------
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 52)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 48)
    ls = ia['legend_size']
    bottom = ia['height'] - ia['legend_yoffset']
    left = ia['width'] - ia['dis_class_number']*ls - ia['legend_xoffset']

    for j in range(ia['mag_class_number']):
        for k in range(ia['dis_class_number']):
            draw.rectangle([(left+k*ls, bottom-j*ls),(left+(k+1)*ls, bottom-(j+1)*ls)], fill = ia['color_scheme'][j][k])

    draw.text((left - 300, bottom - ia['mag_class_number'] * ls / 2 - 30), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 120, bottom - 30), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left - 120, bottom - ia['mag_class_number'] * ls - 10), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    draw.text((left + ia['dis_class_number'] * ls / 2 - 90, bottom + 60), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 80, bottom + 20), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left + ia['dis_class_number'] * ls - 40, bottom + 20), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    # -----------------------------save figure-------------------------------
    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawHexagons_bs(draw, grids, gridWidth, area_scale, margin, dnum):
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * area_scale, dnum // 6)
    fxs, fys = computeCo(gridWidth + margin, dnum // 6)
    for gid in grids:
        if len(grids[gid].wm) == 0:
            print('grid %d is empty!' % gid)
            continue

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


def drawPattern_bs(grids, flows, ia, saveFileName):
    processGrids(grids, flows, ia)

    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']

    # RGB
    image = Image.new('RGB', (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])

    indicatorfont = ImageFont.truetype('./font/times.ttf', 90)

    if False:
        cenx, ceny = computeCen(128, ia)
        draw.line([cenx, ceny, 2850, 750], width=2, fill='#000000')
        draw.text((2870, 700), 'B', font=indicatorfont, fill='#000000')
        cenx, ceny = computeCen(100, ia)
        draw.line([cenx, ceny, 300, 2500], width=2, fill='#000000')
        draw.text((230, 2460), 'A', font=indicatorfont, fill='#000000')

    labelfont = ImageFont.truetype('./font/times.ttf', 50)
    labelColor = '#0000ff'#'#003371'
    textColor = '#871F78'

    if '1km' in saveFileName:
        indicatorfont = ImageFont.truetype('./font/calibril.ttf', 80)
        dx = 20
        dy = 40
        if '0509' in saveFileName:
            draw.text((grids[150].cenx - dx - 4, grids[150].ceny - dy - 6), 'A',
                      font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
            draw.text((grids[150].cenx - dx, grids[150].ceny - dy), 'A', font=indicatorfont, fill=labelColor)

            draw.text((grids[176].cenx - dx - 4, grids[176].ceny - dy - 6), 'B',
                      font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
            #draw.text((grids[176].cenx - dx, grids[176].ceny - dy), 'B', font=indicatorfont, fill=labelColor)

            draw.text((grids[124].cenx - dx - 4, grids[124].ceny - dy - 6), 'C',
                      font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
            #draw.text((grids[124].cenx - dx, grids[124].ceny - dy), 'C', font=indicatorfont, fill=labelColor)

            draw.text((grids[356].cenx - dx - 4, grids[356].ceny - dy - 6), 'D',
                      font=ImageFont.truetype('./font/calibril.ttf', 95), fill='#ffffff')
            draw.text((grids[356].cenx - dx, grids[356].ceny - dy), 'D', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao (A transfer hub)', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)
            draw.text((800, ia['height'] - 60), 'D: Shuangjin', font=labelfont, fill=textColor)
    elif '500m' in saveFileName:
        indicatorfont = ImageFont.truetype('./font/calibril.ttf', 50)
        dx = 13
        dy = 20
        if '0509' in saveFileName:
            draw.text((grids[563].cenx - dx, grids[563].ceny - dy), 'A', font=indicatorfont, fill=labelColor)

            draw.text((grids[1647].cenx - dx, grids[1647].ceny - dy), 'B', font=indicatorfont, fill='#ffffff')
            draw.text((grids[487].cenx - dx, grids[487].ceny - dy), 'C', font=indicatorfont, fill='#ffffff')

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)

    if '1721' in saveFileName:
        labelfont = ImageFont.truetype('./font/calibril.ttf', 80)
        left = 650
        right = 1230
        top = 380
        bottom = 920
        draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill='#0000ff', width=4)
        draw.line([left, top, 200, 200], fill='#0000ff', width=3)
        draw.text((130, 150), 'D', font=labelfont, fill=(0, 0, 0))

        draw.line([grids[124].cenx, grids[124].ceny, 200, 2300], fill='#0000ff', width=3)
        draw.text((140, 2300), 'A', font=labelfont, fill=(0, 0, 0))

        draw.line([grids[116].cenx, grids[116].ceny, 2850, 2300], fill='#0000ff', width=3)
        draw.text((2880, 2300), 'B', font=labelfont, fill=(0, 0, 0))

        draw.line([grids[186].cenx, grids[186].ceny, 2850, 200], fill='#0000ff', width=3)
        draw.text((2880, 150), 'C', font=labelfont, fill=(0, 0, 0))

    # ----draw legend----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 54)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 50)
    sy = iheight - 50
    lw = ia['legendWidth']
    if '500m' in saveFileName:
        gridWidth *= 2

    # magnitude
    mx = iwidth - 480
    for i, c in enumerate(ia['c_m']):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)
    draw.text((mx-gridWidth, sy-(ia['k_m']+5)*lw), 'Magnitude', font=imageTitlefont, fill=(0,0,0))
    draw.text((mx-1.5*gridWidth, sy-lw), 'Low', font=imageMeasureFont, fill=(0,0,0))
    draw.text((mx-1.5*gridWidth, sy-lw*(ia['k_m']+1)), 'High', font=imageMeasureFont, fill=(0,0,0))

    # distance
    disx = iwidth - 230
    scale = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy-(i+0.35)*lw*scale, disx+gridWidth, sy-(i+0.35)*lw*scale], width=int(round(lw*scale)), fill=n)
    draw.text((disx-gridWidth/2-15, sy-(ia['k_m']+5)*lw), 'Distance', font=imageTitlefont, fill=(0,0,0))
    draw.text((disx+20+gridWidth, sy-lw), 'Short', font=imageMeasureFont, fill=(0,0,0))
    draw.text((disx+20+gridWidth, sy-lw*ia['k_m']-lw), 'Long', font=imageMeasureFont, fill=(0,0,0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawSingleHexagon_bs(draw, grid, gridWidth, area_scale, dnum, cenx=None, ceny=None):
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * area_scale, dnum // 6)

    if not cenx:
        cenx = grid.cenx
    if not ceny:
        ceny = grid.ceny

    for i in range(dnum):
        draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                      fill=grid.mcolor[i], outline=grid.mcolor[i])
        draw.polygon(
            [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                cenx + ixs[i + 1], ceny + iys[i + 1]], outline=grid.dcolor[i], fill=grid.dcolor[i])


def drawSinglePattern_bs(gid, grids, flows, ia, saveFileName):
    processGrids(grids, flows, ia)
    gridWidth = 240

    # RGB
    image = Image.new('RGB', (500, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    drawSingleHexagon_bs(draw, grids[gid], gridWidth, 0.85, ia['dnum'], 250, 225)

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawPattern_bs_earlymorning(grids, flows, ia, saveFileName):
    processGrids(grids, flows, ia)

    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']

    # RGB
    image = Image.new('RGB', (iwidth, iheight+530), '#ffffff')
    draw = ImageDraw.Draw(image)
    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])

    drawSingleHexagon_bs(draw, grids[124], 220, 0.8, ia['dnum'], 375, 3250)
    drawSingleHexagon_bs(draw, grids[437], 220, 0.8, ia['dnum'], 1125, 3250)
    drawSingleHexagon_bs(draw, grids[150], 220, 0.8, ia['dnum'], 1875, 3250)
    drawSingleHexagon_bs(draw, grids[392], 220, 0.8, ia['dnum'], 2625, 3250)

    labelfont = ImageFont.truetype('./font/times.ttf', 58)
    lineColor = '#5566ff'#'#0000ff'
    textColor = '#871F78'

    draw.line([grids[124].cenx, grids[124].ceny, 375, 3030], width=4, fill=lineColor)
    draw.line([grids[437].cenx, grids[437].ceny, 1125, 3030], width=4, fill=lineColor)
    draw.line([grids[150].cenx, grids[150].ceny, 1875, 3030], width=4, fill=lineColor)
    draw.line([grids[164].cenx, grids[164].ceny, 2625, 3030], width=4, fill=lineColor)

    draw.text((50, ia['height'] + 530 - 73), 'A: Beijing West Railway Station', font=labelfont, fill=textColor)
    draw.text((960, ia['height'] + 530 - 73), 'B: Wudaokou', font=labelfont, fill=textColor)
    draw.text((1650, ia['height'] + 530 - 73), 'C: The Forbidden City', font=labelfont, fill=textColor)
    draw.text((2500, ia['height'] + 530 - 73), 'D: Sanlitun', font=labelfont, fill=textColor)

    # ----draw legend----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 54)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 50)
    sy = iheight - 50
    lw = ia['legendWidth']
    if '500m' in saveFileName:
        gridWidth *= 2

    # magnitude
    mx = iwidth - 480
    for i, c in enumerate(ia['c_m']):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)
    draw.text((mx - gridWidth, sy - (ia['k_m'] + 5) * lw), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth, sy - lw), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.5 * gridWidth, sy - lw * (ia['k_m'] + 1)), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    # distance
    disx = iwidth - 230
    scale = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy - (i + 0.35) * lw * scale, disx + gridWidth, sy - (i + 0.35) * lw * scale],
                  width=int(round(lw * scale)), fill=n)
    draw.text((disx - gridWidth / 2 - 15, sy - (ia['k_m'] + 5) * lw), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((disx + 20 + gridWidth, sy - lw), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((disx + 20 + gridWidth, sy - lw * ia['k_m'] - lw), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawCdif_Kmeans(grids1, grids2, flows1, flows2, alpha, ia, saveFileName):
    k_dif = ia['k_dif']
    dif = cdif(grids1, grids2, flows1, flows2, alpha)
    dif_train = []
    for gid in grids1:
        dif_train.append([dif[gid], 0])
    difk, difl = kmeans(dif_train, k_dif)
    ia['margin'] /= 2
    ia['height'] = 2700
    ia['width'] = 2700
    ia['ox'] = 10
    ia['oy'] = 30
    c_dif = ia['c_dif']
    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']

    image = Image.new("RGB", (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    for gid in grids1:
        cenx, ceny = computeCen(gid, ia)
        hex_co = computeCo_hexagon(cenx, ceny, gridWidth)

        nc = c_dif[difl.index(difk.predict([[dif[gid], 0]])[0])]
        co = []
        for item in hex_co:
            co.append(item[2])
            co.append(item[3])
        co.append(co[0])
        co.append(co[1])
        draw.polygon(co, fill=nc, outline=nc)

    '''
    if True:
        indicatorfont = ImageFont.truetype('./font/times.ttf', 50)
        cenx, ceny = computeCen(5262, ia, shape)
        symbolWidth = gridWidth + ia['margin']
        draw.line([cenx, ceny, cenx-2*symbolWidth+10, ceny+3*symbolWidth], width=1, fill='#000000')
        draw.text((cenx-2*symbolWidth-10, ceny+3*symbolWidth+10), u'\u2161', font=indicatorfont, fill=(0,0,0))

        cenx, ceny = computeCen(6476, ia, shape)
        symbolWidth = gridWidth + ia['margin']
        draw.line([cenx, ceny, cenx + 9 * symbolWidth+10, ceny - 4 * symbolWidth-5], width=1, fill='#000000')
        draw.text((cenx + 9 * symbolWidth+30, ceny - 4 * symbolWidth - 45), u'\u2160', font=indicatorfont, fill=(0, 0, 0))
    '''
    # ----绘制边框----
    #fm = ia['frameMargin']
    #draw.rectangle([fm, fm, iwidth - fm, iheight - fm], outline='#000000')

    # ----绘制图例----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 54)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 50)
    sy = iheight - 50
    lw = ia['legendWidth']*2

    # 绘制差异矩形
    mx = iwidth - 300
    for i, c in enumerate(c_dif):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)

    draw.text((mx - gridWidth / 2 - 40, sy - (k_dif + 3) * lw), 'Difference', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx + 60 + gridWidth / 2, sy - lw), 'Small', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx + 60 + gridWidth / 2, sy - lw * k_dif - lw/2), 'Large', font=imageMeasureFont, fill=(0, 0, 0))

    iquality = ia['quality']
    idpi = ia['dpi']
    image.save(saveFileName, quality=iquality, dpi=idpi)


def drawCdifDistribution(gids, gdif, c, labels):
    sns.set(style="whitegrid")
    sns.set_context("paper")

    fig, ax = plt.subplots()
    ax.set_ylabel('odif', fontname="Times New Roman", style='italic', fontsize=13)
    ax.set_xlabel('Time', fontname="Times New Roman", fontsize=13)
    x = [i for i in range(5)]
    ls = []
    for i, gid in enumerate(gids):
        l, = ax.plot(x, gdif[gid], 'o--', linewidth = 2, color = c[i], label = labels[i])
        ls.append(l)


    ax.set_ylim(0, 0.4)
    ys = [0, 0.1, 0.2, 0.3, 0.4]
    ax.set_yticks(ys)
    ylabels = [str(abs(item)) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=12)


    ax.set_xlim(0, 4)
    xs = [i for i in range(0, 5)]
    ax.set_xticks(xs)
    xlabels = ['1-5 a.m.', '9 a.m.-1 p.m.', '1-5 p.m.', '5-9 p.m.', '9 p.m.-1 a.m.']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=12)


    leg = plt.legend(handles=ls, loc=0)
    for l in leg.get_texts():
        l.set_fontsize(12)
        l.set_fontname("Times New Roman")

    plt.show()


def userScore():
    sns.set(style="whitegrid")

    x = [i for i in range(1, 4)]
    '''
    oyIM = [[3,2,1,2,1,2,3,4,1,4,0,2,3,2,1,3,3,3,2,4], [3,4,1,1,1,2,3,3,1,2,0,2,3,1,1,3,3,2,2,3], [1,0,2,1,3,0,1,2,3,3],
           [4,2,1,2,2,2,2,3,5,2,2,0,3,1,1,0,2,2,1,3], [3,3,3,3,2,1,2,5,3,2,0,0,0,0,0,2,4,3,3,5],
           [0,1,0,0,0,0,0,0,0,0,0,3,2,1,0,1,0,0,0,0], [1,1,2,2,1,1,1,2,4,5,1,2,1,2,4,1,3,1,1,3]]
    oyFM = [[2,2,0,3,2,4,2,4,3,2,1,1,3,3,3,1,1,2,4,2], [4,4,2,4,2,4,4,5,4,3,3,4,4,3,5,3,3,3,5,3], [4,4,4,3,4,3,4,3,5,4],
           [4,4,2,4,3,3,4,4,5,4,4,4,5,3,5,4,4,4,3,4], [4,1,1,5,2,3,3,4,5,5,3,3,1,1,5,3,1,4,4,3],
           [4,3,2,5,3,3,2,3,3,4,4,2,0,2,5,4,5,3,4,5], [4,2,3,4,3,4,3,4,3,3,3,3,3,3,4,3,2,3,3,5]]
    oyPM = [[5,5,3,5,4,4,4,4,5,3,4,4,5,4,5,5,4,5,5,5], [5,4,3,5,4,4,5,5,4,4,4,4,5,4,4,5,4,4,5,4], [5,5,4,4,5,5,5,4,5,5],
           [5,4,3,5,3,4,3,4,3,3,4,5,5,3,4,4,4,3,5,4], [5,4,2,4,4,5,4,3,1,3,5,3,5,5,3,4,4,2,5,4],
           [5,4,3,5,4,5,4,4,3,3,4,4,4,5,3,5,5,5,5,4], [5,5,4,5,5,5,4,4,2,4,4,4,5,5,3,5,4,5,5,4]]
    
    yIM = []
    yFM = []
    yPM = []

    for i in range(7):
        yIM.append(np.mean(sorted(oyIM[i])[1:-1]))
        yFM.append(np.mean(sorted(oyFM[i])[1:-1]))
        yPM.append(np.mean(sorted(oyPM[i])[1:-1]))

    '''
    yIM = [0.1,0,1,0.1]
    yFM = [0.3,0.8,1.0,0.1]
    yPM = [1,1,1,0.9]
    Q1 = [3/14, 4/14, 14/14]
    Q2 = [0, 11/14, 14/14]
    Q3 = [14/14, 14/14, 14/14]
    Q4 = [1/14, 1/14, 13/14]

    x = np.array(x)
    fs1 = 18
    fs2 = 16

    fig, ax = plt.subplots()
    #ax.set_xlabel('', fontname="Times New Roman", fontsize=fs1)
    ax.set_ylabel('Accuracy', fontname="Times New Roman", fontsize=fs1)

    l1 = ax.bar(x-0.2, Q1, facecolor='#ff2121', width=0.1, label='Q1')
    l2 = ax.bar(x-0.1, Q2, facecolor='#44cef6', width=0.1, label='Q2')
    l3 = ax.bar(x, Q3, facecolor='#00e500', width=0.1, label='Q3')
    l4 = ax.bar(x+0.1, Q4, facecolor='#fff143', width=0.1, label='Q4')


    ax.set_ylim(0, 1)
    ys = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    ax.set_xlim(0, 4)
    xs = [1, 2, 3]
    ax.set_xticks(xs)
    xlabels = ['The interaction matrix', 'The flow map', 'Our approach']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=[l1, l2, l3, l4])
    for l in leg.get_texts():
        l.set_fontsize(14)
        l.set_fontname("Times New Roman")
    plt.show()