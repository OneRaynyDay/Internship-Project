#!/usr/local/bin/python

import wx
from PIL import Image
from PIL import ImageStat
import numpy

# Global variables

class imageStat(wx.Frame):
	def __init__(self, parent):
		# build a frame
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Image Statistics Calculator", size = (700, 220), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

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
		wx.StaticText(mainPanel, -1, "X ROI size", (210, 40), (70,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Y ROI size", (385, 40), (70,-1), wx.ALIGN_RIGHT)
		self.xroiDisplay = wx.TextCtrl(mainPanel, value = "200", pos=(285, 40), size = (90,-1))
		self.yroiDisplay = wx.TextCtrl(mainPanel, value = "200", pos=(460, 40), size = (90,-1))
		

		# build a text control for avg/std display ===========================================
		wx.StaticText(mainPanel, -1, "Average", (80, 90), (70,-1), wx.ALIGN_CENTER)
		wx.StaticText(mainPanel, -1, "Std Dev", (80, 120), (70,-1), wx.ALIGN_CENTER)		
		wx.StaticText(mainPanel, -1, "All", (150,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "B", (260,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Gb", (370,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "Gr", (480,70), (100,-1), wx.ALIGN_RIGHT)
		wx.StaticText(mainPanel, -1, "R", (590,70), (100,-1), wx.ALIGN_RIGHT)

		self.avgDisplay = wx.TextCtrl(mainPanel, value = "", pos=(150, 90), size=(100,-1), style=wx.TE_READONLY)
		self.avgDisplayB = wx.TextCtrl(mainPanel, value = "", pos=(260, 90), size=(100,-1), style=wx.TE_READONLY)
		self.avgDisplayGb = wx.TextCtrl(mainPanel, value = "", pos=(370, 90), size=(100,-1), style=wx.TE_READONLY)
		self.avgDisplayGr = wx.TextCtrl(mainPanel, value = "", pos=(480, 90), size=(100,-1), style=wx.TE_READONLY)
		self.avgDisplayR = wx.TextCtrl(mainPanel, value = "", pos=(590, 90), size=(100,-1), style=wx.TE_READONLY)

		self.stdDisplay = wx.TextCtrl(mainPanel, value = "", pos=(150, 120), size=(100,-1), style=wx.TE_READONLY)
		self.stdDisplayB = wx.TextCtrl(mainPanel, value = "", pos=(260, 120), size=(100,-1), style=wx.TE_READONLY)
		self.stdDisplayGb = wx.TextCtrl(mainPanel, value = "", pos=(370, 120), size=(100,-1), style=wx.TE_READONLY)
		self.stdDisplayGr = wx.TextCtrl(mainPanel, value = "", pos=(480, 120), size=(100,-1), style=wx.TE_READONLY)
		self.stdDisplayR = wx.TextCtrl(mainPanel, value = "", pos=(590, 120), size=(100,-1), style=wx.TE_READONLY)

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
		self.avgDisplay.Clear()
		self.avgDisplayB.Clear()
		self.avgDisplayGb.Clear()
		self.avgDisplayGr.Clear()
		self.avgDisplayR.Clear()
		self.stdDisplay.Clear()
		self.stdDisplayB.Clear()
		self.stdDisplayGb.Clear()
		self.stdDisplayGr.Clear()
		self.stdDisplayR.Clear()

	# function for reading and calculating
	def Calculate(self, event):
		try:
			# update status
			self.statusText.SetValue("Processing...")
			self.statusText.SetForegroundColour(wx.BLACK)
			
			# try reading the file
			self.im = Image.open(self.fileDisplay.GetValue())
			width, height = self.im.size

			# attempt to fetch x roi data
			try:
				self.xroi = int(self.xroiDisplay.GetValue())
				# check for out of bounds conditions
				if self.xroi > width:
					#throw error
					self.statusText.SetValue("Error: x ROI out of bounds, max x = " + str(width) + ", max y = " + str(height))
					self.statusText.SetForegroundColour(wx.RED)
					return
				# check to make sure greater than 0
				if self.xroi < 1:
					#throw error
					self.statusText.SetValue("Error: ROI values must be greater than 0")
					self.statusText.SetForegroundColour(wx.RED)
					return	
				# check to make sure it is even
				if self.xroi % 2 == 1:
					#throw error
					self.statusText.SetValue("Error: ROI values must be even")
					self.statusText.SetForegroundColour(wx.RED)
					return

			except ValueError:
				#throw error
				self.statusText.SetValue("Error: please enter integer ROI value")
				self.statusText.SetForegroundColour(wx.RED)
				return
			# attempt to fetch y roi data
			try:
				self.yroi = int(self.yroiDisplay.GetValue())
				# check for out of bounds conditions
				if self.yroi > height:
					#throw error
					self.statusText.SetValue("Error: y ROI out of bounds, max x = " + str(width) + ", max y = " + str(height))
					self.statusText.SetForegroundColour(wx.RED)
					return
				# check to make sure greater than 0
				if self.yroi < 1:
					#throw error
					self.statusText.SetValue("Error: ROI values must be greater than 0")
					self.statusText.SetForegroundColour(wx.RED)
					return
				# check to make sure it is even
				if self.yroi % 2 == 1:
					#throw error
					self.statusText.SetValue("Error: ROI values must be even")
					self.statusText.SetForegroundColour(wx.RED)
					return
			except ValueError:
				#throw error
				self.statusText.SetValue("Error: please enter integer ROI value")
				self.statusText.SetForegroundColour(wx.RED)
				return

			# convert into matrices			
			self.mat = numpy.array(self.im)
			# apply roi
			self.mat = self.mat[height/2 - self.yroi/2:height/2 + self.yroi/2, width/2 - self.xroi/2:width/2 + self.xroi/2, 0]
			# get each channel
			self.bmat = self.mat[0:self.yroi:2, 0:self.xroi:2]
			self.gbmat = self.mat[0:self.yroi:2, 1:self.xroi:2]
			self.grmat = self.mat[1:self.yroi:2, 0:self.xroi:2]
			self.rmat = self.mat[1:self.yroi:2, 1:self.xroi:2]
	
			# calculate and display mean
			self.avgDisplay.Clear()
			self.avgDisplay.AppendText(str(numpy.around(numpy.mean(self.mat), decimals=4)))
			self.avgDisplayB.Clear()
			self.avgDisplayB.AppendText(str(numpy.around(numpy.mean(self.bmat), decimals=4)))
			self.avgDisplayGb.Clear()
			self.avgDisplayGb.AppendText(str(numpy.around(numpy.mean(self.gbmat), decimals=4)))
			self.avgDisplayGr.Clear()
			self.avgDisplayGr.AppendText(str(numpy.around(numpy.mean(self.grmat), decimals=4)))
			self.avgDisplayR.Clear()
			self.avgDisplayR.AppendText(str(numpy.around(numpy.mean(self.rmat), decimals=4)))

			# calculate and display std
			self.stdDisplay.Clear()
			self.stdDisplay.AppendText(str(numpy.around(numpy.std(self.mat), decimals=4)))
			self.stdDisplayB.Clear()
			self.stdDisplayB.AppendText(str(numpy.around(numpy.std(self.bmat), decimals=4)))
			self.stdDisplayGb.Clear()
			self.stdDisplayGb.AppendText(str(numpy.around(numpy.std(self.gbmat), decimals=4)))
			self.stdDisplayGr.Clear()
			self.stdDisplayGr.AppendText(str(numpy.around(numpy.std(self.grmat), decimals=4)))
			self.stdDisplayR.Clear()
			self.stdDisplayR.AppendText(str(numpy.around(numpy.std(self.rmat), decimals=4)))

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


# end class 
# ============================================================================================

# below is needed for all GUIs
if __name__== '__main__':
	app = wx.App(False) # application object (inner workings) PySimpleApp
	frame = imageStat(parent = None) # frame object (what user sees)
	frame.Show() # show frame
	app.MainLoop() # run main loop	

