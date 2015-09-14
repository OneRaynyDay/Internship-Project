
import wx
import csv
import numpy as np
from matplotlib.figure import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from PIL import Image as im

from library import *

class NoiseGrapher(wx.Frame):

	fileList = ["No file selected", "Open..."]
	bitList = ["8-bit", "10-bit"]
	bitDict = {0: 8, 1: 10}

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Noise Grapher v0.5.3", size=(1115,760))
		# set minimum size
		self.SetMinSize(self.GetSize())
		self.SetMaxSize(self.GetSize())

		# build a panel
		self.mp = wx.Panel(self, wx.ID_ANY)

		# build a status bar 
		self.statusBar = self.CreateStatusBar()

		# file selection
		self.fileDisplay = wx.Choice(self.mp, -1, size=(580,-1), choices = self.fileList)
		self.fileDisplay.SetSelection(0)
		self.fileDisplay.Bind(wx.EVT_CHOICE, self.SelectFile)

		# create tab panels
		self.figurebook = FigureBook(self.mp, self)
		#self.mp.Bind(wx.EVT_SIZE, self.OnResize)

		# create input fields
		self.bitchoice = wx.Choice(self.mp, -1, size=(105,-1), choices = self.bitList)
		self.bitchoice.SetSelection(0)
		self.bitchoice.Bind(wx.EVT_CHOICE, self.Calculate)
		self.sftext = wx.StaticText(self.mp, -1, "SF Gain (X)", size=(75, -1), style=wx.ALIGN_RIGHT)
		self.sfdisp = wx.TextCtrl(self.mp, value="0.9", size=(75,-1))
		self.sfdisp.Bind(wx.EVT_KEY_UP, self.Calculate)
		self.adctext = wx.StaticText(self.mp, -1, "ADC (mV)", size=(75, -1), style=wx.ALIGN_RIGHT)
		self.adcdisp = wx.TextCtrl(self.mp, value="1000", size=(75,-1))
		self.adcdisp.Bind(wx.EVT_KEY_UP, self.Calculate)
		self.offtext = wx.StaticText(self.mp, -1, "Offset (DN)", size=(75, -1), style=wx.ALIGN_RIGHT)
		self.offdisp = wx.TextCtrl(self.mp, value="10", size=(75,-1))
		self.offdisp.Bind(wx.EVT_KEY_UP, self.Graph)
		
		# create data fields
		self.xtext = wx.StaticText(self.mp, -1, "X", size=(40, -1), style=wx.ALIGN_RIGHT)
		self.ytext = wx.StaticText(self.mp, -1, "Y", size=(40, -1), style=wx.ALIGN_RIGHT)
		self.blanktext = wx.StaticText(self.mp, -1, "", size=(40,-1), style=wx.ALIGN_LEFT)
		
		self.lefttext = wx.StaticText(self.mp, -1, "Left", size=(75,-1), style=wx.ALIGN_LEFT)
		self.lefttext.SetForegroundColour('blue')
		self.leftxdisp = wx.TextCtrl(self.mp, value="0.0", size=(75,-1), style=wx.TE_READONLY)
		self.leftydisp = wx.TextCtrl(self.mp, value="0.0", size=(75,-1), style=wx.TE_READONLY)
		self.righttext = wx.StaticText(self.mp, -1, "Right", size=(75,-1), style=wx.ALIGN_LEFT)
		self.righttext.SetForegroundColour('red')
		self.rightxdisp = wx.TextCtrl(self.mp, value="0.0", size=(75,-1), style=wx.TE_READONLY)
		self.rightydisp = wx.TextCtrl(self.mp, value="0.0", size=(75,-1), style=wx.TE_READONLY)
		
		self.blanktext2 = wx.StaticText(self.mp, -1, "", size=(50,-1), style=wx.ALIGN_LEFT)
		self.blanktext3 = wx.StaticText(self.mp, -1, "", size=(50,-1), style=wx.ALIGN_LEFT)
		self.btext = wx.StaticText(self.mp, -1, "Blue", size=(75,-1), style=wx.ALIGN_LEFT)
		self.gbtext = wx.StaticText(self.mp, -1, "Green-B", size=(75,-1), style=wx.ALIGN_LEFT)
		self.grtext = wx.StaticText(self.mp, -1, "Green-R", size=(75,-1), style=wx.ALIGN_LEFT)
		self.rtext = wx.StaticText(self.mp, -1, "Red", size=(75,-1), style=wx.ALIGN_LEFT)

		self.blanktext4 = wx.StaticText(self.mp, -1, "", size=(50,-1), style=wx.ALIGN_LEFT)
		self.slopetext = wx.StaticText(self.mp, -1, "Slope", size=(55,-1), style=wx.ALIGN_LEFT)
		self.slopedispB = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.slopedispGb = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.slopedispGr = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.slopedispR = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		
		self.blanktext5 = wx.StaticText(self.mp, -1, "", size=(50,-1), style=wx.ALIGN_LEFT)
		self.datatext = wx.StaticText(self.mp, -1, "PRNU %", size=(55,-1), style=wx.ALIGN_LEFT)
		self.datadispB = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.datadispGb = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.datadispGr = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)
		self.datadispR = wx.TextCtrl(self.mp, value="", size=(75,-1), style=wx.TE_READONLY)

		self.dataListCtrl = wx.ListCtrl(self.mp, -1, size=(405, 740), style=wx.LC_REPORT)
		self.dataListCtrl.InsertColumn(0, 'X')
		self.dataListCtrl.InsertColumn(1, 'B')
		self.dataListCtrl.InsertColumn(2, 'Gb')
		self.dataListCtrl.InsertColumn(3, 'Gr')
		self.dataListCtrl.InsertColumn(4, 'R')
		
		# define sizers
		self.DefineSizers()

	def SelectFile(self, event):
		if self.fileDisplay.GetCurrentSelection() == 1: # Open
			# file selection
			wildcard = 	"TEXT files (*.txt)|*.txt" 
			fileDialog = wx.FileDialog(None, "Select a Text file", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
			
			# user canceled file opening
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				self.fileDisplay.SetSelection(0)
				return

			# otherwise, proceed loading the file chosen by the user
			# get new filepath
			self.filePath = fileDialog.GetPath()
			# update list
			self.fileList[0] = self.filePath
			self.fileDisplay.SetItems(self.fileList)
			self.fileDisplay.SetSelection(0)

			# read and parse text file
			self.NoiseData = self.ReadText(self.filePath)

			# plot data
			self.Graph(event)

			# populate listctrl
			self.Populate(self.figurebook.GetSelection())

			self.statusBar.SetStatusText('Complete')
		elif self.fileDisplay.GetCurrentSelection() == 0: # original file
			# do nothing
			return

	def ReadText(self, path):
		# read text and return all data as an object
		f = open(path, 'rU')
		csv_reader = csv.reader(f)

		line1 = csv_reader.next()[0].split('\t')
		# get image ROI
		x = (float(line1[2]), float(line1[3]))
		y = (float(line1[5]), float(line1[6]))

		# extract header line
		line2 = csv_reader.next()[0].split('\t')
		loopItem = line2[0]
		loopVals = np.array([])

		meanVals = np.array([[0, 0, 0, 0, 0]])
		TTNVals = np.array([[0, 0, 0, 0, 0]])
		PTNVals = np.array([[0, 0, 0, 0, 0]])
		TFPNVals = np.array([[0, 0, 0, 0, 0]])
		pFPNVals = np.array([[0, 0, 0, 0, 0]])

		for line in csv_reader:
			linesplit = line[0].split('\t')
			try:
				loopVals = np.append(loopVals, int(linesplit[0]))
				meanVals = np.append(meanVals, [np.array(linesplit[1:6]).astype(np.float)], axis=0)
				TTNVals = np.append(TTNVals, [np.array(linesplit[6:11]).astype(np.float)], axis=0)
				PTNVals = np.append(PTNVals, [np.array(linesplit[11:16]).astype(np.float)], axis=0)
				TFPNVals = np.append(TFPNVals, [np.array(linesplit[16:21]).astype(np.float)], axis=0)
				pFPNVals = np.append(pFPNVals, [np.array(linesplit[21:26]).astype(np.float)], axis=0)
			except ValueError:
				break

		return NoiseData(x, y, loopItem, loopVals, meanVals, TTNVals, PTNVals, TFPNVals, pFPNVals)
		
	def GetBits(self):
		return self.bitDict[self.bitchoice.GetCurrentSelection()]

	def GetSFGain(self):
		try:
			sfgain = float(self.sfdisp.GetValue())
			if sfgain <= 0:
				self.statusBar.SetStatusText("Error: please enter positive value for ADC Range")
				self.ClearDisplays()
				return
			return sfgain
		except ValueError:
			self.statusBar.SetStatusText("Error: please enter numerical value for SF Gain")
			self.ClearDisplays()
			return

	def GetADC(self):
		try:
			adc = int(self.adcdisp.GetValue())
			if adc <= 0:
				self.statusBar.SetStatusText("Error: please enter positive value for ADC Range")
				self.ClearDisplays()
				return
			return adc
		except ValueError:
			self.statusBar.SetStatusText("Error: please enter integer value for ADC Range")
			self.ClearDisplays()
			return

	def GetOffset(self):
		try:
			offset = float(self.offdisp.GetValue())
			return offset
		except ValueError:
			self.statusBar.SetStatusText("Error: please enter numerical value for offset")
			self.ClearDisplays()
			return


	def Calculate(self, event):
		panelNum = self.figurebook.GetSelection()
		panel = self.figurebook.panelDict[panelNum]
		leftlim = panel.leftxline._path.vertices[0,0]
		rightlim = panel.rightxline._path.vertices[0,0]
		self.figurebook.frame.leftxdisp.SetValue(str(float_round(leftlim, 6)))
		self.figurebook.frame.rightxdisp.SetValue(str(float_round(rightlim, 6)))
		self.figurebook.frame.datatext.SetLabel(self.figurebook.dataDict[panelNum])
		panel.CalculateSlope()

	def Graph(self, event):
		try:
			# plot data
			self.PlotPRNU(self.NoiseData)
			self.PlotTTN(self.NoiseData)
			self.PlotTTV(self.NoiseData)
			self.PlotSNR(self.NoiseData)
			self.ClearDisplays()
		except AttributeError:
			self.ClearPanels()
			self.statusBar.SetStatusText("Error: please load a file first")
			return	

	def Populate(self, panelNum):
		try:
			meanVals = self.NoiseData.meanVals
			TFPNVals = self.NoiseData.TFPNVals
			TTNVals = self.NoiseData.TTNVals
			offset = self.GetOffset()
		except AttributeError:
			return
		
		def GetPRNUData(self):
			self.xdata = np.log10(meanVals[:, 4]-offset)
			self.bdata = np.log10(TFPNVals[:, 0])
			self.gbdata = np.log10(TFPNVals[:, 1])
			self.grdata = np.log10(TFPNVals[:, 2])
			self.rdata = np.log10(TFPNVals[:, 3])
		def GetTTNData(self):
			self.xdata = np.log10(meanVals[:, 4]-offset)
			self.bdata = np.log10(TTNVals[:, 0])
			self.gbdata = np.log10(TTNVals[:, 1])
			self.grdata = np.log10(TTNVals[:, 2])
			self.rdata = np.log10(TTNVals[:, 3])
		def GetTTVData(self):
			self.xdata = meanVals[:, 4]-offset
			self.bdata = TTNVals[:, 0]**2
			self.gbdata = TTNVals[:, 1]**2
			self.grdata = TTNVals[:, 2]**2
			self.rdata = TTNVals[:, 3]**2
		def GetSNRData(self):
			self.xdata = meanVals[:, 4]
			self.bdata = 20*np.log10(meanVals[:, 0]/TTNVals[:, 0])
			self.gbdata = 20*np.log10(meanVals[:, 1]/TTNVals[:, 1])
			self.grdata = 20*np.log10(meanVals[:, 2]/TTNVals[:, 2])
			self.rdata = 20*np.log10(meanVals[:, 3]/TTNVals[:, 3])

		dataDict = {0: GetPRNUData, 1: GetTTNData, 2: GetTTVData, 3:GetSNRData}
		dataDict[panelNum](self)

		# clear all
		self.dataListCtrl.DeleteAllItems()
		decimals = 6
		for i in range(0,len(self.xdata)):
			self.dataListCtrl.InsertStringItem(i, str(float_round(self.xdata[i], decimals)))
			self.dataListCtrl.SetStringItem(i, 1, str(float_round(self.bdata[i], decimals)))
			self.dataListCtrl.SetStringItem(i, 2, str(float_round(self.gbdata[i], decimals)))
			self.dataListCtrl.SetStringItem(i, 3, str(float_round(self.grdata[i], decimals)))
			self.dataListCtrl.SetStringItem(i, 4, str(float_round(self.rdata[i], decimals)))
		#self.dataListCtrl.resizeLastColumn(-1)
		self.dataListCtrl.SetColumnWidth(4,-1)

	def Highlight(self, xdata):
		try:
			for i in range(0, len(self.xdata)):
				self.dataListCtrl.Select(i, 0)
		except AttributeError: # data hasn't been loaded yet
			return
		try:
			self.index = np.amin(np.where(self.xdata > xdata))
			self.dataListCtrl.Select(self.index)
			self.dataListCtrl.EnsureVisible(self.index)
		except ValueError: # if index cannot be found (inf)
			return
		except AttributeError: # if data hasn't been loaded yet
			return

	def ClearPanels(self):
		self.figurebook.PRNUPanel.axes.cla()
		self.figurebook.TTNPanel.axes.cla()
		self.figurebook.TTVPanel.axes.cla()
		self.figurebook.SNRPanel.axes.cla()


	def PlotPRNU(self, NoiseData):
		loopItem = NoiseData.loopItem
		loopVals = NoiseData.loopVals
		meanVals = NoiseData.meanVals
		TFPNVals = NoiseData.TFPNVals

		offset = self.GetOffset()

		panel = self.figurebook.PRNUPanel
		
		panel.axes.cla()
		panel.axes.grid()
		# set title and axes labels
		panel.axes.set_title('log(TFPN) vs log(Signal Average)')
		panel.axes.set_xlabel('log(Signal Average - Offset) [DN]')
		panel.axes.set_ylabel('log(TFPN) [DN]')
		# plot
		try:
			panel.B = panel.axes.plot(np.log10(meanVals[:, 0]-offset), np.log10(TFPNVals[:, 0]), color='b')
			panel.Gb = panel.axes.plot(np.log10(meanVals[:, 1]-offset), np.log10(TFPNVals[:, 1]), color='g')
			panel.Gr = panel.axes.plot(np.log10(meanVals[:, 2]-offset), np.log10(TFPNVals[:, 2]), color='c')
			panel.R = panel.axes.plot(np.log10(meanVals[:, 3]-offset), np.log10(TFPNVals[:, 3]), color='r')
			self.statusBar.SetStatusText("")
		except TypeError:
			self.ClearPanels()
			self.statusBar.SetStatusText("Error: please enter numerical value for offset")
			return
		# reset vertical line
		panel.leftxline, = panel.axes.plot([0], [0])
		panel.rightxline, = panel.axes.plot([0], [0])
		panel.leftyline, = panel.axes.plot([0], [0])
		panel.rightyline, = panel.axes.plot([0], [0])
		# clear displays
		self.leftxdisp.SetValue("0.0")
		self.rightxdisp.SetValue("0.0")
		self.leftydisp.SetValue("0.0")
		self.rightydisp.SetValue("0.0")

		panel.canvas.draw()

	def PlotTTN(self, NoiseData):
		loopItem = NoiseData.loopItem
		loopVals = NoiseData.loopVals
		meanVals = NoiseData.meanVals
		TTNVals = NoiseData.TTNVals

		offset = self.GetOffset()

		panel = self.figurebook.TTNPanel
		
		panel.axes.cla()
		panel.axes.grid()
		# set title and axes labels
		panel.axes.set_title('log(TTN) vs log(Signal Average)')
		panel.axes.set_xlabel('log(Signal Average - Offset) [DN]')
		panel.axes.set_ylabel('log(TTN) [DN]')
		# plot
		try:
			panel.B = panel.axes.plot(np.log10(meanVals[:, 0]-offset), np.log10(TTNVals[:, 0]), color='b')
			panel.Gb = panel.axes.plot(np.log10(meanVals[:, 1]-offset), np.log10(TTNVals[:, 1]), color='g')
			panel.Gr = panel.axes.plot(np.log10(meanVals[:, 2]-offset), np.log10(TTNVals[:, 2]), color='c')
			panel.R = panel.axes.plot(np.log10(meanVals[:, 3]-offset), np.log10(TTNVals[:, 3]), color='r')
			self.statusBar.SetStatusText("")
		except TypeError:
			self.ClearPanels()
			self.statusBar.SetStatusText("Error: please enter numerical value for offset")
			return
		# reset vertical line
		panel.leftxline, = panel.axes.plot([0], [0])
		panel.rightxline, = panel.axes.plot([0], [0])
		panel.leftyline, = panel.axes.plot([0], [0])
		panel.rightyline, = panel.axes.plot([0], [0])
		# clear displays
		self.leftxdisp.SetValue("0.0")
		self.rightxdisp.SetValue("0.0")
		self.leftydisp.SetValue("0.0")
		self.rightydisp.SetValue("0.0")

		panel.canvas.draw()

	def PlotTTV(self, NoiseData):
		loopItem = NoiseData.loopItem
		loopVals = NoiseData.loopVals
		meanVals = NoiseData.meanVals
		TTNVals = NoiseData.TTNVals

		offset = self.GetOffset()

		panel = self.figurebook.TTVPanel
		
		panel.axes.cla()
		panel.axes.grid()
		# set title and axes labels
		panel.axes.set_title('TTN^2 vs log(Signal Average)')
		panel.axes.set_xlabel('Signal Average - Offset [DN]')
		panel.axes.set_ylabel('TTN^2 [DN^2]')
		# plot
		try:
			panel.B = panel.axes.plot(meanVals[:, 0]-offset, TTNVals[:, 0]**2, color='b')
			panel.Gb = panel.axes.plot(meanVals[:, 1]-offset, TTNVals[:, 1]**2, color='g')
			panel.Gr = panel.axes.plot(meanVals[:, 2]-offset, TTNVals[:, 2]**2, color='c')
			panel.R = panel.axes.plot(meanVals[:, 3]-offset, TTNVals[:, 3]**2, color='r')
		except TypeError:
			self.ClearPanels()
			self.statusBar.SetStatusText("Error: please enter numerical value for offset")
			return
		# reset vertical line
		panel.leftxline, = panel.axes.plot([0], [0])
		panel.rightxline, = panel.axes.plot([0], [0])
		panel.leftyline, = panel.axes.plot([0], [0])
		panel.rightyline, = panel.axes.plot([0], [0])
		# clear displays
		self.leftxdisp.SetValue("0.0")
		self.rightxdisp.SetValue("0.0")
		self.leftydisp.SetValue("0.0")
		self.rightydisp.SetValue("0.0")

		panel.canvas.draw()

	def PlotSNR(self, NoiseData):
		loopItem = NoiseData.loopItem
		loopVals = NoiseData.loopVals
		meanVals = NoiseData.meanVals
		TTNVals = NoiseData.TTNVals

		panel = self.figurebook.SNRPanel
		
		panel.axes.cla()
		panel.axes.grid()
		# set title and axes labels
		panel.axes.set_title('SNR vs Signal Average')
		panel.axes.set_xlabel('Signal Average [DN]')
		panel.axes.set_ylabel('SNR [dB]')
		# plot
		panel.B = panel.axes.plot(meanVals[:, 0], 20*np.log10(meanVals[:, 0]/TTNVals[:, 0]), color='b')
		panel.Gb = panel.axes.plot(meanVals[:, 1], 20*np.log10(meanVals[:, 1]/TTNVals[:, 1]), color='g')
		panel.Gr = panel.axes.plot(meanVals[:, 2], 20*np.log10(meanVals[:, 2]/TTNVals[:, 2]), color='c')
		panel.R = panel.axes.plot(meanVals[:, 3], 20*np.log10(meanVals[:, 3]/TTNVals[:, 3]), color='r')
		# reset vertical line
		panel.leftxline, = panel.axes.plot([0], [0])
		panel.rightxline, = panel.axes.plot([0], [0])
		panel.leftyline, = panel.axes.plot([0], [0])
		panel.rightyline, = panel.axes.plot([0], [0])
		# clear displays
		self.leftxdisp.SetValue("0.0")
		self.rightxdisp.SetValue("0.0")
		self.leftydisp.SetValue("0.0")
		self.rightydisp.SetValue("0.0")

		panel.canvas.draw()


	def ClearDisplays(self):
		self.slopedispB.SetValue("")
		self.slopedispGb.SetValue("")
		self.slopedispGr.SetValue("")
		self.slopedispR.SetValue("")
		self.datadispB.SetValue("")
		self.datadispGb.SetValue("")
		self.datadispGr.SetValue("")
		self.datadispR.SetValue("")	
	
	def DefineSizers(self):
		self.inputsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.inputsizer.Add(self.bitchoice, 0, wx.ALL, 5)
		self.inputsizer.Add(self.sftext, 0, wx.ALL, 5)
		self.inputsizer.Add(self.sfdisp, 0, wx.ALL, 5)
		self.inputsizer.Add(self.adctext, 0, wx.ALL, 5)
		self.inputsizer.Add(self.adcdisp, 0, wx.ALL, 5)
		self.inputsizer.Add(self.offtext, 0, wx.ALL, 5)
		self.inputsizer.Add(self.offdisp, 0, wx.ALL, 5)

		self.dispsizer = wx.FlexGridSizer(3, 9, 5, 5)
		# row 1
		self.dispsizer.Add(self.blanktext)
		self.dispsizer.Add(self.lefttext)
		self.dispsizer.Add(self.righttext)

		self.dispsizer.Add(self.blanktext2)
		self.dispsizer.Add(self.blanktext3)
		self.dispsizer.Add(self.btext)
		self.dispsizer.Add(self.gbtext)
		self.dispsizer.Add(self.grtext)
		self.dispsizer.Add(self.rtext)

		# row 2
		self.dispsizer.Add(self.xtext)
		self.dispsizer.Add(self.leftxdisp)
		self.dispsizer.Add(self.rightxdisp)

		self.dispsizer.Add(self.blanktext4)
		self.dispsizer.Add(self.slopetext)
		self.dispsizer.Add(self.slopedispB)
		self.dispsizer.Add(self.slopedispGb)
		self.dispsizer.Add(self.slopedispGr)
		self.dispsizer.Add(self.slopedispR)

		# row 3
		self.dispsizer.Add(self.ytext)
		self.dispsizer.Add(self.leftydisp)
		self.dispsizer.Add(self.rightydisp)

		self.dispsizer.Add(self.blanktext5)
		self.dispsizer.Add(self.datatext)
		self.dispsizer.Add(self.datadispB)
		self.dispsizer.Add(self.datadispGb)
		self.dispsizer.Add(self.datadispGr)
		self.dispsizer.Add(self.datadispR)

		self.leftsizer = wx.BoxSizer(wx.VERTICAL)
		self.leftsizer.Add(self.fileDisplay, 0, wx.ALL | wx.GROW, 10)
		self.leftsizer.Add(self.inputsizer, 0, wx.ALL | wx.EXPAND, 5)
		self.leftsizer.Add(self.figurebook, 0, wx.ALL | wx.EXPAND, 5)
		self.leftsizer.Add(self.dispsizer, 0, wx.ALL | wx.EXPAND, 5)

		self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.topsizer.Add(self.leftsizer, 0, wx.ALL | wx.GROW, 5)
		self.topsizer.Add(self.dataListCtrl, 0, wx.ALL | wx.GROW, 5)

		self.mp.SetAutoLayout(True)
		self.mp.SetSizer(self.topsizer)
		self.mp.Layout()	

class FigureBook(wx.Notebook):
	panelDict = {}
	dataDict = {}
	a = 1
	def __init__(self, parent, frame):
		wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style = wx.BK_DEFAULT)

		self.frame = frame
		# create PRNU Tab Panel
		self.PRNUPanel = PRNUPanel(self, frame)
		self.AddPage(self.PRNUPanel, "PRNU")
		self.panelDict[0] = self.PRNUPanel
		self.dataDict[0] = "PRNU %"

		# create TTN Tab Panel
		self.TTNPanel = TTNPanel(self, frame)
		self.AddPage(self.TTNPanel, "TTN")
		self.panelDict[1] = self.TTNPanel
		self.dataDict[1] = "CG (uV)"

		# create TTV Tab Panel
		self.TTVPanel = TTVPanel(self, frame)
		self.AddPage(self.TTVPanel, "TTV")
		self.panelDict[2] = self.TTVPanel
		self.dataDict[2] = "CG (uV)"

		# create SNR Tab Panel
		self.SNRPanel = SNRPanel(self, frame)
		self.AddPage(self.SNRPanel, "SNR")
		self.panelDict[3] = self.SNRPanel
		self.dataDict[3] = "Y-int"

		# on page changing
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
		
	def OnPageChanged(self, event):
		#self.frame.ClearDisplays()
		panelNum = event.GetSelection()
		panel = self.panelDict[panelNum]

		leftxlim = panel.leftxline._path.vertices[0,0]
		rightxlim = panel.rightxline._path.vertices[0,0]
		leftylim = panel.leftyline._path.vertices[0,1]
		rightylim = panel.rightyline._path.vertices[0,1]
		self.frame.leftxdisp.SetValue(str(float_round(leftxlim, 6)))
		self.frame.rightxdisp.SetValue(str(float_round(rightxlim, 6)))
		self.frame.leftydisp.SetValue(str(float_round(leftylim, 6)))
		self.frame.rightydisp.SetValue(str(float_round(rightylim, 6)))

		self.frame.datatext.SetLabel(self.dataDict[panelNum])
		panel.CalculateSlope()
		self.frame.Populate(panelNum)
		event.Skip()



# below is needed for all GUIs
if __name__== '__main__':
	app = wx.App(False) # application object (inner workings) 
	frame = NoiseGrapher(parent = None) # frame object (what user sees)
	frame.Show() # show frame
	app.MainLoop() # run main loop	
