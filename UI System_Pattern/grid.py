# -*- coding: utf-8 -*-：

import numpy as np

class Grid(object):
    def __init__(self, gid, dnum):
        # 格网ID
        self.gid = gid
        # 关联的流集合
        self.outFlow = []
        self.inFlow = []

        self.dnum = dnum

        self.cenx = -1
        self.ceny = -1
        self.oco = [] # 外侧三角形
        self.ico = [] # 内侧三角形
        self.border = [] # 黑边

        self.out_wm = [0]*dnum
        self.out_wd = [0]*dnum
        self.out_mcolor = []
        self.out_dcolor = []

        self.in_wm = [0] * dnum
        self.in_wd = [0] * dnum
        self.in_mcolor = []
        self.in_dcolor = []

    def reset(self):
        self.out_mcolor = []
        self.out_dcolor = []
        self.in_mcolor = []
        self.in_dcolor = []

    def addOutFlow(self, fid):
        self.outFlow.append(fid)

    def addInFlow(self, fid):
        self.inFlow.append(fid)

    def calcOutAggregation(self, flows):
        for fid in self.outFlow:
            td, ta = self.calcInteraction(flows[fid].co)
            tm = 1
            idx, tw = self.calcMD(ta, self.dnum)
            self.out_wm[idx] += tm
            self.out_wd[idx] += tm * td

        for i in range(self.dnum):
            if self.out_wm[i] != 0:
                self.out_wd[i] /= self.out_wm[i]

    def calcInAggregation(self, flows):
        for fid in self.inFlow:
            td, ta = self.calcInteraction(flows[fid].co)
            tm = 1
            idx, tw = self.calcMD(ta, self.dnum)
            idx = (idx + 3) % 6
            self.in_wm[idx] += tm
            self.in_wd[idx] += tm * td

        for i in range(self.dnum):
            if self.in_wm[i] != 0:
                self.in_wd[i] /= self.in_wm[i]

    # compute main interaction direction
    @staticmethod
    def calcMD(a, n):
        d = np.array([i*2*np.pi/n for i in range(n)]) + np.pi/n
        w = np.cos(d-a)
        idx = np.where(w==np.max(w))[0][0]
        return idx, w[idx]

    @staticmethod
    def calcInteraction(flow):
        dx = flow[1][0]-flow[0][0]
        dy = flow[1][1]-flow[0][1]
        d = np.sqrt(dy**2+dx**2)
        a = abs(np.arcsin(dy/d))
        if dx>0:
            if dy<0:
                a = 2*np.pi - a
            elif dy==0:
                a = 0
        elif dx<0:
            if dy>0:
                a = np.pi - a
            elif dy<0:
                a += np.pi
            else:
                a = np.pi
        else:
            if dy>0:
                a = 0.5*np.pi
            elif dy<0:
                a = 1.5*np.pi
            else:
                a = -1

        return d/1000.0, a  #距离单位以km计算


class Flow(object):
    def __init__(self, fid, co, ogid, dgid):
        self.fid = fid
        self.co = co
        self.ogid = ogid
        self.dgid = dgid
        self.color = '#000000'
        self.select_tag = False
