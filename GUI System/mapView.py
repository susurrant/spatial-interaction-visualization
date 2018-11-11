#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

"""map view
"""

import sys
sys.path.append('../')
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
from mapFile import relate2data, set_glyph_color, computeCo
from LL2UTM import LL2UTM_USGS
import numpy as np


DATAFILE_MODES = {'Early morning (1-5 a.m.)': 0, 'Morning (5-9 a.m.)': 1, 'Noon (9 a.m.-1 p.m.)': 2,
                  'Afternoon (1-5 p.m.)': 3, 'Evening (5-9 p.m.)': 4, 'Night (9 p.m.-1 a.m.)': 5}

class MapGUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg='#e9e7ef', height=870, width=1600)

        self.pFrm = ParameterFrm(self)  # parameter view
        self.pFrm.place(x=0, y=800)

        self.ia = self.init_ia(0.5, 15, 5)
        filenames_500m = ['../data/sj_051316_0509_500m.csv', '../data/sj_051316_1721_500m.csv']
        self.grids_500m, self.flows_500m, self.max_v_500m = relate2data(filenames_500m, self.ia)
        self.ia = self.init_ia(1, 15, 5)
        filenames_1km = ['../data/sj_051316_0509_1km.csv', '../data/sj_051316_1721_1km.csv']
        self.grids_1km, self.flows_1km, self.max_v_1km  = relate2data(filenames_1km, self.ia)
        self.sample_flows()

        self.pc = pattern_canvas(self, self.grids_1km[0], self.max_v_1km[0]) # pattern map canvas
        self.pc.place(x=0, y=0)
        self.fc = flow_canvas(self, self.flows_1km[0]) # flow map canvas
        self.fc.place(x=800, y=0)

        self.show()

    def sample_flows(self):
        for i in range(len(self.flows_1km)):
            for fid in self.flows_1km[i]:
                if np.random.random() < self.ia['p']:
                    if fid in self.flows_500m[i]:
                        self.flows_1km[i][fid].select_tag = True
                        self.flows_500m[i][fid].select_tag = True

    @staticmethod
    def init_ia(scale=1, k_m=15, k_d=5):
        ia = dict()
        if scale == 0.5:
            ia.update({'shape': (24, 960), 'width': 800, 'height': 800, 'gridWidth': 11, 'gridBorderWidth': 3,
                       'xoffset': 3, 'yoffset': 7, 'ox': 20, 'oy': 5, 'margin': 2, 'dnum': 6,
                       'legendWidth': 4, 'xoff': 425000, 'yoff': 4396000, 'trans_scale': 55, 'area_ratio': 0.85,
                       'p': 0.1, 'dgids_file': '../data/5th_rr_hexagon_500m.csv'})
        elif scale == 1:
            ia.update({'shape': (12, 240), 'width': 800, 'height': 800, 'gridWidth': 22, 'gridBorderWidth': 5,
                       'xoffset': 3, 'yoffset': 3, 'ox': 7, 'oy': 7, 'margin': 3, 'dnum': 6,
                       'legendWidth': 4, 'xoff': 425000, 'yoff': 4396000, 'trans_scale': 55, 'area_ratio': 0.75,
                       'p': 0.1, 'dgids_file': '../data/5th_rr_hexagon_1km.csv'})

        ia.update({'k_m': k_m, 'k_d': k_d, 'c_m': [], 'c_d': []})
        nscale = [(i + 1) / float(ia['k_m'] + 1) for i in range(ia['k_m'])]
        for i, n in enumerate(nscale):
            ia['c_m'].append(
                '#%02X%02X%02X' % (int(round((1 - n) * 255)), int(round((1 - n) * 255)), int(round((1 - n) * 255))))
        ia['c_m'][0] = '#ffffff'

        if k_d == 3:
            ia['c_d'] = ['#fee8c8', '#fdbb84', '#e34a33']
        elif k_d == 4:
            ia['c_d'] = ['#fef0d9', '#fdcc8a', '#fc8d59', '#d7301f']
        elif k_d == 5:
            ia['c_d'] = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']
        elif k_d == 6:
            ia['c_d'] = ['#fef0d9', '#fdd49e', '#fdbb84', '#fc8d59', '#e34a33', '#b30000']
        elif k_d == 7:
            ia['c_d'] = ['#fef0d9', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000']
        elif k_d == 8:
            ia['c_d'] = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000']
        elif k_d == 9:
            ia['c_d'] = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '7f0000']

        return ia

    def update_data(self):
        mapscale = self.pFrm.mapscale.get()
        SI_type = self.pFrm.flow_type.get()
        self.ia = self.init_ia(mapscale, self.pFrm.mag_num.get(), self.pFrm.dis_num.get())

        time_idx = DATAFILE_MODES[self.pFrm.period.get()]
        if time_idx == 1:
            time_idx = 0
        elif time_idx == 4:
            time_idx = 1
        else:
            return

        if mapscale == 0.5:
            set_glyph_color(self.grids_500m[time_idx], self.flows_500m[time_idx])
            self.pc.set_p(self.grids_500m[time_idx], SI_type, self.max_v_500m[time_idx])
            self.fc.set_p(self.flows_500m[time_idx], SI_type)
        elif mapscale == 1:
            set_glyph_color(self.grids_1km[time_idx], self.flows_1km[time_idx])
            self.pc.set_p(self.grids_1km[time_idx], SI_type, self.max_v_1km[time_idx])
            self.fc.set_p(self.flows_1km[time_idx], SI_type)

        self.show()

    def show(self):
        self.pc.invalidate()
        self.fc.invalidate()


class ParameterFrm(Frame):
    def __init__(self, master):
        bgc = '#e9e7ef'
        Frame.__init__(self, master, bg=bgc, height=70, width=1600)

        #----------------------parameters------------------------
        self.period = StringVar()
        self.flow_type = IntVar()
        self.mapscale = DoubleVar()
        self.mag_num = IntVar()
        self.dis_num = IntVar()
        #--------------------------------------------------------

        Label(self, text='Period', bg=bgc).place(x=110, y=5)
        self.period.set('Morning (5-9 a.m.)')
        self.time = ttk.Combobox(self, textvariable=self.period, state='readonly')
        self.time['values'] = ('Early morning (1-5 a.m.)', 'Morning (5-9 a.m.)', 'Noon (9 a.m.-1 p.m.)',
                               'Afternoon (1-5 p.m.)', 'Evening (5-9 p.m.)', 'Night (9 p.m.-1 a.m.)')
        self.time.current(1)
        self.time.place(x=140, y=35)

        Label(self, text='SI type', bg=bgc).place(x=360, y=5)
        self.flow_type.set(0)
        self.sit1 = Radiobutton(self, bg=bgc, text='Outgoing', variable=self.flow_type, value=0)
        self.sit1.place(x=390, y=23)
        self.sit2 = Radiobutton(self, bg=bgc, text='Incoming', variable=self.flow_type, value=1)
        self.sit2.place(x=390, y=45)

        Label(self, text='Scale', bg=bgc).place(x=520, y=5)
        self.mapscale.set(1)
        self.scaleScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=0.5, to=1.0, resolution=0.5, variable=self.mapscale)
        self.scaleScale.place(x=550, y=25)
        Label(self, text='km', bg=bgc).place(x=710, y=25)

        Label(self, text='Number of magnitude classes', bg=bgc).place(x=790, y=5)
        self.mag_num.set(15)
        self.nnScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=5, to=25, resolution=1, variable=self.mag_num)
        self.nnScale.place(x=830, y=25)

        Label(self, text='Number of distance classes', bg=bgc).place(x=1040, y=5)
        self.dis_num.set(5)
        self.dnScale = Scale(self, orient=HORIZONTAL, bg=bgc, length=150, from_=3, to=9, resolution=1, variable=self.dis_num)
        self.dnScale.place(x=1080, y=25)

        self.appbtn = Button(self, text='Apply', bg=bgc, relief=RAISED, height=1, width=15, command=master.update_data)
        self.appbtn.place(x=1350, y=5)

        self.expbtn = Button(self, text='Export', bg=bgc, relief=RAISED, height=1, width=15, command=self.save_img)
        self.expbtn.place(x=1350, y=40)

    def save_img(self):
        save_filename = filedialog.asksaveasfilename(filetypes = (("jpg files", "*.jpg"), ("png files", "*.png"), ("All files", "*.*")))
        messagebox.showinfo('OK', 'successfully saved!')

    def show_Var(self):
        print(DATAFILE_MODES[self.period.get()])
        print(self.flow_type.get())
        print(self.mapscale.get())
        print(self.mag_num.get())
        print(self.dis_num.get())


class pattern_canvas(Canvas):
    def __init__(self, master, grids, max_v):
        Canvas.__init__(self, master, height = 800, width = 800, bg = 'white')
        self.grids = grids
        self.SI_type = 0 # 0: outgoing, 1: incomging
        self.max_v = max_v  # max_mag, max_dis
        
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

    def set_p(self, grids, SI_type, max_v):
        self.grids = grids
        self.SI_type = SI_type
        self.max_v = max_v
        self.invalidate()

    def invalidate(self):
        self.delete(ALL)
        if self.SI_type == 0:
            for gid in self.grids:
                for i in range(self.master.ia['dnum']):
                    self.create_polygon(self.grids[gid].oco[i], fill=self.grids[gid].out_mcolor[i],
                                        outline=self.grids[gid].out_mcolor[i])
                    self.create_polygon(self.grids[gid].ico[i], fill=self.grids[gid].out_dcolor[i],
                                        outline=self.grids[gid].out_dcolor[i])
                self.create_line(self.grids[gid].border, width=0.5, fill='#000000')
        elif self.SI_type == 1:
            for gid in self.grids:
                for i in range(self.master.ia['dnum']):
                    self.create_polygon(self.grids[gid].oco[i], fill=self.grids[gid].in_mcolor[i],
                                        outline=self.grids[gid].in_mcolor[i])
                    self.create_polygon(self.grids[gid].ico[i], fill=self.grids[gid].in_dcolor[i],
                                        outline=self.grids[gid].in_dcolor[i])
                self.create_line(self.grids[gid].border, width=0.5, fill='#000000')

        self.drawLegend()

    #绘制图例
    def drawLegend(self):
        ia = self.master.ia
        sy = ia['height'] - 30
        lw = ia['legendWidth'] * 15 / ia['k_m']
        gridWidth = 20
        if self.SI_type == 0:
            max_v = self.max_v[0:2]
        elif self.SI_type == 1:
            max_v = self.max_v[2:]

        # magnitude
        mx = ia['width'] - 160
        for i, c in enumerate(ia['c_m']):
            self.create_line(mx, sy - i * lw, mx + gridWidth, sy - i * lw, width=lw, fill=c)
        self.create_text(mx + 8, ia['height'] - (ia['k_m'] + 11) * lw - 4, text='Magnitude', font=('Arial', 10),
                         fill='#000000')
        self.create_text(mx - gridWidth + 5, sy - 3, text='0', font=('Arial', 10), fill='#000000')
        self.create_text(mx - gridWidth, sy - lw * ia['k_m'] + lw/2, text=str(max_v[0]), font=('Arial', 10),
                         fill='#000000')

        # distance
        disx = ia['width'] - 80
        lw = ia['legendWidth'] * 15 / ia['k_d']
        for i, n in enumerate(ia['c_d']):
            self.create_line(disx, sy - (i + 0.35) * lw, disx + gridWidth, sy - (i + 0.35) * lw, width=int(round(lw)),
                             fill=n)
        self.create_text(disx + 12, ia['height'] - (ia['k_d'] + 4) * lw, text='Distance/km', font=('Arial', 10),
                         fill='#000000')
        self.create_text(disx + 12 + gridWidth, sy - 3, text='0', font=('Arial', 10), fill='#000000')
        self.create_text(disx + 25 + gridWidth, sy - lw * ia['k_d'], text='%.2f'%max_v[1], font=('Arial', 10),
                         fill='#000000')

    def highlight(self, gid):
        self.invalidate()
        ia = self.master.ia
        oxs, oys = computeCo(ia['gridWidth'] * 2, ia['dnum'] // 6)
        ixs, iys = computeCo(ia['gridWidth'] * 2 * ia['area_ratio'], ia['dnum'] // 6)
        fxs, fys = computeCo(ia['gridWidth'] * 2 + ia['margin'] * 2, ia['dnum'] // 6)

        cx = self.grids[gid].cenx
        cy = self.grids[gid].ceny
        oco = []
        ico = []
        border = []
        for i in range(ia['dnum']):
            oco.append([cx, cy, cx + ixs[i], cy + iys[i], cx + ixs[i + 1], cy + iys[i + 1]])
            ico.append([cx + ixs[i], cy + iys[i], cx + oxs[i], cy + oys[i], cx + oxs[i + 1], cy + oys[i + 1],
                 cx + ixs[i + 1], cy + iys[i + 1]])
            border.append(cx + fxs[i])
            border.append(cy + fys[i])
        border.append(cx + fxs[0])
        border.append(cy + fys[0])

        if self.SI_type == 0:
            for i in range(ia['dnum']):
                self.create_polygon(oco[i], fill=self.grids[gid].out_mcolor[i],
                                    outline=self.grids[gid].out_mcolor[i])
                self.create_polygon(ico[i], fill=self.grids[gid].out_dcolor[i],
                                    outline=self.grids[gid].out_dcolor[i])
            self.create_line(border, width=2, fill='#000000')
        elif self.SI_type == 1:
            for i in range(ia['dnum']):
                self.create_polygon(oco[i], fill=self.grids[gid].in_mcolor[i],
                                    outline=self.grids[gid].in_mcolor[i])
                self.create_polygon(ico[i], fill=self.grids[gid].in_dcolor[i],
                                    outline=self.grids[gid].in_dcolor[i])
            self.create_line(border, width=2, fill='#000000')


class flow_canvas(Canvas):
    def __init__(self, master, flows):
        Canvas.__init__(self, master, height=800, width=800, bg='white')
        self.flows = flows
        self.SI_type = 0  # 0: outgoing, 1: incomging
        self.ringroad = []
        self.read_ringroad()

    def set_p(self, flows, SI_type):
        self.flows = flows
        self.SI_type = SI_type
        self.invalidate()

    def read_ringroad(self):
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
                    self.ringroad.append(pts)
                    tag = int(sl[1])
                    pts = [(x, y)]
            self.ringroad.append(pts)

    def invalidate(self):
        self.delete(ALL)
        self.draw_flows()
        self.draw_ring_roads()

    def draw_ring_roads(self):
        for pts in self.ringroad:
            self.create_line(pts, fill='#000000', width=2)

    def draw_flows(self):
        for fid in self.flows:
            if self.flows[fid].select_tag:
                self.create_line(self.flows[fid].co, width=1, fill='#C0C0C0', arrow=LAST)

    def draw_target_flows(self, gid):
        self.invalidate()
        if self.SI_type == 0:
            for fid in self.master.pc.grids[gid].outFlow:
                self.create_line(self.flows[fid].co, width=1, fill='#0000FF', arrow=LAST)
        elif self.SI_type == 1:
            for fid in self.master.pc.grids[gid].inFlow:
                self.create_line(self.flows[fid].co, width=1, fill='#0000FF', arrow=LAST)