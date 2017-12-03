# -*- coding: utf-8 -*-：

from grid import *
from LL2UTM import LL2UTM_USGS


# 读取五环内的交互，供交互矩阵、流地图使用
def readData(filename, minSpeed=2, maxSpeed=150):
    grids = {}
    flows = {}

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if float(sl[-2]) < minSpeed or float(sl[-2]) > maxSpeed:
                    continue

                fid = int(sl[-4])
                if fid not in flows:
                    flows[fid] = [-1, -1]
                gid = int(sl[-1])
                if sl[-3] == '1':
                    flows[fid][0] = gid
                elif sl[-3] == '0':
                    flows[fid][1] = gid
            else:
                break

    for fid in flows:
        if flows[fid][0] in dgids and flows[fid][1] in dgids:
            if tuple(flows[fid]) not in grids:
                grids[tuple(flows[fid])] = 0
            grids[tuple(flows[fid])] += 1

    return grids


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
def drawODMap(fileName, dgids, dnum, ia, inside=False):
    if inside:
        grids, flows = readData_Inside(fileName + '.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '_in.jpg'
    else:
        grids, flows = readData(fileName + '.csv', dgids, dnum)
        saveFileName = './figure/p_' + fileName[-15:] + '.jpg'

    drawPattern(grids, flows, dnum, ia, saveFileName)



# 读取渲染设置
def readDrawingSetting(scale):
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   hexparm: 网格参数(每行六边形数, 总六边形个数的一半)
    #   网格：gridWidth：网格尺寸；gridBorderWidth：网格边线宽度（奇数较好）；margin：网格间隙宽，应大于gridBorderWidth
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度；frameMargin：图像边框据图像边缘偏移
    #   图例：legendWidth：图例条基本宽度
    #   聚类数：dis_class_number、dis_class_number、k_dif；颜色：color_scheme、c_dif
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 84, 'ox': 30, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000, 'xoffset': 3, 'yoffset': 3,
              'legend_size': 63, 'legend_yoffset': 130, 'legend_xoffset': 150,
              'mag_class_number': 6, 'dis_class_number': 4, 'k_dif': 10, 'c_dif': [],
              'quality': 1000, 'dpi': (1200, 1200)}
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
    fileName = './data/sj_2kmsq_051316_1721.csv'
    ia = readDrawingSetting(scale[1:])
    data = readData(fileName)
    drawODMap(fileName, ia, False)  # True 表示只显示五环内的数据

