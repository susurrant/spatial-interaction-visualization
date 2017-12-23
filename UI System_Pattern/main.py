#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

import tkinter as tk
from mapView import *



if __name__ == '__main__':
    root = tk.Tk()
    root.title("Spatial Interaction Pattern")
    root.geometry('1600x870')
    gui = MapGUI(root)
    gui.place(x=0, y=0)

    root.mainloop()
