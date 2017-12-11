# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
from LL2UTM import LL2UTM_USGS
from draw import kmeans, computeCen


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
    maxmag = 0
    for g in grids:
        grids[g].calcOutList(flows)
        for td in grids[g].wd:
            dis.append(td)
        for tm in grids[g].wm:
            if tm > maxmag:
                maxmag = tm
    dk, dl = kmeans(dis, 3)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):


if __name__ == '__main__':
    grids, flows = readData_Inside('./data/sj_051316_1721_1km.csv', 6)
    saveFileName = './figure/dm_051316_1721_1km_5rr.jpg'
    drawDiagramMap(grids, flows)

