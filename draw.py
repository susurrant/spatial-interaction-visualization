# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns
from func import *
import numpy as np

# draw glyph
def drawSingleGlyph(ia):
    dnum = ia['dnum']

    gridWidth = 240
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * 0.9, dnum // 6)

    image = Image.new('RGB', (500, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    cenx = 250
    ceny = 225
    for i in range(dnum):
        draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                      fill=ia['c_m'][i%dnum], outline=ia['c_m'][i])
        draw.polygon(
            [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                cenx + ixs[i + 1], ceny + iys[i + 1]], outline=ia['c_d'][i%dnum], fill=ia['c_d'][i%dnum])

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

    nk, nl = fisher_jenks(mag, ia['mag_class_number'])
    dk, dl = fisher_jenks(dis, ia['dis_class_number'])

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
            x = np.where(grids[gid].wm[i] <= nk)[0]
            j = x.min() if x.size > 0 else len(nk) - 1
            x = np.where(grids[gid].wd[i] <= dk)[0]
            k = x.min() if x.size > 0 else len(dk) - 1
            nc = ia['color_scheme'][j][k]
            draw.polygon([cenx,ceny,cenx+xs[i], ceny+ys[i], cenx+xs[i+1], ceny+ys[i+1]], fill=nc, outline=nc)
        draw.polygon(border, outline = ia['border_color'])

    # -----------------------------draw legends-------------------------------
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 65)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 60)
    ls = ia['legend_size']
    bottom = ia['height'] - 180
    left = ia['width'] - 400

    for j in range(ia['mag_class_number']):
        for k in range(ia['dis_class_number']):
            draw.rectangle([(left+k*ls, bottom-j*ls),(left+(k+1)*ls, bottom-(j+1)*ls)], fill = ia['color_scheme'][j][k])

    draw.text((left - 350, bottom - ia['mag_class_number'] * ls / 2 - 30), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 140, bottom - 30), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left - 140, bottom - ia['mag_class_number'] * ls - 10), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    draw.text((left + ia['dis_class_number'] * ls / 2 - 90, bottom + 100), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 80, bottom + 20), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left + ia['dis_class_number'] * ls - 40, bottom + 20), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    # -----------------------------save figure-------------------------------
    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawHexagons_bs(draw, grids, gridWidth, area_scale, margin, dnum):
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * area_scale, dnum // 6)
    fxs, fys = computeCo(gridWidth + margin, dnum // 6)
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
    processGrids_fj(grids, flows, ia)

    iwidth = ia['width']
    iheight = ia['height']

    # RGB
    image = Image.new('RGB', (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])

    drawLabels(draw, grids, ia, scale)

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
    draw.text((mx-1.4*lw, sy-lh), 'Low', font=imageMeasureFont, fill=(0,0,0))
    draw.text((mx-1.4*lw, sy-lh*(ia['k_m']+1)), 'High', font=imageMeasureFont, fill=(0,0,0))

    # distance
    disx = iwidth - 260
    scale = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy-(i+0.35)*lh*scale, disx+lw, sy-(i+0.35)*lh*scale], width=int(round(lh*scale)), fill=n)
    draw.text((disx-lw*0.6, sy-(ia['k_m']+5)*lh), 'Distance', font=imageTitlefont, fill=(0,0,0))
    draw.text((disx+1.2*lw, sy-lh), 'Short', font=imageMeasureFont, fill=(0,0,0))
    draw.text((disx+1.2*lw, sy-lh*ia['k_m']-lh), 'Long', font=imageMeasureFont, fill=(0,0,0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


# highlighting single pattern
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

def drawsp(grids, flows, ia, scale, saveFileName):
    processGrids_fj(grids, flows, ia)
    image = Image.new('RGB', (500, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    cenx = 250
    ceny = 225
    drawSingleHexagon_bs(draw, grids[342], 240, 0.9, ia['dnum'], cenx, ceny)
    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])

# draw glyph
def drawglyph342(ia):
    dnum = ia['dnum']

    gridWidth = 240
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * 0.9, dnum // 6)

    #['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']
    ia['c_m'] = ['#303030', '#303030', '#9F9F9F', '#9F9F9F', '#DFDFDF', '#DFDFDF']
    ia['c_d'] = ['#e34a33', '#e34a33', '#fc8d59', '#fc8d59', '#fef0d9', '#fef0d9']

    image = Image.new('RGB', (500, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    cenx = 250
    ceny = 225
    for i in range(dnum):
        draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                      fill=ia['c_m'][i%dnum], outline=ia['c_m'][i])
        draw.polygon(
            [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                cenx + ixs[i + 1], ceny + iys[i + 1]], outline=ia['c_d'][i%dnum], fill=ia['c_d'][i%dnum])

    image.save('./figure/p_051316_1317_1km_pm_bs_3.jpg', quality=95, dpi=(1200, 1200))

# draw patterns with highlighting selected patterns
def drawPattern_bs_sp(grids, flows, ia, saveFileName):
    processGrids_fj(grids, flows, ia)

    iwidth = ia['width']
    iheight = ia['height']
    image = Image.new('RGB', (iwidth, iheight+530), '#ffffff')
    draw = ImageDraw.Draw(image)
    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])

    drawSingleHexagon_bs(draw, grids[124], 220, 0.8, ia['dnum'], 375, 3250)
    drawSingleHexagon_bs(draw, grids[437], 220, 0.8, ia['dnum'], 1125, 3250)
    drawSingleHexagon_bs(draw, grids[150], 220, 0.8, ia['dnum'], 1875, 3250)
    drawSingleHexagon_bs(draw, grids[392], 220, 0.8, ia['dnum'], 2625, 3250)

    labelfont = ImageFont.truetype('./font/times.ttf', 64)
    lineColor = '#5566ff'#'#0000ff'
    textColor = '#871F78'

    draw.line([grids[124].cenx, grids[124].ceny, 375, 3030], width=4, fill=lineColor)
    draw.line([grids[437].cenx, grids[437].ceny, 1125, 3030], width=4, fill=lineColor)
    draw.line([grids[150].cenx, grids[150].ceny, 1875, 3030], width=4, fill=lineColor)
    draw.line([grids[392].cenx, grids[392].ceny, 2625, 3030], width=4, fill=lineColor)

    draw.text((50, ia['height'] + 450), 'A: Beijing West Railway Station', font=labelfont, fill=textColor)
    draw.text((960, ia['height'] + 450), 'B: Wudaokou', font=labelfont, fill=textColor)
    draw.text((1610, ia['height'] + 450), 'C: The Forbidden City', font=labelfont, fill=textColor)
    draw.text((2500, ia['height'] + 450), 'D: Sanlitun', font=labelfont, fill=textColor)

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
    draw.text((mx - lw * 1.2, sy - (ia['k_m'] + 5) * lh), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - 1.4 * lw, sy - lh), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.4 * lw, sy - lh * (ia['k_m'] + 1)), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    # distance
    disx = iwidth - 260
    scale = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy - (i + 0.35) * lh * scale, disx + lw, sy - (i + 0.35) * lh * scale],
                  width=int(round(lh * scale)), fill=n)
    draw.text((disx - lw * 0.6, sy - (ia['k_m'] + 5) * lh), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh * ia['k_m'] - lh), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawDif_Kmeans(grids1, grids2, flows1, flows2, alpha, ia, saveFileName):
    k_dif = ia['k_dif']
    dif = cdif(grids1, grids2, flows1, flows2, alpha)
    dif_train = []
    for gid in grids1:
        dif_train.append(dif[gid])
    difk, difl = kmeans(dif_train, k_dif)

    c_dif = ia['c_dif']
    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']

    image = Image.new("RGB", (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    for gid in grids1:
        cenx, ceny = computeCen(gid, ia)
        hex_co = computeCo_hexagon(cenx, ceny, gridWidth)

        nc = c_dif[difl.index(difk.predict(dif[gid]))]
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

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawDif_fj(grids1, grids2, flows1, flows2, alpha, ia, saveFileName):
    k_dif = ia['k_dif']
    dif = cdif(grids1, grids2, flows1, flows2, alpha)
    dif_train = []
    for gid in grids1:
        dif_train.append(dif[gid])
    difk, difl = fisher_jenks(dif_train, k_dif)

    image = Image.new("RGB", (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    for gid in grids1:
        cenx, ceny = computeCen(gid, ia)
        hex_co = computeCo_hexagon(cenx, ceny, ia['gridWidth'])
        x = np.where(dif[gid] <= difk)[0]
        i = x.min() if x.size > 0 else len(difk) - 1
        nc = ia['c_dif'][i]

        co = []
        for item in hex_co:
            co.append(item[2])
            co.append(item[3])
        co.append(co[0])
        co.append(co[1])
        draw.polygon(co, fill=nc, outline=nc)

    # ----绘制图例----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 74)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 80)
    sy = ia['height'] - 50
    sx = ia['width'] - 400
    lh = ia['legend_height']
    lw = ia['legend_width']
    for i, c in enumerate(ia['c_dif']):
        draw.line([sx, sy - i * lh, sx + lw, sy - i * lh], width=lh, fill=c)

    draw.text((sx - lw, sy - (k_dif+2.5)*lh), 'Difference', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((sx + lw*1.2, sy - lh*0.7), 'Small', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((sx + lw*1.2, sy - lh*(k_dif+0.5)), 'Large', font=imageMeasureFont, fill=(0, 0, 0))

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


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

    Q1 = [6/13, 8/13, 13/13]
    Q2 = [7/13, 7/13, 10/13]
    Q3 = [2/13, 13/13, 13/13]

    x = np.array([i for i in range(1, 4)])
    fs1 = 12
    fs2 = 10

    fig, ax = plt.subplots()
    #ax.set_xlabel('', fontname="Times New Roman", fontsize=fs1)
    ax.set_ylabel('Accuracy', fontname="Times New Roman", fontsize=fs1)

    l1 = ax.bar(x-0.1, Q1, facecolor='#996699', width=0.1, label='Q1')
    l2 = ax.bar(x, Q2, facecolor='#99cccc', width=0.1, label='Q2')
    l3 = ax.bar(x+0.1, Q3, facecolor='#ccccff', width=0.1, label='Q3')

    ax.set_ylim(0, 1)
    ys = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    ax.set_xlim(0, 4)
    xs = [1, 2, 3]
    ax.set_xticks(xs)
    xlabels = ['The OD map', 'The diagram map', 'Our approach']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=[l1, l2, l3])
    for l in leg.get_texts():
        l.set_fontsize(fs2)
        l.set_fontname("Times New Roman")
    plt.show()