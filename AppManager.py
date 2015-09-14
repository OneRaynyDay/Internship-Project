from DarkNoiseGrapherv2 import DarkNoiseGrapher
from NoiseGrapher import NoiseGrapher
from imageCalc2Beta import imageCalc
from imageWDPixel import imageWDPixel
import wx
from PIL import Image
import numpy
import os

class AppManager(wx.Frame):
    CHOICES = {}
    def __init__(self, parent):
        # build a frame
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Image Calculator", size = (700, 170), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        frameSize = wx.DisplaySize()
        print frameSize
        self.CHOICES = {"ImageCalc2Beta": imageCalc(parent = None), 
        "ImageWDPixel": imageWDPixel(parent = None), 
        "NoiseGrapher": NoiseGrapher(parent = None), 
        "DarkNoiseGrapherV2": DarkNoiseGrapher(None, frameSize)}
        # build a panelz
	self.mainPanel = wx.Panel(self, wx.ID_ANY)
	
	# sizer
	self.buttonSizer = wx.GridSizer(4,0)
	# build buttons for selecting files ==================================================
	self.imageCalc2Beta = wx.Button(self.mainPanel, id=wx.ID_ANY, label = "Open ImageCalc2Beta")
	self.imageCalc2Beta.name = "ImageCalc2Beta"
	self.imageCalc2Beta.Bind(wx.EVT_BUTTON, self.openApp)
	self.ImageWDPixel = wx.Button(self.mainPanel, id=wx.ID_ANY, label = "Open ImageWDPixel")
	self.ImageWDPixel.name = "ImageWDPixel"
	self.ImageWDPixel.Bind(wx.EVT_BUTTON, self.openApp)
	self.NoiseGrapher = wx.Button(self.mainPanel, id=wx.ID_ANY, label = "Open NoiseGrapher")
	self.NoiseGrapher.name = "NoiseGrapher"
	self.NoiseGrapher.Bind(wx.EVT_BUTTON, self.openApp)
	self.DarkNoiseGrapherV2 = wx.Button(self.mainPanel, id=wx.ID_ANY, label = "Open DarkNoiseGrapherV2")
	self.DarkNoiseGrapherV2.name = "DarkNoiseGrapherV2"
	self.DarkNoiseGrapherV2.Bind(wx.EVT_BUTTON, self.openApp)
	
	#adding buttons into sizer
	self.buttonSizer.Add(self.imageCalc2Beta)
        self.buttonSizer.Add(self.ImageWDPixel)
        self.buttonSizer.Add(self.NoiseGrapher)
        self.buttonSizer.Add(self.DarkNoiseGrapherV2)   
        
        #Setting sizer to panel
        self.mainPanel.SetSizer(self.buttonSizer)
        self.mainPanel.Layout()
        
    def openApp(self, event):
        self.frame = self.CHOICES[event.GetEventObject().name]
        self.frame.Show()
# below is needed for all GUIs
if __name__== '__main__':
	app = wx.App(False) # application object (inner workings) 
	frame = AppManager(parent = None) # frame object (what user sees)
	frame.Show() # show frame
	app.MainLoop() # run main loop	
		