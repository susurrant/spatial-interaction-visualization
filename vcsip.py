# -*- coding: utf-8 -*-：

from grid import *
from draw import *
from LL2UTM import LL2UTM_USGS

# 读取数据
def readData(filename, dgids, dnum, minSpeed = 2, maxSpeed = 150):
    flows = {}
    grids = {}
    for gid in dgids:
        grids[gid] = Grid(gid, dnum)

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
def readData_Inside(filename, dnum, minSpeed = 2, maxSpeed = 150):
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

# 读取要绘制的网格编号
def readGids(fileName):
    dgids = set()
    with open(fileName, 'r') as f:
        lines = f.readlines()
        del lines[0]
        for line in lines:
            sl = line.strip().split(',')
            dgids.add(int(sl[-1]))
    return dgids

# 交互模式可视化
def drawSIPattern(fileName, dgids, dnum, ia, inside=False):
    if inside:
        grids, flows = readData_Inside(fileName+'.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '_in.jpg'
    else:
        grids, flows = readData(fileName + '.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '.jpg'

    drawPattern(grids, flows, dnum, ia, saveFileName)

# 模式差异可视化
def drawDifference(fileName1, fileName2, dgids, dnum, ia, alpha):
    ia['legendWidth'] = 15
    grids1, flows1 = readData(fileName1 + '.csv', dgids, dnum)
    grids2, flows2 = readData(fileName2 + '.csv', dgids, dnum)
    saveFileName = './figure/d_' + fileName1[-15:-4]+'-'+fileName2[-8:]+'_'+str(alpha)+'.jpg'
    drawCdif_Kmeans(grids1, grids2, flows1, flows2, alpha, ia, saveFileName)

# 差异时变
def drawDifVar(fs, dgids, gids, labels, colors, alpha, dnum):
    grids = []
    flows = []
    for fn in fs:
        g, f = readData(fn + '.csv', dgids, dnum)
        grids.append(g)
        flows.append(f)
    gdif = cdif_multi(grids, flows, alpha)
    drawCdifDistribution(gids, gdif, colors, labels)

# 读取渲染设置
def readDrawingSetting(scale):
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   hexparm: 网格参数(每行六边形数, 总六边形个数的一半)
    #   网格：gridWidth：网格尺寸；margin：网格间隙宽
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度；
    #   图例：legendWidth：图例条基本宽度；；legend_yoffset：图例相对右下角点的纵向偏移；legend_xoffset：图例相对右下角点的横向偏移
    #   聚类数：dis_class_number、dis_class_number、k_dif；颜色：color_scheme、c_dif
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 84, 'ox': 30, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000, 'xoffset': 3, 'yoffset': 3,
              'legend_size': 63, 'legend_yoffset': 130, 'legend_xoffset': 150,
              'mag_class_number': 6, 'dis_class_number': 4, 'k_dif': 10, 'c_dif': [],
              'quality': 95, 'dpi': (1200, 1200)}
    elif scale == '500m':
        ia = {'hexParm': (24, 960), 'gridWidth': 38, 'gridBorderWidth': 9, 'ox': -10, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 1, 'yoffset': 6, 'frameMargin': 2, 'legendWidth': 20, 'quality': 1000, 'dpi': (1200, 1200),
              'mag_class_number': 5, 'dis_class_number': 5, 'k_dif': 10, 'c_dif': []}


    # color setting
    ia['border_color'] = '#000000'
    # green-pink
    ia['color_scheme0'] = [['#ffffff', '#d7eadf', '#b2d8c3', '#8dc6ab', '#69b995'],
                           ['#f4cbdc', '#d4bdc5', '#b6b3b2', '#95a69a', '#779b87'],
                           ['#e29abb', '#cb91a8', '#b18a99', '#97858a', '#7d7e7b'],
                           ['#d2699c', '#c4658e', '#ad6383', '#965e77', '#7f5c6b'],
                           ['#c73984', '#be3c7b', '#a93d70', '#933c67', '#7e3d5d']]
    # blue-orange
    ia['color_scheme2'] = [['#ffffff', '#d3e2f1', '#a7c7e4', '#78abd7', '#3192c8'],
                          ['#f9dacc', '#d4cccb', '#aabcc6', '#7caac0', '#3a93b4'],
                          ['#f1b69b', '#cfab9b', '#aea19a', '#849599', '#4c8695'],
                          ['#e99567', '#cc8d69', '#ac856a', '#897d6d', '#59726d'],
                          ['#e47920', '#c7722a', '#aa6d2f', '#8b6736', '#5f613c']]

    # blue-red
    ia['color_scheme1'] = [['#ffffff', '#c7c5df', '#8f90c0', '#535a9f', '#253f8e'],
                           ['#f4c5c6', '#c7b5c3', '#9191b2', '#555c95', '#264285'],
                           ['#e88f91', '#c18690', '#947b91', '#565f86', '#284478'],
                           ['#de5d5c', '#bb595f', '#945361', '#5e4e65', '#294663'],
                           ['#d8211c', '#b72825', '#932c2c', '#633233', '#383336']]

    # blue-orange
    ia['color_scheme'] = [['#ffffff', '#c4d9ed', '#8ab6dc', '#3192c8'],
                           ['#fae0d7', '#c7cdd4', '#8cb5cb', '#3993ba'],
                           ['#f3c3ae', '#c6b3af', '#91a3ab', '#438da4'],
                           ['#eea787', '#c39c88', '#97908a', '#527d86'],
                           ['#e88f5b', '#c1855f', '#987b62', '#5b6f65'],
                           ['#e47920', '#be712b', '#966933', '#5f613c']]

    # blue to red
    rgbcolor = [(153, 153, 255), (156, 187, 255), (156, 222, 255), (153, 255, 255), (194, 255, 220),
                (227, 255, 186), (255, 255, 153), (255, 221, 153), (255, 187, 153), (255, 153, 153)]
    for color in rgbcolor:
        ia['c_dif'].append('#%02X%02X%02X' % color)

    return ia


if __name__ == '__main__':
    # -----------------------------data----------------------------------
    fileNames = ['./data/sj_051316_0105','./data/sj_051316_0509', './data/sj_051316_0913',
                 './data/sj_051316_1317', './data/sj_051316_1721', './data/sj_051316_2101']

    scale = '_1km'
    dnum = 6
    dgids = readGids('./data/5th_rr_gid'+scale+'.csv')
    ia = readDrawingSetting(scale[1:])

    # -----------------------------drawing--------------------------------
    #drawGridSymbol_hexagon(ia['c_d'])False

    drawSIPattern(fileNames[1]+scale, dgids, dnum, ia, False) #True 表示只显示五环内的数据

    #drawDifference(fileNames[1]+scale, fileNames[4]+scale, dgids, dnum, ia, 0.7)

    if False:
        labels = ['T', 'S', 'C', 'R']
        gids = [487, 563, 800, 1455]   #scale = 500m
        gids = [124, 150, 437, 356]    #scale = 1km
        colors = ['#eaff56', '#44cef6', '#ff461f', '#bddd22']
        drawDifVar([fileNames[i]+scale for i in [1,0,2,3,4,5]], dgids, gids, labels, colors, 0.7, dnum)

    #userScore()