# -*- coding: utf-8 -*-：

import numpy as np

class Glyph(object):
    def __init__(self, gid, dnum):
        # 格网ID
        self.gid = gid
        # 关联的流集合
        self.outFlow = []
        self.inFlow = []

        self.wm = [0] * dnum
        self.wd = [0] * dnum

        self.mcolor = []
        self.dcolor = []
        self.cenx = -1
        self.ceny = -1

        self.ld = []
        for i in range(dnum):
            self.ld.append([])
        self.round_flow_num = 0

    def addOutFlow(self, fid):
        self.outFlow.append(fid)

    def addInFlow(self, fid):
        self.inFlow.append(fid)

    def calcOutAggregation(self, flows):
        for fid in self.outFlow:
            td, ta = self.calcInteraction(flows[fid])
            tm = 1
            idx, tw = self.calcMD(ta, len(self.wm))
            self.wm[idx] += tm
            self.wd[idx] += tm * td

        for i in range(len(self.wm)):
            if self.wm[i] != 0:
                self.wd[i] /= self.wm[i]

    def calcOutList(self, flows):
        for fid in self.outFlow:
            td, ta = self.calcInteraction(flows[fid])
            idx, tw = self.calcMD(ta, len(self.ld))
            self.ld[idx].append(td)

    # compute main interaction direction
    @staticmethod
    def calcMD(a, n):
        d = np.array([i * 2 * np.pi / n for i in range(n)]) + np.pi / n
        w = np.cos(d - a)
        idx = np.where(w == np.max(w))[0][0]
        return idx, w[idx]

    @staticmethod
    def calcInteraction(flow):
        dx = flow[1][0]-flow[0][0]
        dy = flow[1][1]-flow[0][1]
        d = np.sqrt(dy**2+dx**2)
        a = abs(np.arcsin(dy/d))
        if dx > 0:
            if dy < 0:
                a = 2*np.pi - a
            elif dy == 0:
                a = 0
        elif dx < 0:
            if dy > 0:
                a = np.pi - a
            elif dy < 0:
                a += np.pi
            else:
                a = np.pi
        else:
            if dy > 0:
                a = 0.5*np.pi
            elif dy < 0:
                a = 1.5*np.pi
            else:
                a = -1

        return d/1000.0, a  # return distance (km) and azimuth


class Hexagon(Glyph):
    def __init__(self, gid, dnum=6):
        Glyph.__init__(self, gid, dnum)


class Square(Glyph):
    def __init__(self, gid, dnum=8):
        Glyph.__init__(self, gid, dnum)