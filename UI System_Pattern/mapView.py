#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

' map view '

from tkinter import *
from tkinter import ttk
from mapFile import relate2data, computeCo, computeCo_hexagon
from numpy import sqrt

class MapGUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg='#e9e7ef', height=870, width=1600)

        # 图层栏-lFrm
        self.pFrm = PFrm(self)
        # 地图栏-cv
        self.cv = MapCanvas(self)
        #
        self.fc = FlowCanvas(self)

        self.cv.place(x=0, y=0)
        self.fc.place(x=800, y=0)
        self.pFrm.place(x=0, y=800)

        self.ia = {}
        self.init_ia()

        self.fileNames = ['../data/sj_051316_0105', '../data/sj_051316_0509', '../data/sj_051316_0913',
                          '../data/sj_051316_1317', '../data/sj_051316_1721', '../data/sj_051316_2101']
        self.cv.generateGrids(self.fileNames[0])

    def init_ia(self):
        self.ia = {'hexParm': (12, 240), 'width': 1000, 'height': 1000, 'gridWidth': 19, 'gridBorderWidth': 5,
              'xoffset': 3, 'yoffset': 3, 'ox': 7, 'oy': 7, 'margin': 6, 'scale': '_1km', 'dnum': 6, 'legendWidth': 6,
              'k_m': 15, 'k_d': 5, 'c_m': [], 'c_d': []}
        nscale = [(i + 1) / float(self.ia['k_m'] + 1) for i in range(self.ia['k_m'])]
        for i, n in enumerate(nscale):
            self.ia['c_m'].append(
                '#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
        self.ia['c_m'][0] = '#ffffff'
        self.ia['c_d'] = ['#bee6fe', '#abdda4', '#fee08b', '#f46d43', '#d53e4f']

class PFrm(Frame):
    def __init__(self, master):
        bgc = '#e9e7ef'
        Frame.__init__(self, master, bg=bgc, height=70, width=1600)

        Label(self, text='Time period', bg=bgc).place(x=110, y=5)
        self.time = ttk.Combobox(self, textvariable=StringVar(), state='readonly')
        self.time['values'] = ('Early morning (1-5 a.m.)', 'Morning (5-9 a.m.)', 'Noon (9 a.m.-1 p.m.)', 'Afternoon (1-5 p.m.)', 'Evening (5-9 p.m.)', 'Night (9 p.m.-1 a.m.)')
        self.time.current(0)
        self.time.place(x=140, y=35)


        Label(self, text='SI type', bg=bgc).place(x=360, y=5)
        self.sit1 = Radiobutton(self, bg=bgc, text='Outgoing', value=1)
        self.sit1.place(x=390, y=25)
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
    def __init__(self, master):
        Canvas.__init__(self, master, height = 800, width = 800, bg = 'white')
        self.grids = None
        
        def mouseLeftClick(event):
            self.delete(ALL)
            self.drawGridFlows(event.x, event.y)

        self.bind("<Button>", mouseLeftClick)

    def generateGrids(self, fileName):
        self.grids = relate2data(fileName, self.master.ia)
        self.invalidate()
        
    def drawEmptyGrids(self):
        for gid in self.grids:
            hex_co = computeCo_hexagon(self.grids[gid].cenx, self.grids[gid].ceny, self.master.ia['gridWidth'])
            co = []
            for item in hex_co:
                co.append(item[2])
                co.append(item[3])
            co.append(co[0])
            co.append(co[1])
            self.create_polygon(co, fill='#ffffff', outline='#000000')

    def drawGridFlows(self, x, y):
        mgid = -1
        mdis = float('inf')
        for gid in self.grids:
            dis = sqrt((self.grids[gid].cenx-x)**2+(self.grids[gid].ceny-y)**2)
            if dis < mdis:
                mgid = gid
                mdis = dis
        if mdis > (self.master.ia['gridWidth'] + self.master.ia['margin']):
            self.invalidate()
            return

        self.drawEmptyGrids()
        cenx = self.grids[mgid].cenx
        ceny = self.grids[mgid].ceny
        for gid in self.grids[mgid].toGrid:
            if gid:
                #print(self.grids[mgid].width[gid])
                self.create_line(cenx, ceny, self.grids[gid].cenx, self.grids[gid].ceny, width=self.grids[mgid].width[gid], fill='#00bc12', arrow=LAST)
                if cenx <= self.grids[gid].cenx:
                    self.create_text(self.grids[gid].cenx + 8, self.grids[gid].ceny, text=str(self.grids[mgid].toGrid[gid]), font=('Times New Roman', 9), fill='#000000')
                else:
                    self.create_text(self.grids[gid].cenx - 8, self.grids[gid].ceny,
                                     text=str(self.grids[mgid].toGrid[gid]), font=('Times New Roman', 8),
                                     fill='#000000')
        for co in self.grids[mgid].toOutFlowCo:
            self.create_line(cenx, ceny, co[0], co[1], width=0.2, fill='#00bc12', arrow=LAST)

    #重绘
    def invalidate(self):
        self.delete(ALL)
        xs, ys = computeCo(self.master.ia['gridWidth'], int(self.master.ia['dnum'] / 6))
        for gid in self.grids:
            cx = self.grids[gid].cenx
            cy = self.grids[gid].ceny
            for i in range(self.master.ia['dnum']):
                self.create_polygon(cx, cy, cx + xs[i], cy + ys[i], cx + xs[i + 1], cy + ys[i + 1],
                                    fill=self.grids[gid].mcolor[i], outline=self.grids[gid].mcolor[i])
                self.create_line(cx + xs[i], cy + ys[i], cx + xs[i + 1], cy + ys[i + 1],
                                 width=self.master.ia['gridBorderWidth'], fill=self.grids[gid].dcolor[i])
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
        self.create_text(mx + 12, sy - (ia['k_m'] + 5) * lw, text='Magnitude', font=('Times New Roman', 14),
                         fill='#000000')
        self.create_text(mx - gridWidth, sy - lw, text='Low', font=('Times New Roman', 12), fill='#000000')
        self.create_text(mx - gridWidth, sy - lw * (ia['k_m'] + 1), text='High', font=('Times New Roman', 12),
                         fill='#000000')

        # distance
        disx = ia['width'] - 80
        scale = ia['k_m'] / ia['k_d']
        for i, n in enumerate(ia['c_d']):
            self.create_line(disx, sy - (i + 0.35) * lw * scale, disx + gridWidth, sy - (i + 0.35) * lw * scale,
                             width=int(round(lw * scale)), fill=n)
        self.create_text(disx + 12, sy - (ia['k_m'] + 5) * lw, text='Distance', font=('Times New Roman', 14),
                         fill='#000000')
        self.create_text(disx + 25 + gridWidth, sy - lw, text='Short', font=('Times New Roman', 12), fill='#000000')
        self.create_text(disx + 25 + gridWidth, sy - lw * ia['k_m'] - lw, text='Long', font=('Times New Roman', 12),
                         fill='#000000')

class FlowCanvas(Canvas):
    def __init__(self, master):
        Canvas.__init__(self, master, height=800, width=800, bg='white')
        self.grids = None

        def mouseLeftClick(event):
            #self.delete(ALL)
            #self.drawGridFlows(event.x, event.y)
            pass

        self.bind("<Button>", mouseLeftClick)


class ColorCanvas(Canvas):
    def __init__(self, master, lFrm):
        Canvas.__init__(self, master, height=700, width=250, bg='#ffffff')
        self.pMap = ''
        self.lFrm = lFrm

        self.mouseDownX = 0
        self.mouseDownY = 0

        # self.affiCV.calcScale(self.disExt, self.winExt)

        def mouseMove(event):
            if self.pMap == '':
                return

            if self.mouseMode == 'VIEW' and self.mousePressed == True:
                pass

        def doubleLeft(event):
            if self.pMap == '':
                return

            if self.mouseMode == 'DRAW':
                if self.obj.pNum > 0:
                    if self.layerEditing.lType == 'POLYGON':
                        self.obj.appendXY(self.obj.x[0], self.obj.y[0])

                    self.objs.append(self.obj)
                    self.obj = Obj(0, 'null')

        self.bind("<Motion>", mouseMove)
        self.bind("<Double-Button-1>", doubleLeft)

    # 重绘
    def invalidate(self):
        pass

    def invalidateLFrm(self):
        self.lFrm.flash()