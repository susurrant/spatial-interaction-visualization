# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns
from func import *
import numpy as np


def drawSingleGlyph_bs(ia):
    dnum = ia['dnum']

    gridWidth = 240
    oxs, oys = computeCo(gridWidth, dnum // 6)
    ixs, iys = computeCo(gridWidth * 0.9, dnum // 6)

    image = Image.new('RGB', (830, 450), '#ffffff')
    draw = ImageDraw.Draw(image)
    cenx = 250
    ceny = 225
    mindex = [1, 4, 8, 10, 12, 14]
    dindex = [0, 1, 2, 3, 4, 2]
    for i in range(dnum):
        draw.polygon([cenx, ceny, cenx + ixs[i], ceny + iys[i], cenx + ixs[i + 1], ceny + iys[i + 1]],
                      fill=ia['c_m'][mindex[i]], outline=ia['c_m'][mindex[i]])
        draw.polygon(
            [cenx + ixs[i], ceny + iys[i], cenx + oxs[i], ceny + oys[i], cenx + oxs[i + 1], ceny + oys[i + 1],
                cenx + ixs[i + 1], ceny + iys[i + 1]], outline=ia['c_d'][dindex[i]], fill=ia['c_d'][dindex[i]])

    imageTitlefont = ImageFont.truetype('./font/arial.ttf', 28)
    imageMeasureFont = ImageFont.truetype('./font/arial.ttf', 26)
    sy = 450 - 100
    lh = 13
    lw = 40

    # magnitude
    mx = 830 - 230
    for i, c in enumerate(ia['c_m']):
        draw.line([mx, sy - i * lh, mx + lw, sy - i * lh], width=lh, fill=c)
    draw.text((mx - lw * 1.8, sy + lh*2), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - 1.4 * lw, sy - lh), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.4 * lw, sy - lh * (ia['k_m'] + 1)), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    # distance
    disx = 830 - 125
    scale = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy - (i + 0.35) * lh * scale, disx + lw, sy - (i + 0.35) * lh * scale],
                  width=int(round(lh * scale)), fill=n)
    draw.text((disx - lw *0.3, sy + lh*2), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh * ia['k_m'] - lh), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

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
    draw.text((left - 70, bottom - 35), '0', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left - 100, bottom - ia['mag_class_number'] * ls - 20), str(max(mag)), font=imageMeasureFont, fill=(0, 0, 0))

    draw.text((left + ia['dis_class_number'] * ls / 2 - 160, bottom + 100), 'Distance/km', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 40, bottom + 20), '0', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left + ia['dis_class_number'] * ls - 40, bottom + 20), '%.2f' % max(dis), font=imageMeasureFont, fill=(0, 0, 0))

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
        draw.line([grids[517].cenx, grids[517].ceny, 2800, 700], width=4, fill='#5566ff')
        draw.text((2820, 670), 'C', font=indicatorfont, fill=labelColor)
        draw.line([grids[487].cenx, grids[487].ceny, 160, 2000], width=4, fill='#5566ff')
        draw.text((110, 1980), 'D', font=indicatorfont, fill=labelColor)
        draw.text((grids[1716].cenx - dx, grids[1716].ceny - dy), 'B', font=indicatorfont, fill=labelColor)

        draw.text((30, ia['height'] - 260), 'A: The Forbidden City', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 200), 'B: Olympic Forest Park', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 140), 'C: Beijing Railway Station', font=labelfont, fill=textColor)
        draw.text((30, ia['height'] - 80), 'D: Beijing West Railway Station', font=labelfont, fill=textColor)


def drawLegend(draw, ia, max_mag, max_dis):
    '''
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
    '''
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 64)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 60)
    sy = ia['height'] - 50
    lh = ia['legend_height']
    lw = ia['legend_width']

    # magnitude
    mx = ia['width'] - 530
    for i, c in enumerate(ia['c_m']):
        draw.line([mx, sy - i * lh, mx + lw, sy - i * lh], width=lh, fill=c)
    draw.text((mx - lw * 1.2, sy - (ia['k_m'] + 5) * lh), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx - lw / 1.7, sy - lh), '0', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx - 1.1 * lw, sy - lh * (ia['k_m'] + 1)), str(max_mag), font=imageMeasureFont, fill=(0, 0, 0))

    # distance
    disx = ia['width'] - 260
    s = ia['k_m'] / ia['k_d']
    for i, n in enumerate(ia['c_d']):
        draw.line([disx, sy - (i + 0.35) * lh * s, disx + lw, sy - (i + 0.35) * lh * s], width=int(round(lh * s)),
                  fill=n)
    draw.text((disx - lw * 0.8, sy - (ia['k_m'] + 5) * lh), 'Distance/km', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh), '0', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((disx + 1.2 * lw, sy - lh * ia['k_m'] - lh), str('%.2f' % max_dis), font=imageMeasureFont, fill=(0, 0, 0))


def drawPattern_bs(grids, flows, ia, scale, saveFileName):
    max_mag, max_dis = processGrids_fj(grids, flows, ia)

    # RGB
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    drawHexagons_bs(draw, grids, ia['gridWidth'], ia['area_scale'], ia['margin'], ia['dnum'])
    drawLabels(draw, grids, ia, scale)
    drawLegend(draw, ia, max_mag, max_dis)

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


# draw patterns with highlighting selected patterns
def drawPattern_bs_sp(grids, flows, ia, saveFileName):
    max_mag, max_dis = processGrids_fj(grids, flows, ia)

    image = Image.new('RGB', (ia['width'], ia['height']+530), '#ffffff')
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

    drawLegend(draw, ia, max_mag, max_dis)

    image.save(saveFileName, quality=ia['quality'], dpi=ia['dpi'])


def drawDif_fj(grids1, grids2, flows1, flows2, alpha, ia, saveFileName):
    k_dif = ia['k_dif']
    dif, gid_nodata = cdif(grids1, grids2, flows1, flows2, alpha)
    dif_train = []
    for gid in dif:
        dif_train.append(dif[gid])
    difk, difl = fisher_jenks(dif_train, k_dif)

    image = Image.new("RGB", (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    for gid in grids1:
        cenx, ceny = computeCen(gid, ia)
        hex_co = computeCo_hexagon(cenx, ceny, ia['gridWidth'])
        co = []
        for item in hex_co:
            co.append(item[2])
            co.append(item[3])
        co.append(co[0])
        co.append(co[1])
        if gid in gid_nodata:
            draw.polygon(co, fill=None, outline=ia['c_dif'][0])
        else:
            x = np.where(dif[gid] <= difk)[0]
            i = x.min() if x.size > 0 else len(difk) - 1
            nc = ia['c_dif'][i]
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


def user_accu():
    sns.set(style="whitegrid")

    user_num = 27
    # OD, DM, PM
    ra = np.array([[23, 24, 27],  # Q1
                   [22, 19, 16],  # Q2
                   [5, 20, 23],  # Q3
                   [15, 16, 24],  # Q4
                   [21, 22, 25],  # Q5
                   [18, 17, 27]]) / user_num  # Q6

    x = np.array([0.5, 1.5, 2.5])
    fs1 = 14
    fs2 = 12
    colors = ['#d73027', '#f46d43', '#fdae61', '#fee090', '#91bfdb', '#4575b4']
    colors = ['#d73027', '#fdae61', '#1b7837', '#7fbf7b', '#762a83', '#af8dc3']

    fig, ax = plt.subplots(figsize=(7, 3))
    # ax.set_xlabel('', fontname="Times New Roman", fontsize=fs1)
    ax.set_ylabel('Accuracy', fontname="Times New Roman", fontsize=fs1)

    bw = 0.11
    ll = []
    for n, i in enumerate([-5, -3, -1, 1, 3, 5]):
        ll.append(ax.bar(x + i * bw / 2, ra[n], facecolor=colors[n], width=bw, label='Q' + str(n + 1)))

    ax.set_ylim(0, 1)
    ys = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    ax.set_xlim(0, 3.4)
    xs = [0.5, 1.5, 2.5]
    ax.set_xticks(xs)
    xlabels = ['OD map', 'Diagram map', 'Direction-based pattern map']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=ll)
    for l in leg.get_texts():
        l.set_fontsize(10)
        l.set_fontname("Times New Roman")
    plt.show()


def user_resTime():
    ticks = ['OD map', 'Diagram map', 'Direction-based pattern map']
    t1 = [[6.3, 14.2, 12.2, 9.1, 11.7, 11.4], [7.1, 15.2, 4.9, 6.4, 3.8, 23.6, 8.0],
          [8.3, 8.1, 5.7, 2.3, 2.4, 6.5, 3.4, 3.7, 2.3, 3.7, 2.8]]
    t2 = [[24.7, 25.6, 27.8, 13.2, 21.9, 25.6, 33.1, 31.6], [9.7, 13.5, 15.0, 17.7, 6, 11.5, 15.9, 16.5, 9.3],
          [10.6, 7.2, 10.2, 11, 10.8, 8.9, 8.6, 5.2]]
    t3 = [[22.6, 24.3, 27.6], [23.4, 15.4, 4.7, 20.2, 12.2], [17.6, 8.8, 8.1, 11.5, 7.8, 9.6, 8.2]]
    t4 = [[13.0, 19.1, 18.8, 16.4, 18.6, 19.5, 15.2], [13.8, 11.9, 6.1, 15.7, 11.8, 10.4],
          [8.6, 9.8, 9.5, 5.3, 12.4, 5.8, 10.1, 4.5]]
    t5 = [[16.4, 10.8, 19.9, 9.5, 20.2, 21.1, 18.7, 11.2], [8.1, 6.2, 9.6, 9.7, 10.3, 10.1],
          [4, 3.2, 3.2, 3.0, 6.3, 5.2, 5.1, 4.6]]
    t6 = [[22.7, 25.7, 13.2, 21.8], [23.4, 18.4, 10.2, 8.3, 15, 8.2, 7.4],
          [7.4, 2.7, 2.9, 2.1, 4.3, 3.8, 7.3, 7.3, 4.2]]
    t = [t1, t2, t3, t4, t5, t6]
    fs1 = 14
    fs2 = 12

    fig, ax = plt.subplots(figsize=(7, 3))
    colors = ['#d73027', '#f46d43', '#fdae61', '#fee090', '#91bfdb', '#4575b4']
    colors = ['#d73027', '#fdae61', '#1b7837', '#7fbf7b', '#762a83', '#af8dc3']
    ax.set_ylabel('Time/s', fontname="Times New Roman", fontsize=fs1)
    xs = np.array([0.5, 1.5, 2.5])

    def set_box_color(bp, color):
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        plt.setp(bp['medians'], color=color)

    bw = 0.1
    margin = 0.05
    for n, i in enumerate([-5, -3, -1, 1, 3, 5]):
        bp = ax.boxplot(t[n], positions=xs + (bw + margin / 2) * i / 2, sym='', widths=bw)
        set_box_color(bp, colors[n])

    ax.set_xlim(0, 3)
    ax.set_xticks(xs)
    ax.xaxis.set_ticklabels(ticks, fontname="Times New Roman", fontsize=fs2)

    ax.set_ylim(0, 35)
    ys = [0, 5, 10, 15, 20, 25, 30, 35]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    for i in range(6):
        ax.plot([], c=colors[i], label='Q' + str(i + 1))
    ax.legend()

    plt.show()