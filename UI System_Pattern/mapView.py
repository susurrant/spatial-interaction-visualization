#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

"""map view
"""

import sys
sys.path.append('../')
from tkinter import *
from tkinter import ttk
from mapFile import relate2data
from func import computeCo
from LL2UTM import LL2UTM_USGS
import numpy as np

class MapGUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg='#e9e7ef', height=870, width=1600)

        # layer
        self.pFrm = ParameterFrm(self)
        self.pFrm.place(x=0, y=800)

        self.ia = {}
        self.init_ia()

        self.fileNames = ['../data/sj_051316_0105', '../data/sj_051316_0509', '../data/sj_051316_0913',
                          '../data/sj_051316_1317', '../data/sj_051316_1721', '../data/sj_051316_2101']
        grids, flows = relate2data(self.fileNames[4], self.ia)
        # pattern map
        self.cv = MapCanvas(self, grids)
        # flow map
        self.fc = FlowCanvas(self, flows)

        self.cv.place(x=0, y=0)
        self.fc.place(x=800, y=0)

        self.show()

    def init_ia(self):
        # 'xoff': 431300, 'yoff': 4400700, 'trans_scale': 38
        self.ia = {'hexParm': (12, 240), 'width': 800, 'height': 800, 'gridWidth': 22, 'gridBorderWidth': 5,
                   'xoffset': 3, 'yoffset': 3, 'ox': 7, 'oy': 7, 'margin': 3, 'scale': '_1km', 'dnum': 6, 'legendWidth': 4,
                   'xoff': 425000, 'yoff': 4396000, 'trans_scale': 55, 'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': [],
                   'p': 0.1}

        nscale = [(i + 1) / float(self.ia['k_m'] + 1) for i in range(self.ia['k_m'])]
        for i, n in enumerate(nscale):
            self.ia['c_m'].append(
                '#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
        self.ia['c_m'][0] = '#ffffff'
        self.ia['c_d'] = ['#9fd4ff', '#00dd66', '#ffd700', '#ff8000', '#c70000']

    def show(self):
        self.cv.invalidate()
        self.fc.invalidate()

class ParameterFrm(Frame):
    def __init__(self, master):
        bgc = '#e9e7ef'
        Frame.__init__(self, master, bg=bgc, height=70, width=1600)

        Label(self, text='Time period', bg=bgc).place(x=110, y=5)
        self.time = ttk.Combobox(self, textvariable=StringVar(), state='readonly')
        self.time['values'] = ('Early morning (1-5 a.m.)', 'Morning (5-9 a.m.)', 'Noon (9 a.m.-1 p.m.)', 'Afternoon (1-5 p.m.)', 'Evening (5-9 p.m.)', 'Night (9 p.m.-1 a.m.)')
        self.time.current(1)
        self.time.place(x=140, y=35)


        Label(self, text='SI type', bg=bgc).place(x=360, y=5)
        self.sit1 = Radiobutton(self, bg=bgc, text='Outgoing', value=1)
        self.sit1.place(x=390, y=23)
        self.sit2 = Radiobutton(self, bg=bgc, text='Incoming', value=2)
        self.sit2.place(x=390, y=45)

        Label(self, text='Scale', bg=bgc).place(x=520, y=5)
        self.scaleScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=0.5, to=1.0, resolution=0.5)
        self.scaleScale.place(x=550, y=25)
        Label(self, text='km', bg=bgc).place(x=710, y=25)

        Label(self, text='Number of magnitude classes', bg=bgc).place(x=790, y=5)
        self.nnScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=5, to=25, resolution=1)
        self.nnScale.place(x=830, y=25)

        Label(self, text='Number of distance classes', bg=bgc).place(x=1040, y=5)
        self.dnScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=4, to=8, resolution=1)
        self.dnScale.place(x=1080, y=25)

        self.appbtn = Button(self, text='Apply', bg=bgc, relief=RAISED, height=1, width=15)
        self.appbtn.place(x=1350, y=5)

        self.expbtn = Button(self, text='Export', bg=bgc, relief=RAISED, height=1, width=15)
        self.expbtn.place(x=1350, y=40)


class MapCanvas(Canvas):
    def __init__(self, master, grids):
        Canvas.__init__(self, master, height = 800, width = 800, bg = 'white')
        self.grids = grids
        self.borders = []

        fxs, fys = computeCo(master.ia['gridWidth'] + master.ia['margin'], master.ia['dnum'] // 6)
        for gid in self.grids:
            cx = self.grids[gid].cenx
            cy = self.grids[gid].ceny
            for i in range(self.master.ia['dnum']):
                lineco1 = [cx + fxs[i], cy + fys[i], cx + fxs[(i + 1) % 6], cy + fys[(i + 1) % 6]]
                lineco2 = [cx + fxs[(i + 1) % 6], cy + fys[(i + 1) % 6], cx + fxs[i], cy + fys[i]]
                tag = True
                for lc in self.borders:
                    dis = (np.array(lineco1) - np.array(lc)) ** 2
                    if np.sqrt(dis[0] + dis[1]) < 20 and np.sqrt(dis[2] + dis[3]) < 20:
                        tag = False
                        break
                    dis = (np.array(lineco2) - np.array(lc)) ** 2
                    if np.sqrt(dis[0] + dis[1]) < 20 and np.sqrt(dis[2] + dis[3]) < 20:
                        tag = False
                        break
                if tag:
                    self.borders.append(lineco1)
        
        def mouseLeftClick(event):
            mgid = -1
            mdis = float('inf')
            for gid in self.grids:
                dis = np.sqrt((self.grids[gid].cenx - event.x) ** 2 + (self.grids[gid].ceny - event.y) ** 2)
                if dis < mdis:
                    mgid = gid
                    mdis = dis
            if mdis > (self.master.ia['gridWidth'] + self.master.ia['margin']):
                self.master.show()
                return
            self.highlight(mgid)
            self.master.fc.draw_target_flows(mgid)

        self.bind("<Button>", mouseLeftClick)

    def invalidate(self):
        self.delete(ALL)
        oxs, oys = computeCo(self.master.ia['gridWidth'], self.master.ia['dnum'] // 6)
        ixs, iys = computeCo(self.master.ia['gridWidth'] * 0.7, self.master.ia['dnum'] // 6)

        for gid in self.grids:
            cx = self.grids[gid].cenx
            cy = self.grids[gid].ceny
            for i in range(self.master.ia['dnum']):
                self.create_polygon(cx, cy, cx + ixs[i], cy + iys[i], cx + ixs[i + 1], cy + iys[i + 1],
                                    fill=self.grids[gid].mcolor[i], outline=self.grids[gid].mcolor[i])
                self.create_polygon(cx + ixs[i], cy + iys[i], cx + oxs[i], cy + oys[i], cx + oxs[i+1], cy + oys[i+1],
                                    cx + ixs[i+1], cy + iys[i+1], fill=self.grids[gid].dcolor[i])

        for lc in self.borders:
            self.create_line(lc, width=1, fill='#000000')

        self.drawLegend()

    #绘制图例
    def drawLegend(self):
        ia = self.master.ia
        sy = ia['height'] - 14
        lw = ia['legendWidth']
        gridWidth = ia['gridWidth']

        # magnitude
        mx = ia['width'] - 180
        for i, c in enumerate(ia['c_m']):
            self.create_line(mx, sy - i * lw, mx + gridWidth, sy - i * lw, width=lw, fill=c)
        self.create_text(mx + 12, sy - (ia['k_m'] + 5) * lw, text='Magnitude', font=('Times New Roman', 12),
                         fill='#000000')
        self.create_text(mx - gridWidth, sy - lw, text='Low', font=('Times New Roman', 10), fill='#000000')
        self.create_text(mx - gridWidth, sy - lw * (ia['k_m'] + 1), text='High', font=('Times New Roman', 10),
                         fill='#000000')

        # distance
        disx = ia['width'] - 80
        scale = ia['k_m'] / ia['k_d']
        for i, n in enumerate(ia['c_d']):
            self.create_line(disx, sy - (i + 0.35) * lw * scale, disx + gridWidth, sy - (i + 0.35) * lw * scale,
                             width=int(round(lw * scale)), fill=n)
        self.create_text(disx + 12, sy - (ia['k_m'] + 5) * lw, text='Distance', font=('Times New Roman', 12),
                         fill='#000000')
        self.create_text(disx + 25 + gridWidth, sy - lw, text='Short', font=('Times New Roman', 10), fill='#000000')
        self.create_text(disx + 25 + gridWidth, sy - lw * ia['k_m'] - lw, text='Long', font=('Times New Roman', 10),
                         fill='#000000')

    def highlight(self, mgid):
        self.invalidate()
        fxs, fys = computeCo(self.master.ia['gridWidth'] + self.master.ia['margin'], self.master.ia['dnum'] // 6)
        cenx, ceny = self.grids[mgid].cenx, self.grids[mgid].ceny
        fco = []
        for i in range(self.master.ia['dnum']):
            fco.append(cenx + fxs[i])
            fco.append(ceny + fys[i])
        fco.append(cenx + fxs[0])
        fco.append(ceny + fys[0])
        self.create_line(fco)


class FlowCanvas(Canvas):
    def __init__(self, master, flows):
        Canvas.__init__(self, master, height=800, width=800, bg='white')
        self.flows = flows
        for fid in self.flows:
            if np.random.random() < self.master.ia['p']:
                self.flows[fid].select_tag = True
            co = self.flows[fid].co
            ox = (co[0][0] - self.master.ia['xoff']) / self.master.ia['trans_scale']
            oy = 800 - (co[0][1] - self.master.ia['yoff']) / self.master.ia['trans_scale']
            dx = (co[1][0] - self.master.ia['xoff']) / self.master.ia['trans_scale']
            dy = 800 - (co[1][1] - self.master.ia['yoff']) / self.master.ia['trans_scale']
            self.flows[fid].co = [(ox, oy), (dx, dy)]

    def invalidate(self):
        self.delete(ALL)
        self.draw_flows()
        self.draw_ring_roads()

    def draw_ring_roads(self):
        with open('../data/ringroad_pt.csv', 'r') as f:
            lines = f.readlines()
            tag = 0
            pts = []
            for line in lines[1:]:
                sl = line.strip().split(',')
                x, y = LL2UTM_USGS(float(sl[3]), float(sl[2]))
                x = (x - self.master.ia['xoff']) / self.master.ia['trans_scale']
                y = 800 - (y - self.master.ia['yoff']) / self.master.ia['trans_scale']

                if int(sl[1]) == tag:
                    pts.append((x, y))
                else:
                    self.create_line(pts, fill='#000000', width=2)
                    tag = int(sl[1])
                    pts = [(x, y)]
            self.create_line(pts, fill='#000000', width=2)

    def draw_flows(self):
        for fid in self.flows:
            if self.flows[fid].select_tag:
                self.create_line(self.flows[fid].co, width=1, fill='#C0C0C0', arrow=LAST)

    def draw_target_flows(self, gid):
        self.invalidate()
        for fid in self.flows:
            if self.flows[fid].ogid == gid:
                self.create_line(self.flows[fid].co, width=1, fill='#0000FF', arrow=LAST)