# -*- coding: utf-8 -*-：


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


    # navi blue(hue 202)- red(hue 0)
    ia['color_scheme'] = [['#ffffff', '#c7dcf2', '#8cbce5', '#359bd7'],
                          ['#f9d3d4', '#c7c1d0', '#91afcc', '#3b9bc8'],
                          ['#f3a8aa', '#c69ba8', '#968da6', '#537ea4'],
                          ['#ee7e7f', '#c47580', '#986c80', '#5f6280'],
                          ['#ea5554', '#c25257', '#994e5a', '#654a5d'],
                          ['#e71f18', '#c12824', '#992d2c', '#693233']]


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
        ia = {'hexParm': (12, 240), 'gridWidth': 82, 'area_scale': 0.75, 'ox': 15, 'oy': 15, 'margin': 13,
              'width': 3000, 'height': 3000, 'dnum': 6,
              'xoffset': 3, 'yoffset': 3, 'frameMargin': 5, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': []}
    elif scale == '500m':
        ia = {'hexParm': (24, 960), 'gridWidth': 38, 'area_scale': 0.75, 'ox': -10, 'oy': 40, 'margin': 9,
              'width': 3000, 'height': 3000, 'dnum': 6,
              'xoffset': 1, 'yoffset': 6, 'frameMargin': 2, 'legendWidth': 20, 'quality': 95, 'dpi': (1200, 1200),
              'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': []}

    # color setting
    nscale = [(i + 1) / float(ia['k_m'] + 1) for i in range(ia['k_m'])]

    for i, n in enumerate(nscale):
        ia['c_m'].append('#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
    ia['c_m'][0] = '#ffffff'

    ia['c_d'] = ['#9fd4ff', '#00dd66', '#ffd700', '#ff8000', '#c70000'] # diverging
    ia['c_d'] = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']     # sequential (OrRd)

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
    ia['color_scheme'] = ['#fee8c8','#fdbb84','#e34a33'] #['#fed998', '#ffaa63', '#fe7b00']
    ia['class_num'] = len(ia['color_scheme'])
    return ia


def od_map():
    #   rows, columns: 网格行数、列数; gridWidth：网格尺寸
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度
    #   图例：legendWidth：图例条基本宽度
    #   聚类数：class_number；颜色梯度：color_scheme
    ia = dict()
    ia.update({'rows': 19, 'columns':19,
               'gridWidth': 10, 'ox': 40, 'oy': 20,
               'width': 3700, 'height': 3750, 'xoffset': 0, 'yoffset': 0,
               'legend_height': 80, 'legend_width': 60,
               'quality': 95, 'dpi': (1200, 1200)})

    # color setting
    ia['border_color'] = '#000000'
    cstr = 'ffffff#ffff80#fff771#ffee61#ffe452#ffd743#ffc933#ffb924#ffa815#ff9505#f58000#e66c00#d65900#c74900#b83900#a82c00#991f00#8a1500#7a0c00#6b0500'
    ia['color_scheme'] = []
    for color in cstr.split('#'):
        ia['color_scheme'].append('#'+color)

    ia['class_number'] = len(ia['color_scheme'])
    return ia


def trajectory(scale):
    if scale == '1km':
        ia = {'hexParm': (12, 240), 'gridWidth': 84, 'gridBorderWidth': 2, 'ox': 40, 'oy': 50, 'margin': 9,
              'width': 3000, 'height': 3000,
              'xoffset': 3, 'yoffset': 3, 'frameMargin': 5, 'legendWidth': 15, 'quality': 1000, 'dpi': (1200, 1200),
              'k_m': 27, 'k_d': 9, 'c_m': [], 'c_d': []}

    nscale = [(i + 1) / float(ia['k_m'] + 1) for i in range(ia['k_m'])]

    for i, n in enumerate(nscale):
        ia['c_m'].append(
            '#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
    ia['c_m'][0] = '#ffffff'

    ia['c_d'] = ['#fefffe', '#ffe6e6', '#fecece', '#fbb5b5', '#f69d9d', '#f08585', '#e76c6c', '#de5252', '#d23434',
                 '#c50000']

    ia['c_d'] = ['#fff7ec','#fee8c8','#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#b30000','#7f0000']
    return ia


# 读取渲染设置
def readDrawingSetting(mode, scale='1km'):
    if mode == 'bc':
        return bivarite_color(scale)
    elif mode == 'bs':
        return bivariate_symbol(scale)
    elif mode == 'diff':
        return diff(scale)
    elif mode == 'dm':
        return diagram_map()
    elif mode == 'om':
        return od_map()
    elif mode == 'tj':
        return trajectory(scale)