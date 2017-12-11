# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
from LL2UTM import LL2UTM_USGS
from draw import kmeans, computeCen
import numpy as np


# 读取五环内的交互，供drawSIPattern使用
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

                fid = int(sl1[-4])
                ogid = int(sl1[-1])
                dgid = int(sl2[-1])

                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))
                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))

                flows_co[fid] = [(ox, oy), (dx, dy)]

                if ogid not in grids:
                    grids[ogid] = Grid(ogid, dnum)
                if dgid not in grids:
                    grids[dgid] = Grid(dgid, dnum)

                grids[ogid].addOutFlow(fid)
                grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows_co

def  drawDiagramMap(grids, flows, dnum, ia):
    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[g].ld:
            dis.extend(ld)
    dk, dl = kmeans(dis, ia['class_number'])

    grid_sta = {}
    maxmag = 0
    for gid in grids:
        grid_sta[gid] = []
        for i in range(dnum):
            grid_sta[gid].append([0, 0, 0])
        for j, ld in enumerate(grids.ld):
            for d in ld:
                idx = dl.index(dk.predict(d))
                grid_sta[gid][j][idx] += 1
        for maglist in grid_sta[gid]:
            for num in maglist:
                if num > maxmag:
                    maxmag = num

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if dnum == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    radius = ia['radius']
    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            r = np.cumsum(np.array(grid_sta[gid][i])*radius/maxmag)
            for j in range(ia['class_number']-1, -1, -1):
                draw.pieslice([cenx-r[j], ceny-r[j], cenx+r[j], ceny+r[j]], angle[i][0], angle[i][1],
                              fill=ia['color_scheme'][j])


# 读取渲染设置
def readDrawingSetting():
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   rows, columns: 网格行数、列数; gridWidth：网格尺寸
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度
    #   legendWidth：图例条基本宽度; radius：扇形符号最大半径
    #   class_number： 聚类数；color_scheme： 颜色
    ia = dict()
    ia.update({'hexParm': (12, 240), 'gridWidth': 84, 'ox': 30, 'oy': 40, 'margin': 0, 'width': 3000, 'height': 3000,
               'xoffset': 3, 'yoffset': 3, 'legend_size': 63, 'radius': 100, 'quality': 95, 'dpi': (1200, 1200)})

    # color setting
    ia['border_color'] = '#000000'
    ia['color_scheme'] = ['', '', '']
    ia['class_number'] = len(ia['color_scheme'])
    return ia


if __name__ == '__main__':
    grids, flows = readData_Inside('./data/sj_051316_1721_1km.csv', 6)
    saveFileName = './figure/dm_051316_1721_1km_5rr.jpg'
    ia = readDrawingSetting()

    drawDiagramMap(grids, flows, 6, ia)

