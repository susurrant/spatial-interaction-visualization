# -*- coding: utf-8 -*-：

# 读取渲染设置
def bivarite_color(scale):
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
              'quality': 95, 'dpi': (1200, 1200)}
    elif scale == '500m':
        ia = {'hexParm': (24, 960), 'gridWidth': 38, 'gridBorderWidth': 9, 'ox': -10, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 1, 'yoffset': 6, 'frameMargin': 2, 'legendWidth': 20, 'quality': 1000, 'dpi': (1200, 1200),
              'mag_class_number': 5, 'dis_class_number': 5}


    # color setting
    ia['border_color'] = '#000000'
    # blue-orange
    ia['color_scheme0'] = [['#ffffff', '#d3e2f1', '#a7c7e4', '#78abd7', '#3192c8'],
                          ['#f9dacc', '#d4cccb', '#aabcc6', '#7caac0', '#3a93b4'],
                          ['#f1b69b', '#cfab9b', '#aea19a', '#849599', '#4c8695'],
                          ['#e99567', '#cc8d69', '#ac856a', '#897d6d', '#59726d'],
                          ['#e47920', '#c7722a', '#aa6d2f', '#8b6736', '#5f613c']]
    # blue-red
    ia['color_scheme2'] = [['#ffffff', '#c7c5df', '#8f90c0', '#535a9f', '#253f8e'],
                           ['#f4c5c6', '#c7b5c3', '#9191b2', '#555c95', '#264285'],
                           ['#e88f91', '#c18690', '#947b91', '#565f86', '#284478'],
                           ['#de5d5c', '#bb595f', '#945361', '#5e4e65', '#294663'],
                           ['#d8211c', '#b72825', '#932c2c', '#633233', '#383336']]
    # blue-orange
    ia['color_scheme1'] = [['#ffffff', '#c4d9ed', '#8ab6dc', '#3192c8'],
                           ['#fae0d7', '#c7cdd4', '#8cb5cb', '#3993ba'],
                           ['#f3c3ae', '#c6b3af', '#91a3ab', '#438da4'],
                           ['#eea787', '#c39c88', '#97908a', '#527d86'],
                           ['#e88f5b', '#c1855f', '#987b62', '#5b6f65'],
                           ['#e47920', '#be712b', '#966933', '#5f613c']]

    ia['mag_class_number'] = len(ia['color_scheme'])
    ia['dis_class_number'] = len(ia['color_scheme'][0])

    return ia

def bivariate_symbol(scale):
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   hexparm: 网格参数(每行六边形数, 总六边形个数的一半)
    #   网格：gridWidth：网格尺寸；gridBorderWidth：网格边线宽度（奇数较好）；margin：网格间隙宽，应大于gridBorderWidth
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度；frameMargin：图像边框据图像边缘偏移
    #   图例：legendWidth：图例条基本宽度
    #   聚类数：k_m、k_d、k_dif；颜色：c_m、c_d、c_dif
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 76, 'gridBorderWidth': 18, 'ox': 20, 'oy': 40, 'margin': 18,
              'width': 3000, 'height': 3000,
              'xoffset': 3, 'yoffset': 3, 'frameMargin': 5, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': []}
    elif scale == '500m':
        ia = {'hexParm': (24, 960), 'gridWidth': 38, 'gridBorderWidth': 9, 'ox': -10, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 1, 'yoffset': 6, 'frameMargin': 2, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': []}


    # color setting
    nscale = [(i + 1) / float(ia['k_m'] + 1) for i in range(ia['k_m'])]

    for i, n in enumerate(nscale):
        ia['c_m'].append('#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
    ia['c_m'][0] = '#ffffff'

    ia['c_d'] = ['#bee6fe', '#abdda4', '#ffffbf', '#fdae61', '#f46d43']
    ia['c_d'] = ['#bee6fe', '#abdda4', '#fee08b', '#f46d43', '#d53e4f']

    return ia


def diff(scale):
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   hexparm: 网格参数(每行六边形数, 总六边形个数的一半)
    #   网格：gridWidth：网格尺寸；gridBorderWidth：网格边线宽度（奇数较好）；margin：网格间隙宽，应大于gridBorderWidth
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度；frameMargin：图像边框据图像边缘偏移
    #   图例：legendWidth：图例条基本宽度
    #   聚类数：k_dif；颜色：c_dif
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 76, 'gridBorderWidth': 18, 'ox': 20, 'oy': 40, 'margin': 18,
              'width': 3000, 'height': 3000,
              'xoffset': 3, 'yoffset': 3, 'frameMargin': 5, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'c_dif': []}
    elif scale == '500m':
        ia = {'hexParm': (24, 960), 'gridWidth': 38, 'gridBorderWidth': 9, 'ox': -10, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 1, 'yoffset': 6, 'frameMargin': 2, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'c_dif': []}

    # color setting
    # blue to red
    rgbcolor = [(153, 153, 255), (156, 187, 255), (156, 222, 255), (153, 255, 255), (194, 255, 220),
                (227, 255, 186), (255, 255, 153), (255, 221, 153), (255, 187, 153), (255, 153, 153)]
    for color in rgbcolor:
        ia['c_dif'].append('#%02X%02X%02X' % color)
    ia['k_dif'] = len(ia['c_dif'])

    return ia


def diagram_map():
    #   rows, columns: 网格行数、列数; gridWidth：网格尺寸
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度
    #   legendWidth：图例条基本宽度; radius：扇形符号最大半径
    #   class_number： 聚类数；color_scheme： 颜色
    ia = dict()
    ia.update({'hexParm': (12, 240), 'gridWidth': 92, 'ox': 45, 'oy': 50, 'margin': 0, 'width': 3000, 'height': 3000,
               'xoffset': 3, 'yoffset': 3, 'legend_size': 63, 'radius': 100, 'quality': 95, 'dpi': (1200, 1200),
               'radii': [30, 60, 90]})

    # color setting
    ia['border_color'] = '#000000'
    ia['color_scheme'] = ['#fed998', '#ffaa63', '#fe7b00']
    ia['class_num'] = len(ia['color_scheme'])
    return ia


def readDrawingSetting(mode, scale='1km'):
    if mode == 'bc':
        return bivarite_color(scale)
    elif mode == 'bs':
        return bivariate_symbol(scale)
    elif mode == 'diff':
        return diff(scale)
    elif mode == 'dm':
        return diagram_map()