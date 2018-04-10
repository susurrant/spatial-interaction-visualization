# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
from LL2UTM import LL2UTM_USGS
from draw import kmeans, computeCen, computeCo, fisher_jenks
import numpy as np
from grid import Grid
import style
import csv


# 读取五环内的交互
def readData_Inside(filename, dnum, minSpeed=2, maxSpeed=150):
    flows_co = {}
    grids = {}

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

                ogid = int(sl1[-1])
                dgid = int(sl2[-1])
                if ogid not in grids:
                    grids[ogid] = Grid(ogid, dnum)
                if dgid not in grids:
                    grids[dgid] = Grid(dgid, dnum)

                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))
                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))
                if np.sqrt((dx-ox)**2+(dy-oy)**2) <= 500:
                    grids[ogid].round_flow_num += 1
                    continue

                fid = int(sl1[-4])
                flows_co[fid] = [(ox, oy), (dx, dy)]

                grids[ogid].addOutFlow(fid)
                grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows_co

def readData_with_zones(filename, zones, dnum, minSpeed=2, maxSpeed=150):
    flows_co = {}
    grids = {}
    for rid in zones:
        grids[rid] = Grid(rid, dnum)

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

                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))

                ogid = -1
                mindis = float('inf')
                for rid in zones:
                    dis = np.sqrt((ox - zones[rid][0]) ** 2 + (oy - zones[rid][1]) ** 2)
                    if  dis < mindis:
                        ogid = rid
                        mindis = dis
                if ogid == -1:
                    print('cannot find ogid.')
                    continue

                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))
                '''
                dgid = -1
                mindis = float('inf')
                for rid in zones:
                    dis = np.sqrt((dx - zones[rid][0]) ** 2 + (dy - zones[rid][1]) ** 2)
                    if dis < mindis:
                        dgid = rid
                        mindis = dis
                if dgid == -1:
                    print('cannot find dgid.')
                    continue
                    
                if np.sqrt((dx - ox) ** 2 + (dy - oy) ** 2) <= 500:
                    grids[ogid].round_flow_num += 1
                    continue
                '''
                fid = int(sl1[-4])
                flows_co[fid] = [(ox, oy), (dx, dy)]

                grids[ogid].addOutFlow(fid)
                #grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows_co

def statistic_kmeans(data_file, dis_class_num, dnum):
    grids, flows = readData_Inside(data_file, dnum)
    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[gid].ld:
            dis.extend(ld)
    dk, dl = kmeans(dis, dis_class_num)

    grid_sta = {}
    round_flow = {}
    maxmag = 0
    for gid in grids:
        grid_sta[gid] = []
        for i in range(dnum):
            grid_sta[gid].append([0, 0, 0])
        for j, ld in enumerate(grids[gid].ld):
            for d in ld:
                idx = dl.index(dk.predict(d))
                grid_sta[gid][j][idx] += 1
        for maglist in grid_sta[gid]:
            for num in maglist:
                if num > maxmag:
                    maxmag = num
        if grids[gid].round_flow_num > maxmag:
            maxmag = grids[gid].round_flow_num
        round_flow[gid] = grids[gid].round_flow_num

    return grid_sta, round_flow, maxmag

def statistic_fj(data_file, dis_class_num, dnum):
    grids, flows = readData_Inside(data_file, dnum)
    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[gid].ld:
            dis.extend(ld)
    dk, dl = fisher_jenks(dis, dis_class_num)

    grid_sta = {}
    round_flow = {}
    maxmag = 0
    for gid in grids:
        grid_sta[gid] = []
        for i in range(dnum):
            grid_sta[gid].append([0, 0, 0])
        for j, ld in enumerate(grids[gid].ld):
            uptos = [np.where(value <= dk)[0] for value in ld]
            for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
                grid_sta[gid][j][i] += 1
        for maglist in grid_sta[gid]:
            for num in maglist:
                if num > maxmag:
                    maxmag = num
        if grids[gid].round_flow_num > maxmag:
            maxmag = grids[gid].round_flow_num
        round_flow[gid] = grids[gid].round_flow_num

    return grid_sta, round_flow, maxmag

def write(grids, fn):
    with open(fn, 'w', newline='') as f:
        sheet = csv.writer(f)
        for gid in grids:
            d = [gid]
            for ld in grids[gid]:
                d.extend(ld)
            sheet.writerow(d)

def statistic_dif(data_file, data_file_c, zones, ia):
    # 时间段1的分布统计：data_file
    grids, flows = readData_Inside(data_file, ia['dnum'])
    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[gid].ld:
            dis.extend(ld)
    dk, dl = fisher_jenks(dis, ia['dis_class_num'])

    grid_sta = {}
    for gid in grids:
        grid_sta[gid] = []
        for i in range(ia['dnum']):
            grid_sta[gid].append([0, 0, 0])
        for j, ld in enumerate(grids[gid].ld):
            uptos = [np.where(value <= dk)[0] for value in ld]
            for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
                grid_sta[gid][j][i] += 1
    #write(grid_sta, '1.csv')

    # 时间段2的分布统计：data_file_c
    grids_c, flows_c = readData_with_zones(data_file_c, zones, ia['dnum'])
    for gid in grids_c:
        grids_c[gid].calcOutList(flows_c)
    grid_sta_c = {}
    for gid in grids_c:
        grid_sta_c[gid] = []
        for i in range(ia['dnum']):
            grid_sta_c[gid].append([0, 0, 0])
        for j, ld in enumerate(grids_c[gid].ld):
            uptos = [np.where(value <= dk)[0] for value in ld]
            for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
                grid_sta_c[gid][j][i] += 1

    #write(grid_sta_c, '2.csv')

    # 求差
    grid_dif = {}
    dif = []
    for gid in grid_sta:
        grid_dif[gid] = []
        for i in range(ia['dnum']):
            grid_dif[gid].append([abs(grid_sta[gid][i][0]-grid_sta_c[gid][i][0]), abs(grid_sta[gid][i][1]-grid_sta_c[gid][i][1])
                                     , abs(grid_sta[gid][i][2]-grid_sta_c[gid][i][2])])
            dif.extend(grid_dif[gid][i])
            #print(grid_dif[gid][i])
        round_dif = abs(grids[gid].round_flow_num - grids_c[gid].round_flow_num)
        grid_dif[gid].append([round_dif])
        dif.append(round_dif)
    fk, fl = fisher_jenks(dif, ia['dif_class_num'])
    #print(fk)

    # 设置颜色
    rgrids = {}
    for gid in grid_dif:
        rgrids[gid] = []
        for j, dif in enumerate(grid_dif[gid]):
            rgrids[gid].append([])
            uptos = [np.where(value <= fk)[0] for value in dif]
            for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
                rgrids[gid][j].append(ia['c_dif'][i])

    return rgrids

def statistic_class(data_file, dis_class_num, mag_class_num, dnum, radius):
    grids, flows = readData_Inside(data_file, dnum)

    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[gid].ld:
            dis.extend(ld)
    dk, dl = fisher_jenks(dis, dis_class_num)

    grid_sta = {}
    for gid in grids:
        grid_sta[gid] = []
        for i in range(dnum):
            grid_sta[gid].append([0, 0, 0])

        for j, ld in enumerate(grids[gid].ld):
            uptos = [np.where(value <= dk)[0] for value in ld]
            for i in [x.min() if x.size > 0 else len(dk) - 1 for x in uptos]:
                grid_sta[gid][j][i] += 1

        grid_sta[gid].append([grids[gid].round_flow_num])

    mag = []
    rgrids = {}
    for gid in grid_sta:
        for mlist in grid_sta[gid]:
            mag.extend(mlist)
    mk, ml = fisher_jenks(mag, mag_class_num)

    radii = []
    for i in range(mag_class_num):
        #radii.append((ml[i] / ml[-1]) * radius)
        radii.append(((i+1) / 15) * radius)

    for gid in grid_sta:
        rgrids[gid] = []
        for i in range(dnum+1):
            rgrids[gid].append([])

        for j, ld in enumerate(grid_sta[gid]):
            uptos = [np.where(value <= mk)[0] for value in ld]
            for i in [x.min() if x.size > 0 else len(mk) - 1 for x in uptos]:
                rgrids[gid][j].append(radii[i])
            if j < dnum:
                rgrids[gid][j][1] += rgrids[gid][j][0]
                rgrids[gid][j][2] += rgrids[gid][j][1]

    return rgrids

def drawDiagramMap_AJ1(data_file, ia, save_file, dnum=6):
    grid_sta, round_flow, maxmag = statistic_kmeans(data_file, ia['class_num'], dnum)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    angle = [330, 270, 210, 150, 90, 30]
    radii = ia['radii']

    for gid in grid_sta:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            r = np.array(grid_sta[gid][i])*60/maxmag
            for j in range(ia['class_num']-1,-1,-1):
                draw.pieslice([cenx-radii[j], ceny-radii[j], cenx+radii[j], ceny+radii[j]], angle[i]-r[j], angle[i]+r[j],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        #r = round_flow[gid]*radius/maxmag
        #draw.arc([cenx-r, ceny-r, cenx+r, ceny+r], 0, 360, fill='#323232')

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])

def readZones(file_name):
    zones = {}
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            sl = line.strip().split(',')
            zones[int(sl[0])] = (float(sl[1]), float(sl[2]))
    return zones

def drawRingRoad(draw, file_name, xoff, yoff):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        tag = 0
        pts = []
        for line in lines[1:]:
            sl = line.strip().split(',')
            x, y = LL2UTM_USGS(float(sl[3]), float(sl[2]))
            x = (x - xoff) / 10
            y = ia['height'] - (y - yoff) / 10
            if int(sl[1]) == tag:
                pts.append((x, y))
            else:
                draw.line(pts, fill='#000000', width=2)
                tag = int(sl[1])
                pts = [(x, y)]
        draw.line(pts, fill='#000000', width=2)

def drawRoundTrip(draw, cenx, ceny, r):
    a = np.arange(0, 360, 10) * 2 * np.pi / 360
    xs = cenx + r * np.cos(a)
    ys = ceny + r * np.sin(a)
    for x, y in zip(xs, ys):
        draw.ellipse([x-1,y-1,x+1,y+1], fill='#323232')

# 按比例连续设置扇形半径
def drawDiagramMap_RO1_proportion(data_file, zone_file, save_file, ia):
    grid_sta, round_flow, maxmag = statistic_fj(data_file, ia['dis_class_num'], ia['dnum'])
    zones = readZones(zone_file)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if ia['dnum'] == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    radius = ia['radius']
    xoff = 431500
    yoff = 4400700

    drawRingRoad(draw, './data/ringroad_pt.csv', xoff, yoff)

    for gid in grid_sta:
        cenx, ceny = zones[gid]
        cenx = (cenx - xoff) / 10
        ceny = ia['height'] - (ceny - yoff) / 10
        for i in range(ia['dnum']):
            r = np.cumsum(np.array(grid_sta[gid][i])*radius/maxmag)
            for j in range(ia['dis_class_num']-1, -1, -1):
                draw.pieslice([cenx-r[j], ceny-r[j], cenx+r[j], ceny+r[j]], angle[i][0], angle[i][1],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        r = round_flow[gid]*radius/maxmag
        drawRoundTrip(draw, cenx, ceny, r)

    labelfont = ImageFont.truetype('./font/calibril.ttf', 110)
    draw.text((930, 1480), 'A', font=labelfont, fill=(0, 0, 0))
    draw.text((2310, 1560), 'B', font=labelfont, fill=(0, 0, 0))
    draw.text((1570, 550), 'C', font=labelfont, fill=(0, 0, 0))
    left = 650
    right = 1230
    top = 380
    bottom = 920
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill='#0000ff', width=4)
    draw.text((left+20, top+20), 'D', font=labelfont, fill=(0, 0, 0))

    x = ia['width'] - 700
    y = ia['height'] - 200
    legend_size = ia['legend_size']
    for j in range(ia['dis_class_num'] - 1, -1, -1):
        r = (j+1)*legend_size/ia['dis_class_num']
        draw.pieslice([x - r, y - r, x + r, y + r], 300, 0, fill=ia['color_scheme'][j], outline='#fe0000')
    draw.pieslice([x - legend_size + 400, y - legend_size, x + legend_size + 400, y + legend_size], 300, 0, fill=None, outline='#fe0000')
    #draw.arc([x + 500 - legend_size/3, y - 400 - legend_size/3, x + 500 + legend_size/3, y - 400 + legend_size/3], 0, 360, fill='#323232')
    drawRoundTrip(draw, x + 500, y - 400, legend_size/3)
    px = x + 400
    draw.line([px, y, px + np.sqrt(3)*legend_size/2, y - legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-20, y-legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-12, y-legend_size/2+19], width=1, fill='#000000')

    imagescalefont = ImageFont.truetype('./font/times.ttf', 40)
    draw.text((x - 110, y - 40), 'Short', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 110, y - 130), 'Medium', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 20, y - 200), 'Long', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px - 50, y + 10), 'Low', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px + 180, y + 10), 'High', font=imagescalefont, fill=(0, 0, 0))

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 50)
    draw.text((x, y + 60), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((px, y + 60), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((x + 380, y - 310), 'Round trips', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])

# 按分级等间隔设置半径
def drawDiagramMap_RO1_class(data_file, zone_file, save_file, ia):
    grid_sta = statistic_class(data_file, ia['dis_class_num'], ia['mag_class_num'], ia['dnum'], ia['radius'])
    zones = readZones(zone_file)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if ia['dnum'] == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    xoff = 431500
    yoff = 4400700

    drawRingRoad(draw, './data/ringroad_pt.csv', xoff, yoff)

    for gid in grid_sta:
        cenx, ceny = zones[gid]
        cenx = (cenx - xoff) / 10
        ceny = ia['height'] - (ceny - yoff) / 10
        for i in range(ia['dnum']):
            for j in range(ia['dis_class_num']-1, -1, -1):
                r = grid_sta[gid][i][j]
                draw.pieslice([cenx-r, ceny-r, cenx+r, ceny+r], angle[i][0], angle[i][1],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        drawRoundTrip(draw, cenx, ceny, grid_sta[gid][ia['dnum']][0])

    labelfont = ImageFont.truetype('./font/calibril.ttf', 110)
    draw.text((930, 1480), 'A', font=labelfont, fill=(0, 0, 0))
    draw.text((2310, 1560), 'B', font=labelfont, fill=(0, 0, 0))
    draw.text((1570, 550), 'C', font=labelfont, fill=(0, 0, 0))
    left = 650
    right = 1230
    top = 380
    bottom = 920
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill='#0000ff', width=4)
    draw.text((left+20, top+20), 'D', font=labelfont, fill=(0, 0, 0))

    x = ia['width'] - 700
    y = ia['height'] - 200
    legend_size = ia['legend_size']
    for j in range(ia['dis_class_num'] - 1, -1, -1):
        r = (j+1)*legend_size/ia['dis_class_num']
        draw.pieslice([x - r, y - r, x + r, y + r], 300, 0, fill=ia['color_scheme'][j], outline='#fe0000')
    draw.pieslice([x - legend_size + 400, y - legend_size, x + legend_size + 400, y + legend_size], 300, 0, fill=None, outline='#fe0000')
    drawRoundTrip(draw, x + 500, y - 400, legend_size/4)
    px = x + 400
    draw.line([px, y, px + np.sqrt(3)*legend_size/2, y - legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-20, y-legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-12, y-legend_size/2+19], width=1, fill='#000000')

    imagescalefont = ImageFont.truetype('./font/times.ttf', 55)
    draw.text((x - 150, y - 50), 'Short', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 155, y - 130), 'Medium', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 60, y - 200), 'Long', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px - 60, y + 10), 'Low', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px + 170, y + 10), 'High', font=imagescalefont, fill=(0, 0, 0))

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 65)
    draw.text((x-20, y + 80), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((px-20, y + 80), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 55)
    draw.text((x + 380, y - 310), 'Round trips', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])

def drawDifferenceMap_CJ(data_file, zone_file, data_file_c, save_file, ia):
    zones = readZones(zone_file)
    grid_sta = statistic_dif(data_file, data_file_c, zones, ia)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if ia['dnum'] == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    radii = ia['radii']
    xoff = 431500
    yoff = 4400700

    drawRingRoad(draw, './data/ringroad_pt.csv', xoff, yoff)

    for gid in grid_sta:
        cenx, ceny = zones[gid]
        cenx = (cenx - xoff) / 10
        ceny = ia['height'] - (ceny - yoff) / 10
        for i in range(ia['dnum']):
            for j in range(ia['dis_class_num'] - 1, -1, -1):
                draw.pieslice([cenx - radii[j], ceny - radii[j], cenx + radii[j], ceny + radii[j]], angle[i][0], angle[i][1],
                              fill=grid_sta[gid][i][j], outline='#fe0000')
        draw.ellipse([cenx-ia['round_radius'],ceny-ia['round_radius'],cenx+ia['round_radius'],ceny+ia['round_radius']],
                     fill=grid_sta[gid][ia['dnum']][0], outline='#fe0000')

    x = ia['width'] - 600
    y = ia['height'] - 200
    for i in range(ia['dif_class_num']):
        draw.rectangle([x + i * ia['legend_width'], y - ia['legend_height'], x + (i + 1) * ia['legend_width'], y],
                       fill=ia['c_dif'][i])
    imagescalefont = ImageFont.truetype('./font/times.ttf', 50)
    draw.text((x - 70, y + 20), 'Small', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x + ia['dif_class_num']*ia['legend_width']-50, y + 20), 'Large', font=imagescalefont, fill=(0, 0, 0))

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])


if __name__ == '__main__':
    mode = 'dm_dif'
    data_file = './data/sj_051316_1721_5rr_gp.csv'
    zone_file = './data/group_051316_1721_r3km.csv'
    save_file = './figure/dm_dif_051316_1721_3km_5rr_'+mode+'.jpg'
    ia = style.readDrawingSetting(mode)

    #drawDiagramMap_RO1_class(data_file, zone_file, save_file, ia)

    data_file_c = './data/sj_051316_0509_5rr.csv'
    drawDifferenceMap_CJ(data_file, zone_file, data_file_c, save_file, ia)
