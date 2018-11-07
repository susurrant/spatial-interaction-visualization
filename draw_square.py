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
