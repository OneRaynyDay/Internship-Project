#!/usr/local/bin/python

import wx
from PIL import Image
#import ImageStat
import numpy
import scipy
from scipy.signal import convolve2d

# Global variables

class imageWDPixel(wx.Frame):
	def __init__(self, parent):
		# build a frame
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Image WD Pixel Calculator", size = (700, 220), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

		# build a panel
		mainPanel = wx.Panel(self, wx.ID_ANY)

		# build a status bar =================================================================
		statusBar = self.CreateStatusBar()

		# build a menu bar ===================================================================
		menuBar = wx.MenuBar()
		self.SetMenuBar(menuBar)

		# build buttons for selecting files ==================================================
		openButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Open...", pos=(595, 5), size=(90,-1))
		openButton.Bind(wx.EVT_BUTTON, self.FileSelect)

		# build a text control for file display ==============================================
		self.fileDisplay = wx.TextCtrl(mainPanel, value = "File name", pos=(10,10), size=(580,-1))
		
		# build a text control for roi =======================================================
		wx.StaticText(mainPanel, -1, "Threshold (DN)", (210, 40), (100,-1), wx.ALIGN_RIGHT)
		self.threshDisplay = wx.TextCtrl(mainPanel, value = "16", pos=(315, 40), size = (90,-1))
		
		# build a checkbox ===================================================================
		self.ppmCheck = wx.CheckBox(mainPanel, -1, "Display PPM", (415, 40))
		self.ppmCheck.SetValue(True)

		# declare number of decimal places
		self.decimals = 4

		wx.EVT_CHECKBOX(self, self.ppmCheck.GetId(), self.ShowPPM)

		# build a text control for avg/std display ===========================================
		wx.StaticText(mainPanel, -1, "White Pixels", (65, 90), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Dark Pixels", (65, 120), (100,-1), wx.ALIGN_RIGHT)		
		wx.StaticText(mainPanel, -1, "All", (150,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "B", (260,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Gb", (370,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Gr", (480,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "R", (590,70), (100,-1), wx.ALIGN_RIGHT)

		self.wDisplay = wx.TextCtrl(mainPanel, value = "", pos=(150, 90), size=(100,-1), style=wx.TE_READONLY)
		self.wDisplayB = wx.TextCtrl(mainPanel, value = "", pos=(260, 90), size=(100,-1), style=wx.TE_READONLY)
		self.wDisplayGb = wx.TextCtrl(mainPanel, value = "", pos=(370, 90), size=(100,-1), style=wx.TE_READONLY)
		self.wDisplayGr = wx.TextCtrl(mainPanel, value = "", pos=(480, 90), size=(100,-1), style=wx.TE_READONLY)
		self.wDisplayR = wx.TextCtrl(mainPanel, value = "", pos=(590, 90), size=(100,-1), style=wx.TE_READONLY)

		self.dDisplay = wx.TextCtrl(mainPanel, value = "", pos=(150, 120), size=(100,-1), style=wx.TE_READONLY)
		self.dDisplayB = wx.TextCtrl(mainPanel, value = "", pos=(260, 120), size=(100,-1), style=wx.TE_READONLY)
		self.dDisplayGb = wx.TextCtrl(mainPanel, value = "", pos=(370, 120), size=(100,-1), style=wx.TE_READONLY)
		self.dDisplayGr = wx.TextCtrl(mainPanel, value = "", pos=(480, 120), size=(100,-1), style=wx.TE_READONLY)
		self.dDisplayR = wx.TextCtrl(mainPanel, value = "", pos=(590, 120), size=(100,-1), style=wx.TE_READONLY)

		# build a text control for status display ============================================
		self.statusText = wx.TextCtrl(mainPanel, value = "", pos=(10, 150), size=(680,-1), style=wx.TE_READONLY)

		# build a button for reading in the image and processing =============================
		calcButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Calculate", pos=(5, 35), size=(90,-1))
		calcButton.Bind(wx.EVT_BUTTON, self.Calculate)

		# build a button for displaying image ================================================
		dispButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Display", pos=(105, 35), size=(90,-1))
		dispButton.Bind(wx.EVT_BUTTON, self.Display)

	# define callbacks
	# ========================================================================================
	

	# function for closing window
	def CloseWindow(self, event):
		self.Destroy()
	
	# function for file selection
	def FileSelect(self, event):
		fileDialog = wx.FileDialog(None, "Select a bmp file", "", "", "BMP files (*.bmp)|*.bmp", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

		# user canceled file opening
		if fileDialog.ShowModal() == wx.ID_CANCEL:
			return
			   
		# otherwise, proceed loading the file chosen by the user
		self.fileName = fileDialog.GetPath()
		self.fileDisplay.Clear()
		self.fileDisplay.AppendText(self.fileName)
		self.wDisplay.Clear()
		self.wDisplayB.Clear()
		self.wDisplayGb.Clear()
		self.wDisplayGr.Clear()
		self.wDisplayR.Clear()
		self.dDisplay.Clear()
		self.dDisplayB.Clear()
		self.dDisplayGb.Clear()
		self.dDisplayGr.Clear()
		self.dDisplayR.Clear()

	# function for reading and calculating
	def Calculate(self, event):
		try:
			# update status
			self.statusText.SetValue("Processing...")
			self.statusText.SetForegroundColour(wx.BLACK)
			
			# try reading the file
			self.im = Image.open(self.fileDisplay.GetValue())
			self.width, self.height = self.im.size

			# attempt to fetch x roi data
			try:
				self.thresh = int(self.threshDisplay.GetValue())
				# check for out of bounds conditions
				if self.thresh > self.width:
					#throw error
					self.statusText.SetValue("Error: x ROI out of bounds, max x = " + str(self.width) + ", max y = " + str(self.height))
					self.statusText.SetForegroundColour(wx.RED)
					return
				# check to make sure greater than 0
				if self.thresh < 1:
					#throw error
					self.statusText.SetValue("Error: ROI values must be greater than 0")
					self.statusText.SetForegroundColour(wx.RED)
					return	
			except ValueError:
				#throw error
				self.statusText.SetValue("Error: please enter integer ROI value")
				self.statusText.SetForegroundColour(wx.RED)
				return

			# convert into matrices			
			self.mat = numpy.array(self.im)
			self.mat = self.mat[:, :, 1] # extract only first channel
			self.bmat = self.mat[0:self.height:2, 0:self.width:2]
			self.gbmat = self.mat[0:self.height:2, 1:self.width:2]
			self.grmat = self.mat[1:self.height:2, 0:self.width:2]
			self.rmat = self.mat[1:self.height:2, 1:self.width:2]

			# calculate average matrix
			self.avgMat = self.GetAvgMat(self.mat, self.height, self.width)
			self.avgMatB = self.avgMat[0:self.height:2, 0:self.width:2]
			self.avgMatGb = self.avgMat[0:self.height:2, 1:self.width:2]
			self.avgMatGr = self.avgMat[1:self.height:2, 0:self.width:2]
			self.avgMatR = self.avgMat[1:self.height:2, 1:self.width:2]

			# calculate white and dark matrices
			self.darkMat = self.avgMat - self.mat
			self.darkMatB = self.avgMatB - self.bmat
			self.darkMatGb = self.avgMatGb - self.gbmat
			self.darkMatGr = self.avgMatGr - self.grmat
			self.darkMatR = self.avgMatR -self.rmat
			self.whiteMat = self.mat - self.avgMat
			self.whiteMatB = self.bmat - self.avgMatB
			self.whiteMatGb = self.gbmat - self.avgMatGb
			self.whiteMatGr = self.grmat - self.avgMatGr
			self.whiteMatR = self.rmat - self.avgMatR
                        
			# calculate ppmFactor (default display count)
			self.ppmFactor = 1
			self.ppmFactor2 = 1
			# check to see if checkbox is checked
			if self.ppmCheck.GetValue():
				self.ppmFactor = float(self.height*self.width)/1000000
				self.ppmFactor2 = float(self.height*self.width)/4/1000000

			# display values
			self.wVal = float(len(self.whiteMat[self.whiteMat > self.thresh]))/self.ppmFactor
			self.wValB = float(len(self.whiteMatB[self.whiteMatB > self.thresh]))/self.ppmFactor2
			self.wValGb = float(len(self.whiteMatGb[self.whiteMatGb > self.thresh]))/self.ppmFactor2
			self.wValGr = float(len(self.whiteMatGr[self.whiteMatGr > self.thresh]))/self.ppmFactor2
			self.wValR = float(len(self.whiteMatR[self.whiteMatR > self.thresh]))/self.ppmFactor2
			
			self.dVal = float(len(self.darkMat[self.darkMat > self.thresh]))/self.ppmFactor
			self.dValB = float(len(self.darkMatB[self.darkMatB > self.thresh]))/self.ppmFactor2
			self.dValGb = float(len(self.darkMatGb[self.darkMatGb > self.thresh]))/self.ppmFactor2
			self.dValGr = float(len(self.darkMatGr[self.darkMatGr > self.thresh]))/self.ppmFactor2
			self.dValR = float(len(self.darkMatR[self.darkMatR > self.thresh]))/self.ppmFactor2

			# calculate and display white pixels
			self.wDisplay.Clear()
			self.wDisplay.AppendText(str(numpy.around(self.wVal, decimals=self.decimals)))
			self.wDisplayB.Clear()
			self.wDisplayB.AppendText(str(numpy.around(self.wValB, decimals=self.decimals)))
			self.wDisplayGb.Clear()
			self.wDisplayGb.AppendText(str(numpy.around(self.wValGb, decimals=self.decimals)))
			self.wDisplayGr.Clear()
			self.wDisplayGr.AppendText(str(numpy.around(self.wValGr, decimals=self.decimals)))
			self.wDisplayR.Clear()
			self.wDisplayR.AppendText(str(numpy.around(self.wValR, decimals=self.decimals)))

			# calculate and display dark pixels
			self.dDisplay.Clear()
			self.dDisplay.AppendText(str(numpy.around(self.dVal, decimals=self.decimals)))
			self.dDisplayB.Clear()
			self.dDisplayB.AppendText(str(numpy.around(self.dValB, decimals=self.decimals)))
			self.dDisplayGb.Clear()
			self.dDisplayGb.AppendText(str(numpy.around(self.dValGb, decimals=self.decimals)))
			self.dDisplayGr.Clear()
			self.dDisplayGr.AppendText(str(numpy.around(self.dValGr, decimals=self.decimals)))
			self.dDisplayR.Clear()
			self.dDisplayR.AppendText(str(numpy.around(self.dValR, decimals=self.decimals)))

			# update status
			self.statusText.SetValue("Done.")
			self.statusText.SetForegroundColour(wx.BLACK)
		except IOError:
			# throw error
			self.statusText.SetValue("Error: cannot read file.")
			self.statusText.SetForegroundColour(wx.RED)

	# function for displaying
	def Display(self, event):
		try:
			# update status
			self.statusText.SetValue("Processing...")
			self.statusText.SetForegroundColour(wx.BLACK)
			# try reading the file
			self.im = Image.open(self.fileDisplay.GetValue())
			# display image
			self.im.show()
			# update status
			self.statusText.SetValue("Done.")
			self.statusText.SetForegroundColour(wx.BLACK)
		except IOError:
			# throw error
			self.statusText.SetValue("Error: cannot read file.")
			self.statusText.SetForegroundColour(wx.RED)
	
	# function for checkbox event
	def ShowPPM(self, event):
		try:
			# calculate ppmFactor (default display count)
			self.ppmFactor = 1
			self.ppmFactor2 = 1
			# check to see if checkbox is checked
			if self.ppmCheck.GetValue():
				self.ppmFactor = float(self.height*self.width)/1000000
				self.ppmFactor2 = float(self.height*self.width)/4/1000000

			# display values
			self.wVal = float(len(self.whiteMat[self.whiteMat > self.thresh]))/self.ppmFactor
			self.wValB = float(len(self.whiteMatB[self.whiteMatB > self.thresh]))/self.ppmFactor2
			self.wValGb = float(len(self.whiteMatGb[self.whiteMatGb > self.thresh]))/self.ppmFactor2
			self.wValGr = float(len(self.whiteMatGr[self.whiteMatGr > self.thresh]))/self.ppmFactor2
			self.wValR = float(len(self.whiteMatR[self.whiteMatR > self.thresh]))/self.ppmFactor2
			
			self.dVal = float(len(self.darkMat[self.darkMat > self.thresh]))/self.ppmFactor
			self.dValB = float(len(self.darkMatB[self.darkMatB > self.thresh]))/self.ppmFactor2
			self.dValGb = float(len(self.darkMatGb[self.darkMatGb > self.thresh]))/self.ppmFactor2
			self.dValGr = float(len(self.darkMatGr[self.darkMatGr > self.thresh]))/self.ppmFactor2
			self.dValR = float(len(self.darkMatR[self.darkMatR > self.thresh]))/self.ppmFactor2

			# calculate and display white pixels
			self.wDisplay.Clear()
			self.wDisplay.AppendText(str(numpy.around(self.wVal, decimals=self.decimals)))
			self.wDisplayB.Clear()
			self.wDisplayB.AppendText(str(numpy.around(self.wValB, decimals=self.decimals)))
			self.wDisplayGb.Clear()
			self.wDisplayGb.AppendText(str(numpy.around(self.wValGb, decimals=self.decimals)))
			self.wDisplayGr.Clear()
			self.wDisplayGr.AppendText(str(numpy.around(self.wValGr, decimals=self.decimals)))
			self.wDisplayR.Clear()
			self.wDisplayR.AppendText(str(numpy.around(self.wValR, decimals=self.decimals)))

			# calculate and display dark pixels
			self.dDisplay.Clear()
			self.dDisplay.AppendText(str(numpy.around(self.dVal, decimals=self.decimals)))
			self.dDisplayB.Clear()
			self.dDisplayB.AppendText(str(numpy.around(self.dValB, decimals=self.decimals)))
			self.dDisplayGb.Clear()
			self.dDisplayGb.AppendText(str(numpy.around(self.dValGb, decimals=self.decimals)))
			self.dDisplayGr.Clear()
			self.dDisplayGr.AppendText(str(numpy.around(self.dValGr, decimals=self.decimals)))
			self.dDisplayR.Clear()
			self.dDisplayR.AppendText(str(numpy.around(self.dValR, decimals=self.decimals)))
		except AttributeError:
			# do nothing
			# calculate ppmFactor (default display count)
			self.ppmFactor = 1
			self.ppmFactor2 = 1

	# function for calculating avg matrix
	def GetAvgMat(self, mat, height, width):
		convMat = numpy.zeros((height+2, width+2))
		convMat[1:height+1, 1:width+1] = mat # center is the same
		# get edges
		convMat[1:height+1, 0] = mat[0:height, 1] # first col is second col in mat
		convMat[1:height+1, width+1] = mat[0:height, width-2] # last col is second to last col	
		convMat[0, 1:width+1] = mat[1, 0:width] # first row is second row in mat
		convMat[height+1, 1:width+1] = mat[height-1, 0:width] # last row is second to last row 
		# get corners
		convMat[0, 0] = mat[1, 1]
		convMat[0, width+1] = mat[1, width-2] 
		convMat[height+1, 0] = mat[height-2, 1]
		convMat[height+1, width+1] = mat[height-2, width-2]

		averager = numpy.ones((3,3))/9
		avgMatTemp = convolve2d(convMat, averager)
		avgMat = avgMatTemp[2:height+2, 2:width+2]
		return avgMat
	       


# end class 
# ============================================================================================

# below is needed for all GUIs
if __name__== '__main__':
	app = wx.App(False) # application object (inner workings) PySimpleApp
	frame = imageWDPixel(parent = None) # frame object (what user sees)
	frame.Show() # show frame
	app.MainLoop() # run main loop	


