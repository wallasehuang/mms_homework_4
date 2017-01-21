#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pylab import *

import pickle

from Tkinter import *
from PIL import ImageTk, Image
import tkMessageBox
import tkFileDialog
from ttk import Frame, Button, Label, Style
import mosaic_by_color_layout as mosaic
# import image_retrieval_q1 as q1
# import image_retrieval_q2 as q2
# import image_retrieval_q3 as q3
# import image_retrieval_q4 as q4

from random import randint


class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()


    def initUI(self):

        self.parent.title("Mosaic")

        self.pack(fill=BOTH, expand=1)

        Button(self, text = "Select File", command = openFile).grid(row=0, column=0, pady=5)
        self.fileName = StringVar()
        Label(self, textvariable=self.fileName).grid(row=0, column=1, columnspan=2, pady=5, sticky=W)

        Label(self, text = "Select N: ").grid(row=1, column=0, pady=5)
        mode = StringVar(self)
        mode.set("N = 20")
        om = OptionMenu(self, mode, "N = 10", "N = 20", "N = 30", "N = 40")
        om.grid(row=1, column=1, pady=5, sticky=W)

        Button(self, text = "Generate image", command = lambda: generateImage(self.fileName.get(),mode.get())).grid(row=3, column=0, pady=5)


def openFile ():
    fileName = tkFileDialog.askopenfilename(initialdir = "./dataset")
    app.fileName.set(fileName)


def generateImage (fileName,mode):
    size = 128,128
    img = Image.open(fileName)
    img.thumbnail(size,Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    search_img = Label(app,image = img)
    search_img.image = img
    search_img.pack()
    search_img.place(x=440,y=20)

    n = 20
    if(mode == 'N = 10'):
        n = 10
    if(mode == 'N = 20'):
        n = 20
    if(mode == 'N = 30'):
        n = 30
    if(mode == 'N = 40'):
        n = 40

    if(mosaic.mosaic(fileName,n)):
        size = 512,512
        img = Image.open('mosaic.jpg')
        img.thumbnail(size,Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        result_img = Label(app,image = img)
        result_img.image = img
        result_img.pack()
        result_img.place(x = 55,y= 120)


if __name__ == '__main__':
    root = Tk()
    size = 220, 250

    app = Example(root)
    root.geometry("620x550")
    root.mainloop()


