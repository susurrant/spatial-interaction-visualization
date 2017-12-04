# -*- coding: utf-8 -*-：

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans


# 读取五环内的交互
def readData(filename, rows, columns, minSpeed=2, maxSpeed=150):
    data = np.zeros((rows, columns), dtype=np.uint32)

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            if line1:
                sl1 = line1.split(',')
                sl2 = f.readline().strip().split(',')
                if int(sl1[-2]) == 0 or int(sl1[-2]) == 0:
                    continue
                if float(sl1[-2]) < minSpeed or float(sl1[-2]) > maxSpeed:
                    continue

                ogid = int(sl1[-1])
                dgid = int(sl2[-1])
                orow = rows - ogid // columns - 1
                ocolumn = ogid % columns
                drow = rows - dgid // columns - 1
                dcolumn = dgid % columns
                ridx = orow * rows + drow
                cidx = ocolumn * columns + dcolumn

                data[ridx, cidx] += 1
            else:
                break

    return data

# kmeans classifier
def kmeans(dn, cNum):
    X = np.sort(dn).reshape((-1,1))
    k = KMeans(n_clusters = cNum, random_state = 0).fit(X)
    labels = []
    for l in k.labels_:
        if l not in labels:
            labels.append(l)
    return k, labels


# 交互模式可视化
def drawODMap(data, ia):
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    nk, nl = kmeans(data.flatten(), ia['class_number'])
    




# 读取渲染设置
def readDrawingSetting():
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   hexparm: 网格参数(每行六边形数, 总六边形个数的一半)
    #   网格：gridWidth：网格尺寸；gridBorderWidth：网格边线宽度（奇数较好）；margin：网格间隙宽，应大于gridBorderWidth
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度；frameMargin：图像边框据图像边缘偏移
    #   图例：legendWidth：图例条基本宽度
    #   聚类数：dis_class_number、dis_class_number、k_dif；颜色：color_scheme、c_dif
    ia = dict()
    ia.update({'gridWidth': 84, 'ox': 30, 'oy': 40, 'margin': 9,
          'width': 3000, 'height': 3000, 'xoffset': 3, 'yoffset': 3,
          'legend_size': 63, 'legend_yoffset': 130, 'legend_xoffset': 150,
          'class_number': 15, 'quality': 1000, 'dpi': (1200, 1200)})

    # color setting
    ia['border_color'] = '#000000'
    cstr = 'fefffe#fff2f1#ffe5e3#ffd9d5#ffccc6#ffc0b8#ffb3aa#ffa69b#ff9a8c#ff8d7d#ff806d#ff735c#ff6548#ff5730#fe4800'
    ia['color_scheme'] = []
    for color in cstr.split('#'):
        ia['color_scheme'].append('#'+color)

    return ia


if __name__ == '__main__':
    fileName = './data/sj_2kmsq_051316_1721.csv'
    ia = readDrawingSetting()
    data = readData(fileName, 15, 15)
    drawODMap(fileName, ia)  # True 表示只显示五环内的数据

