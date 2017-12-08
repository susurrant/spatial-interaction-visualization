# -*- coding: utf-8 -*-：

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans


# 读取五环内的交互
def readData(filename, rows, columns, minSpeed=2, maxSpeed=150):
    data = np.zeros((rows**2, columns**2), dtype=np.uint32)
    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            line2 = f.readline().strip()
            if line1 and line2:
                sl1 = line1.split(',')
                sl2 = line2.split(',')
                if int(sl1[1]) == 0 or int(sl2[1]) == 0:
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
def drawODMap(file_name, save_file_name, ia):
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    data = readData(file_name, ia['rows'], ia['columns'])
    nk, nl = kmeans(data.flatten(), ia['class_number'])
    gridWidth = ia['gridWidth']

    for r in range(ia['rows']**2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns']**2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            color = ia['color_scheme'][nl.index(nk.predict(data[r, c]))]
            draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill = color)

    for r in range(ia['rows']):
        top = ia['oy'] + (r - ia['yoffset'])*gridWidth*ia['rows']
        for c in range(ia['columns']):
            left = ia['ox'] + (c - ia['xoffset'])*gridWidth*ia['columns']
            draw.rectangle([(left, top), (left+gridWidth*ia['columns'], top+gridWidth*ia['rows'])], outline=ia['border_color'])

    left = (ia['width'] - ia['legend_width']*ia['class_number']) // 2
    bottom = ia['height'] - 10
    for i, c in enumerate(ia['color_scheme']):
        draw.rectangle([(left+i*ia['legend_width'], bottom-ia['legend_height']), (left+(i+1)*ia['legend_width'], bottom)],
                       fill=c)

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 58)
    draw.text((left - 50, bottom - ia['legend_height']), '0', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left + ia['legend_width']*ia['class_number'] + 20, bottom - ia['legend_height']), 'max magnitude', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file_name, quality=ia['quality'], dpi=ia['dpi'])

# 读取渲染设置
def readDrawingSetting():
    # -----------------------------配置----------------------------------
    # 参数说明：
    #   rows, colummns: 网格行数、列数; gridWidth：网格尺寸
    #   图像位置：ox、oy：左上角的原点x、y坐标偏移，用于细微调整图像位置；xoffset、yoffset：图像水平、竖直偏移，大范围调节图像位置
    #   图像尺寸：width：图像宽度；height：图像高度
    #   图例：legendWidth：图例条基本宽度；legend_yoffset：图例相对右下角点的纵向偏移；legend_xoffset：图例相对右下角点的横向偏移
    #   聚类数：class_number；颜色梯度：color_scheme
    ia = dict()
    ia.update({'rows': 15, 'columns':15,
               'gridWidth': 15, 'ox': 20, 'oy': 20,
               'width': 3415, 'height': 3500, 'xoffset': 0, 'yoffset': 0,
               'legend_height': 80, 'legend_width': 60,
               'quality': 1000, 'dpi': (1200, 1200)})

    # color setting
    ia['border_color'] = '#000000'
    cstr = 'ffffff#ffff80#fff771#ffee61#ffe452#ffd743#ffc933#ffb924#ffa815#ff9505#f58000#e66c00#d65900#c74900#b83900#a82c00#991f00#8a1500#7a0c00#6b0500'
    cstr = 'ffffff#f5f500#f5e700#f5da00#f5cc00#f5bf00#f5b100#f5a300#f59600#f58800#f57a00#f56d00#f55f00#f55200#f54400#f53600#f52900#f51b00#f50e00#f50000'
    ia['color_scheme'] = []
    for color in cstr.split('#'):
        ia['color_scheme'].append('#'+color)
    ia['class_number'] = len(ia['color_scheme'])
    return ia


if __name__ == '__main__':
    file_name = './data/sj_2kmsq_051316_1721.csv'
    ia = readDrawingSetting()
    drawODMap(file_name, './figure/odmap_2kmsq_051316_1721.jpg', ia)

