from math import ceil, floor

import wx
import wx.lib.mixins.listctrl as listmix
import csv
import numpy as np
from matplotlib.figure import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from PIL import Image as im

class NoiseData(object):
	def __init__(self, x, y, loopItem, loopVals, meanVals, TTNVals, PTNVals, TFPNVals, pFPNVals):
		self.x = x
		self.y = y
		self.loopItem = loopItem
		# skip the first line
		self.loopVals = loopVals[1:loopVals.shape[0]]
		self.meanVals = meanVals[1:meanVals.shape[0]]
		self.TTNVals = TTNVals[1:TTNVals.shape[0]]
		self.PTNVals = PTNVals[1:PTNVals.shape[0]]
		self.TFPNVals = TFPNVals[1:TFPNVals.shape[0]]
		self.pFPNVals = pFPNVals[1:pFPNVals.shape[0]]

def float_round(num, places = 0, direction = floor):
	try:
		toRet = direction(num * (10**places)) / float(10**places)
		return toRet
	except TypeError:
		return 0.0


class NoisePanel(wx.Panel):
	flag = None
	decimals = 4
	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, id=wx.ID_ANY)

		self.frame = frame
		# create a panel
		self.panel = wx.Panel(self, wx.ID_ANY)
		
		self.figure = plt.figure(facecolor="white")
		
		self.canvas = FigureCanvas(self.panel, -1, self.figure)

		self.axes = self.figure.add_subplot(111)
		self.axes.grid()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas, 0, wx.ALL, 5)
		
		# draw vertical lines
		self.leftxline, = self.axes.plot([0], [0], color='b')
		self.rightxline, = self.axes.plot([0], [0], color='r')
		self.leftyline, = self.axes.plot([0], [0], color='b')
		self.rightyline, = self.axes.plot([0], [0], color='r')
		
		self.click = self.canvas.mpl_connect('button_press_event', self.OnClick)
		self.move = self.canvas.mpl_connect('motion_notify_event', self.OnMove)
		self.release = self.canvas.mpl_connect('button_release_event', self.OnRelease)

		self.panel.SetAutoLayout(True)
		self.panel.SetSizer(self.sizer)
		self.panel.Layout()
		self.sizer.Fit(self.panel)

	def OnClick(self, event):
		xdata = event.xdata
		ydata = event.ydata
		xbound = self.axes.get_xbound()
		ybound = self.axes.get_ybound()
		if event.button == 1: # left click
			self.leftxline.remove()
			self.leftyline.remove()
			self.leftxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='b')
			self.leftyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='b')
			self.canvas.draw()
			self.frame.leftxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.leftydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		elif event.button == 3: # right click
			self.rightxline.remove()
			self.rightyline.remove()
			self.rightxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='r')
			self.rightyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='r')
			self.canvas.draw()
			self.frame.rightxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.rightydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		self.flag = 1
		self.frame.Highlight(xdata)

	def OnMove(self, event):
		if self.flag is None: return
		if event.xdata is None: return
		xdata = event.xdata
		ydata = event.ydata
		xbound = self.axes.get_xbound()
		ybound = self.axes.get_ybound()
		if event.button == 1: # left click
			self.leftxline.remove()
			self.leftyline.remove()
			self.leftxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='b')
			self.leftyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='b')
			self.canvas.draw()
			self.frame.leftxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.leftydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		if event.button == 3: # right click
			self.rightxline.remove()
			self.rightyline.remove()
			self.rightxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='r')
			self.rightyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='r')
			self.canvas.draw()
			self.frame.rightxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.rightydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		self.frame.Highlight(xdata)

	def OnRelease(self, event):
		xdata = event.xdata
		ydata = event.ydata
		xbound = self.axes.get_xbound()
		ybound = self.axes.get_ybound()
		if event.button == 1: # left click
			self.leftxline.remove()
			self.leftyline.remove()
			self.leftxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='b')
			self.leftyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='b')
			self.canvas.draw()
			self.frame.leftxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.leftydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		elif event.button == 3: # right click
			self.rightxline.remove()
			self.rightyline.remove()
			self.rightxline, = self.axes.plot([xdata, xdata], [ybound[0], ybound[1]], color='r')
			self.rightyline, = self.axes.plot([xbound[0], xbound[1]], [ydata, ydata], color='r')
			self.canvas.draw()
			self.frame.rightxdisp.SetValue(str(float_round(event.xdata, self.decimals)))
			self.frame.rightydisp.SetValue(str(float_round(event.ydata, self.decimals)))
		self.flag = None
		self.frame.Highlight(xdata)
		self.CalculateSlope()

	
class PRNUPanel(NoisePanel):

	def CalculateSlope(self):
		try:
			Bdata = np.asarray(self.B[0]._path.vertices)
			Gbdata = np.asarray(self.Gb[0]._path.vertices)
			Grdata = np.asarray(self.Gr[0]._path.vertices)
			Rdata = np.asarray(self.R[0]._path.vertices)

			try:
				leftlim = float(str(self.frame.leftxdisp.GetValue()))
				rightlim = float(str(self.frame.rightxdisp.GetValue()))
			except ValueError:
				return

			xBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 0]
			yBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 1]
			xGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 0]
			yGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 1]
			xGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 0]
			yGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 1]
			xRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 0]
			yRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 1]

			try:
				Bslope, Bint = np.polyfit(xBdata, yBdata, 1)
				Gbslope, Gbint = np.polyfit(xGbdata, yGbdata, 1)
				Grslope, Grint = np.polyfit(xGrdata, yGrdata, 1)
				Rslope, Rint = np.polyfit(xRdata, yRdata, 1)
				self.frame.statusBar.SetStatusText("")
			except TypeError:
				self.frame.statusBar.SetStatusText("Error: Left limit must be smaller than right limit")
				self.frame.ClearDisplays()
				return

			try:
				offset = self.frame.GetOffset()
			except TypeError:
				return

			self.frame.slopedispB.SetValue(str(float_round(Bslope, self.decimals)))
			self.frame.slopedispGb.SetValue(str(float_round(Gbslope, self.decimals)))
			self.frame.slopedispGr.SetValue(str(float_round(Grslope, self.decimals)))
			self.frame.slopedispR.SetValue(str(float_round(Rslope, self.decimals)))
			self.frame.datadispB.SetValue(str(float_round(10**(Bint/Bslope)*100, self.decimals)))
			self.frame.datadispGb.SetValue(str(float_round(10**(Gbint/Gbslope)*100, self.decimals)))
			self.frame.datadispGr.SetValue(str(float_round(10**(Grint/Grslope)*100, self.decimals)))
			self.frame.datadispR.SetValue(str(float_round(10**(Rint/Rslope)*100, self.decimals)))				
		except AttributeError:
			return

class TTNPanel(NoisePanel):
	
	def CalculateSlope(self):
		try:
			Bdata = np.asarray(self.B[0]._path.vertices)
			Gbdata = np.asarray(self.Gb[0]._path.vertices)
			Grdata = np.asarray(self.Gr[0]._path.vertices)
			Rdata = np.asarray(self.R[0]._path.vertices)

			try:
				leftlim = float(str(self.frame.leftxdisp.GetValue()))
				rightlim = float(str(self.frame.rightxdisp.GetValue()))
			except ValueError:
				return

			xBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 0]
			yBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 1]
			xGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 0]
			yGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 1]
			xGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 0]
			yGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 1]
			xRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 0]
			yRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 1]

			try:
				Bslope, Bint = np.polyfit(xBdata, yBdata, 1)
				Gbslope, Gbint = np.polyfit(xGbdata, yGbdata, 1)
				Grslope, Grint = np.polyfit(xGrdata, yGrdata, 1)
				Rslope, Rint = np.polyfit(xRdata, yRdata, 1)
				self.frame.statusBar.SetStatusText("")
			except TypeError:
				self.frame.statusBar.SetStatusText("Error: Left limit must be smaller than right limit")
				self.frame.ClearDisplays()
				return

			try:
				bits = self.frame.GetBits()
				sfgain = self.frame.GetSFGain()
				adc = self.frame.GetADC()
				factor = adc*1000/(2**bits)/sfgain
			except TypeError:
				return

			self.frame.slopedispB.SetValue(str(float_round(Bslope, self.decimals)))
			self.frame.slopedispGb.SetValue(str(float_round(Gbslope, self.decimals)))
			self.frame.slopedispGr.SetValue(str(float_round(Grslope, self.decimals)))
			self.frame.slopedispR.SetValue(str(float_round(Rslope, self.decimals)))
			self.frame.datadispB.SetValue(str(float_round(10**(Bint/Bslope)*factor, self.decimals)))
			self.frame.datadispGb.SetValue(str(float_round(10**(Gbint/Gbslope)*factor, self.decimals)))
			self.frame.datadispGr.SetValue(str(float_round(10**(Grint/Grslope)*factor, self.decimals)))
			self.frame.datadispR.SetValue(str(float_round(10**(Rint/Rslope)*factor, self.decimals)))				
		except AttributeError:
			return

class TTVPanel(NoisePanel):

	def CalculateSlope(self):
		try:
			Bdata = np.asarray(self.B[0]._path.vertices)
			Gbdata = np.asarray(self.Gb[0]._path.vertices)
			Grdata = np.asarray(self.Gr[0]._path.vertices)
			Rdata = np.asarray(self.R[0]._path.vertices)

			try:
				leftlim = float(str(self.frame.leftxdisp.GetValue()))
				rightlim = float(str(self.frame.rightxdisp.GetValue()))
			except ValueError:
				return

			xBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 0]
			yBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 1]
			xGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 0]
			yGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 1]
			xGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 0]
			yGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 1]
			xRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 0]
			yRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 1]

			try:
				Bslope, Bint = np.polyfit(xBdata, yBdata, 1)
				Gbslope, Gbint = np.polyfit(xGbdata, yGbdata, 1)
				Grslope, Grint = np.polyfit(xGrdata, yGrdata, 1)
				Rslope, Rint = np.polyfit(xRdata, yRdata, 1)
				self.frame.statusBar.SetStatusText("")
			except TypeError:
				self.frame.statusBar.SetStatusText("Error: Left limit must be smaller than right limit")
				self.frame.ClearDisplays()
				return

			try:
				bits = self.frame.GetBits()
				sfgain = self.frame.GetSFGain()
				adc = self.frame.GetADC()
				factor = adc*1000/(2**bits)/sfgain
			except TypeError:
				return

			
				
			self.frame.slopedispB.SetValue(str(float_round(Bslope, self.decimals)))
			self.frame.slopedispGb.SetValue(str(float_round(Gbslope, self.decimals)))
			self.frame.slopedispGr.SetValue(str(float_round(Grslope, self.decimals)))
			self.frame.slopedispR.SetValue(str(float_round(Rslope, self.decimals)))
			self.frame.datadispB.SetValue(str(float_round(Bslope*factor, self.decimals)))
			self.frame.datadispGb.SetValue(str(float_round(Gbslope*factor, self.decimals)))
			self.frame.datadispGr.SetValue(str(float_round(Grslope*factor, self.decimals)))
			self.frame.datadispR.SetValue(str(float_round(Rslope*factor, self.decimals)))				
		except AttributeError:
			return

class SNRPanel(NoisePanel):
	
	def CalculateSlope(self):
		try:
			Bdata = np.asarray(self.B[0]._path.vertices)
			Gbdata = np.asarray(self.Gb[0]._path.vertices)
			Grdata = np.asarray(self.Gr[0]._path.vertices)
			Rdata = np.asarray(self.R[0]._path.vertices)

			try:
				leftlim = float(str(self.frame.leftxdisp.GetValue()))
				rightlim = float(str(self.frame.rightxdisp.GetValue()))
			except ValueError:
				return

			xBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 0]
			yBdata = Bdata[(Bdata[:,0] > leftlim) & (Bdata[:,0] < rightlim), 1]
			xGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 0]
			yGbdata = Gbdata[(Gbdata[:,0] > leftlim) & (Gbdata[:,0] < rightlim), 1]
			xGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 0]
			yGrdata = Grdata[(Grdata[:,0] > leftlim) & (Grdata[:,0] < rightlim), 1]
			xRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 0]
			yRdata = Rdata[(Rdata[:,0] > leftlim) & (Rdata[:,0] < rightlim), 1]

			try:
				Bslope, Bint = np.polyfit(xBdata, yBdata, 1)
				Gbslope, Gbint = np.polyfit(xGbdata, yGbdata, 1)
				Grslope, Grint = np.polyfit(xGrdata, yGrdata, 1)
				Rslope, Rint = np.polyfit(xRdata, yRdata, 1)
				self.frame.statusBar.SetStatusText("")
			except TypeError:
				self.frame.statusBar.SetStatusText("Error: Left limit must be smaller than right limit")
				self.frame.ClearDisplays()
				return

			self.frame.slopedispB.SetValue(str(float_round(Bslope, self.decimals)))
			self.frame.slopedispGb.SetValue(str(float_round(Gbslope, self.decimals)))
			self.frame.slopedispGr.SetValue(str(float_round(Grslope, self.decimals)))
			self.frame.slopedispR.SetValue(str(float_round(Rslope, self.decimals)))
			self.frame.datadispB.SetValue(str(float_round(Bint, self.decimals)))
			self.frame.datadispGb.SetValue(str(float_round(Gbint, self.decimals)))
			self.frame.datadispGr.SetValue(str(float_round(Grint, self.decimals)))
			self.frame.datadispR.SetValue(str(float_round(Rint, self.decimals)))				
		except AttributeError:
			return

class CustomListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

