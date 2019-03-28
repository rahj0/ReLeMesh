# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 19:36:09 2018

@author: Rasmus
"""

from tkinter import *
import numpy as np
from Networks.BasicQNetwork import *

class meshEnvViewer():
    def __init__(self, master, env, lineDistance = 10, tfSession = None, qNetwork = None, resetOnStart = False):
        self._actionCount = 0
        self._tfSession = tfSession
        self._qNetwork = qNetwork
        self._gameOver = False
        self._env = env
        self._master = master
        master.wm_title("ReLeMesh")
        self._canvasWidth = self._env.getSizeX()
        self._canvasHeight = self._env.getSizeY()
        self._lineDistance = lineDistance
        self._canvasPixelWidth=(self._canvasWidth+2)*self._lineDistance
        self._canvasPxelHeight=(self._canvasHeight+2)*self._lineDistance
    
        self.score_frame = Frame(master)
        self.top_frame = Frame(master)
        self.bottom_frame = Frame(master)
        self.info_frame = Frame(master)
        self._canvas = Canvas(self.top_frame, 
           width=self._canvasPixelWidth,
           height=self._canvasPxelHeight)
        self._canvas.grid(row=1,column=1)
        self.createEmptyGrid()
        self._score = 0
        if resetOnStart:
            env.reset()
        self.paintState(env.getState())
        
        
        self._scoreLabel = Label(self.score_frame, text="Score: 0.0")
        self._scoreLabel.grid(row=0,column=0)
       
        
        self._cornerVariable = StringVar(master)
        self._cornerVariable.set("LeftCorner") # default value

        self._w = OptionMenu(self.bottom_frame, self._cornerVariable, "LeftCorner", "RightCorner").grid(row=0,column=2)
        
        bUp = Button(self.bottom_frame, text="Up", command=self.callback_up).grid(row=1,column=2)
        bDown = Button(self.bottom_frame, text="down", command=self.callback_down).grid(row=3,column=2)
        bLeft = Button(self.bottom_frame, text="left", command=self.callback_left).grid(row=2,column=1)
        bRight = Button(self.bottom_frame, text="right", command=self.callback_right).grid(row=2,column=3)
        
        Label(self.info_frame, text="Space: Change Corner to Control").pack()
        Label(self.info_frame, text="Arrow keys: Control selected corner position").pack()
        Label(self.info_frame, text="Enter: Next Object").pack()
        
        self._master.focus_set()
        self._master.bind("<space>", lambda e:self.callback_tab())
        
        self._master.bind("<Up>", lambda e:self.callback_up())
        self._master.bind("<Down>", lambda e:self.callback_down())
        self._master.bind("<Left>", lambda e:self.callback_left())
        self._master.bind("<Right>", lambda e:self.callback_right())
        self._master.bind("<Return>", lambda e:self.callback_enter())
        self._master.bind("0", lambda e:self.callback_key0())
        self._master.bind("1", lambda e:self.callback_key1())
        self._master.bind("2", lambda e:self.callback_key2())
        self._master.bind("3", lambda e:self.callback_key3())
        self._master.bind("4", lambda e:self.callback_key4())
        self._master.bind("5", lambda e:self.callback_key5())
        self._master.bind("6", lambda e:self.callback_key6())
        self._master.bind("7", lambda e:self.callback_key7())
        self._master.bind("8", lambda e:self.callback_key8())
        self._master.bind("q", lambda e:self.useNetworkToMove())

        self.score_frame.pack()
        self.top_frame.pack()
        self.info_frame.pack()

    def doAction(self, action):
        self._actionCount += 1
        indexAdd = 0
        if (self._cornerVariable.get() ==  "RightCorner"):
            indexAdd = 4
        if action == 8:
            indexAdd = 0
        (state,reward,done) = self._env.step(action+indexAdd)
        print(self._actionCount,reward)
        self._score += reward
        self.clearCanvas()
        self.paintState(state)
        scorText = "Score: " + str(self._score)
        self._scoreLabel.config(text=scorText)
        if(done):
            self._gaveOver = True
            self._scoreLabel.config(text=(scorText + "  --Game Over--"))
            
        
    def callback_tab(self):
        if (self._cornerVariable.get() ==  "LeftCorner"):
            self._cornerVariable.set("RightCorner")
        elif (self._cornerVariable.get() ==  "RightCorner"):
            self._cornerVariable.set("LeftCorner")
    def callback_enter(self):
        if not self._gameOver:
            self.doAction(8)            
    def callback_up(self):
        if not self._gameOver:
            self.doAction(2)
    def callback_down(self):
        if not self._gameOver:
            self.doAction(3)
    def callback_right(self):
        if not self._gameOver:
            self.doAction(0)
    def callback_left(self):
        if not self._gameOver:
            self.doAction(1)
    def callback_key0(self):
        if not self._gameOver:
            self.doAction(0)
    def callback_key1(self):
        if not self._gameOver:
            self.doAction(1)
    def callback_key2(self):
        if not self._gameOver:
            self.doAction(2)
    def callback_key3(self):
        if not self._gameOver:
            self.doAction(3)
    def callback_key4(self):
        if not self._gameOver:
            self.doAction(4)
    def callback_key5(self):
        if not self._gameOver:
            self.doAction(5)
    def callback_key6(self):
        if not self._gameOver:
            self.doAction(6)
    def callback_key7(self):
        if not self._gameOver:
            self.doAction(7)
    def callback_key8(self):
        if not self._gameOver:
            self.doAction(8)
    def useNetworkToMove(self):
        if self._tfSession != None:
            print(self._env.getSizeX())
            s = processState(self._env.getState(), self._env.getSizeX(), self._env.getNumberOfChannels())
            a = self._tfSession.run(self._qNetwork.predict,feed_dict={self._qNetwork.scalarInput:[s]})[0]
            self.doAction(a)

    def paintState(self,state):
        self.clearCanvas()
        self.createEmptyGrid()

        for colorBand in reversed(range(state.shape[2])):
            for i in range(state.shape[0]):
                for j in range(state.shape[1]):
                    if (state[i,j,colorBand] != 0):
                         self.paintPixel( i,j,colorBand,state[i,j,colorBand])
        
    def clearCanvas(self):
        self._canvas.delete("all")

    def createEmptyGrid(self):
       for x in range(self._lineDistance,self._canvasPixelWidth,self._lineDistance):
          self._canvas.create_line(x, 0, x, self._canvasPxelHeight, fill="#476042")
       for y in range(self._lineDistance,self._canvasPxelHeight,self._lineDistance):
          self._canvas.create_line(0, y, self._canvasPixelWidth, y, fill="#476042")
                             
       self._canvas.create_rectangle(0, 0, self._lineDistance, self._canvasPxelHeight, fill="#476042")
       self._canvas.create_rectangle(0, 0, self._canvasPixelWidth, self._lineDistance, fill="#476042")
       self._canvas.create_rectangle(0, 0, self._lineDistance, self._canvasPxelHeight, fill="#476042")
       self._canvas.create_rectangle(self._canvasPixelWidth-self._lineDistance, 0, self._canvasPixelWidth, self._canvasPxelHeight, fill="#476042")
       self._canvas.create_rectangle(self._lineDistance, self._canvasPxelHeight, self._canvasPixelWidth, self._canvasPxelHeight-self._lineDistance, fill="#476042")
                      
    def paintPixel(self, indexX, indexY, color, intensity):
        if (intensity == 0):
            return
        x0 = (indexX+1)*self._lineDistance
        y0 = (self._canvasHeight - indexY)*self._lineDistance

        colorID = "yellow"
        if color == 2:
            colorID = "blue"
        elif color == 1:
            colorID = "#1a8a1a"
            if intensity < 0.70:
                colorID = "#aacdaa"
            elif intensity < 1.0:
                colorID = "#72ad72"
        elif color == 0:
            colorID = "#ff0f0f"
            if intensity < 0.70:
                colorID = "#ffbbbb"
            elif intensity < 1.0:
                colorID = "#ff7877"
                
        self._canvas.create_rectangle(x0, y0, x0 + self._lineDistance, y0 + self._lineDistance, fill=colorID)

def createEnvCanvas(line_distance,tensor):
    canvas_width =  tensor.shape[0]
    canvas_height = tensor.shape[1] 
    pixelWidth=(canvas_width+2)*line_distance
    pixelHeight=(canvas_height+2)*line_distance
    b = Canvas(master, 
           width=pixelWidth,
           height=pixelHeight)
    checkered(b,line_distance,pixelWidth,pixelHeight)
    for colorBand in range(tensor.shape[2]):
        for i in range(canvas_width):
            for j in range(canvas_height):
                paintPixel(b, i,j,line_distance,canvas_width, canvas_height,colorBand)
    return b
    
