# -*- coding: utf-8 -*-：

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from style import readDrawingSetting
from func import kmeans, fisher_jenks

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

def drawODMap_kmeans(file_name, save_file_name, ia):
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    data = readData(file_name, ia['rows'], ia['columns'])
    nk, nl = kmeans(data.flatten(), ia['mag_class_num'])
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

    left = (ia['width'] - ia['legend_width']*ia['mag_class_num']) // 2
    bottom = ia['height'] - 10
    for i, c in enumerate(ia['color_scheme']):
        draw.rectangle([(left+i*ia['legend_width'], bottom-ia['legend_height']), (left+(i+1)*ia['legend_width'], bottom)],
                       fill=c)

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 58)
    draw.text((left - 50, bottom - ia['legend_height']), '0', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left + ia['legend_width']*ia['mag_class_num'] + 20, bottom - ia['legend_height']), 'max magnitude', font=imageTitlefont, fill=(0, 0, 0))

    labelfont = ImageFont.truetype('./font/calibril.ttf', 90)
    left = ia['ox'] + (4*ia['columns'] - ia['xoffset']) * gridWidth
    right = ia['ox'] + (8*ia['columns'] - ia['xoffset']) * gridWidth
    top = ia['oy'] + (2*ia['rows'] - ia['yoffset']) * gridWidth
    bottom = ia['oy'] + (6*ia['rows'] - ia['yoffset']) * gridWidth
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill='#0000ff', width=4)
    draw.text((left + 20, top + 110), 'D', font=labelfont, fill=(0, 0, 0))

    draw.text((ia['ox'] + (6*ia['columns'] - ia['xoffset']) * gridWidth,
               ia['oy'] + (9*ia['rows'] - ia['yoffset']) * gridWidth), 'A', font=labelfont, fill=(0, 0, 0))
    draw.text((ia['ox'] + (13*ia['columns'] - ia['xoffset']) * gridWidth,
               ia['oy'] + (10*ia['rows'] - ia['yoffset']) * gridWidth), 'B', font=labelfont, fill=(0, 0, 0))
    draw.text((ia['ox'] + (10*ia['columns'] - ia['xoffset']) * gridWidth,
               ia['oy'] + (4*ia['rows'] - ia['yoffset']) * gridWidth), 'C', font=labelfont, fill=(0, 0, 0))

    image.save(save_file_name, quality=ia['quality'], dpi=ia['dpi'])

def drawODMap_fj(file_name, save_file_name, ia):
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    gridWidth = ia['gridWidth']

    data = readData(file_name, ia['rows'], ia['columns'])
    nk, nl = fisher_jenks(data.flatten(), ia['mag_class_num'])

    # draw cells
    for r in range(ia['rows']**2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns']**2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            x = np.where(data[r, c] <= nk)[0]
            i = x.min() if x.size > 0 else len(nk) - 1
            color = ia['color_scheme'][i]
            draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill=color)

    # draw border
    for r in range(ia['rows']):
        top = ia['oy'] + (r - ia['yoffset'])*gridWidth*ia['rows']
        for c in range(ia['columns']):
            left = ia['ox'] + (c - ia['xoffset'])*gridWidth*ia['columns']
            draw.rectangle([(left, top), (left+gridWidth*ia['columns'], top+gridWidth*ia['rows'])], outline=ia['border_color'])


    # draw home cell border
    for r in range(ia['rows']**2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns']**2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            if r % ia['rows'] == r // ia['rows'] and c % ia['columns'] == c // ia['columns']:
                #draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill=None, outline='#0000ff')
                draw.line([left, top, left + gridWidth, top, left + gridWidth, top + gridWidth,
                           left, top + gridWidth, left, top], fill='#0000ff', width=2)

    draw.line([ia['width'] - 600, ia['height'] - 75, ia['width'] - 600 + 30, ia['height'] - 75, ia['width'] - 600 + 30,
               ia['height'] - 45, ia['width'] - 600, ia['height'] - 45, ia['width'] - 600, ia['height'] - 75],
              fill='#0000ff', width=2)

    left = (ia['width'] - ia['legend_width']*ia['mag_class_num']) // 2
    bottom = ia['height'] - 10
    for i, c in enumerate(ia['color_scheme']):
        draw.rectangle([left+i*ia['legend_width'], bottom-ia['legend_height'], left+(i+1)*ia['legend_width'], bottom],
                       fill=c)

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 58)
    draw.text((ia['width']-600+70, bottom - ia['legend_height']), 'home cell', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 50, bottom - ia['legend_height']), '0', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left + ia['legend_width']*ia['mag_class_num'] + 20, bottom - ia['legend_height']), 'max magnitude',
              font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file_name, quality=ia['quality'], dpi=ia['dpi'])

def drawODMap_dif(file_name, file_name_c, save_file_name, ia):
    data = readData(file_name, ia['rows'], ia['columns'])
    data_c = readData(file_name_c, ia['rows'], ia['columns'])
    dif = np.abs(data-data_c)
    nk, nl = fisher_jenks(dif.flatten(), ia['dif_class_num'])

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    gridWidth = ia['gridWidth']

    # draw cells
    for r in range(ia['rows'] ** 2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns'] ** 2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            if data[r,c] == 0 and data_c[r,c]==0:
                color = '#ffffff'
            else:
                x = np.where(dif[r, c] <= nk)[0]
                i = x.min() if x.size > 0 else len(nk) - 1
                color = ia['c_dif'][i]
            draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill=color)

    # draw border
    for r in range(ia['rows']):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth * ia['rows']
        for c in range(ia['columns']):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth * ia['columns']
            draw.rectangle([(left, top), (left + gridWidth * ia['columns'], top + gridWidth * ia['rows'])],
                           outline=ia['border_color'])

    # draw home cell border
    for r in range(ia['rows'] ** 2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns'] ** 2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            if r % ia['rows'] == r // ia['rows'] and c % ia['columns'] == c // ia['columns']:
                #draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill=None, outline='#000000')
                draw.line([left, top, left + gridWidth, top, left + gridWidth, top + gridWidth,
                           left, top + gridWidth, left, top], fill='#000000', width=2)

    draw.line([ia['width'] - 600, ia['height'] - 70, ia['width'] - 600 + 30, ia['height'] - 70, ia['width'] - 600 + 30,
               ia['height'] - 40, ia['width'] - 600, ia['height'] - 40, ia['width'] - 600, ia['height'] - 70],
              fill='#000000', width=2)

    left = (ia['width'] - ia['legend_width'] * ia['dif_class_num']) // 2
    bottom = ia['height'] - 10
    for i, c in enumerate(ia['c_dif']):
        draw.rectangle([(left + i * ia['legend_width'], bottom - ia['legend_height']),
                        (left + (i + 1) * ia['legend_width'], bottom)], fill=c)

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 64)
    draw.text((ia['width'] - 600 + 70, bottom - ia['legend_height']), 'home cell', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 180, bottom - ia['legend_height']), 'Small', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left + ia['legend_width'] * ia['dif_class_num'] + 30, bottom - ia['legend_height']), 'Large',
              font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file_name, quality=ia['quality'], dpi=ia['dpi'])



if __name__ == '__main__':
    mode = 'om'
    file_name = './data/sj_1600msq_051316_1721.csv'
    file_name_c = './data/sj_1600msq_051316_0509.csv'
    save_file_name = './figure/odmap_1600msq_051316_1721_dif.jpg'

    ia = readDrawingSetting(mode)
    #drawODMap_fj(file_name, save_file_name, ia)
    drawODMap_dif(file_name, file_name_c, save_file_name, ia)

