#!/usr/local/bin/python

import wx
from PIL import Image
#import ImageStat
import numpy
import os

# Global variables

class imageCalc(wx.Frame):
	def __init__(self, parent):
		# build a frame
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Image Calculator", size = (700, 170), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

		# build a panel
		mainPanel = wx.Panel(self, wx.ID_ANY)
		
		# build a status bar =================================================================
		statusBar = self.CreateStatusBar()

		# build a menu bar ===================================================================
		menuBar = wx.MenuBar()
		self.SetMenuBar(menuBar)

		# build text controls for file display ===============================================
		self.fileDisplay1 = wx.TextCtrl(mainPanel, value = "File 1", pos=(10,10), size=(580,-1))
		self.fileDisplay2 = wx.TextCtrl(mainPanel, value = "File 2", pos=(10,40), size=(580,-1))
		
		
		# build buttons for selecting files ==================================================
		openButton1 = wx.Button(mainPanel, id=wx.ID_ANY, label = "Open...", pos=(597, 7), size=(90,-1))
		openButton1.Bind(wx.EVT_BUTTON, self.FileSelect1)
		openButton2 = wx.Button(mainPanel, id=wx.ID_ANY, label = "Open...", pos=(597, 37), size=(90,-1))
		openButton2.Bind(wx.EVT_BUTTON, self.FileSelect2)
		
		addButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Add (1+2)", pos=(7, 67), size=(120,-1))
		addButton.Bind(wx.EVT_BUTTON, self.Add)
		subButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Subtract (2-1)", pos=(137, 67), size=(120,-1))
		subButton.Bind(wx.EVT_BUTTON, self.Subtract)
		avgButton = wx.Button(mainPanel, id=wx.ID_ANY, label = "Average (1+2)/2", pos=(267, 67), size=(120,-1))
		avgButton.Bind(wx.EVT_BUTTON, self.Average)

		# build a text control for offset ====================================================
		self.offsetCtrl = wx.TextCtrl(mainPanel, value="0", pos=(397, 70), size=(90,-1))
		
		# build a text control for status display ============================================
		self.statusText = wx.TextCtrl(mainPanel, value = "", pos=(10, 100), size=(680,-1), style=wx.TE_READONLY)

		# build static text ==================================================================
		wx.StaticText(mainPanel, -1, "Offset", (500, 73), (45,-1), wx.ALIGN_RIGHT)
		
		# making sure some variables are predefined as nullpointers
		self.fileNames1 = None
		self.fileNames2 = None
                self.blocker = True

	# define callbacks
	# ========================================================================================
	
	# function for file selection 1
	def FileSelect1(self, event):
		dirDialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE);

		# user canceled file opening
		if dirDialog.ShowModal() == wx.ID_CANCEL:
			return
			   
		# otherwise, proceed loading the file chosen by the user
		self.rootDir1 = dirDialog.GetPath()
		self.subdirArray1 = [];
                for dirName, subdirList, fileList in os.walk(self.rootDir1):
                    for fname in fileList:
                        if os.path.splitext(fname)[1] == '.bmp':
                            self.subdirArray1.append(dirName+'\\'+fname)
		
		self.fileDisplay1.Clear()
		self.blocker = False
		self.statusText.SetForegroundColour(wx.BLACK)
		self.fileDisplay1.AppendText(self.rootDir1)

	# function for file selection 2
	def FileSelect2(self, event):
		dirDialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE);

		# user canceled file opening
		if dirDialog.ShowModal() == wx.ID_CANCEL:
			return
			   
		# otherwise, proceed loading the file chosen by the user
		self.rootDir2 = dirDialog.GetPath()
		self.subdirArray2 = [];
                for dirName, subdirList, fileList in os.walk(self.rootDir2):
                    for fname in fileList:
                        if os.path.splitext(fname)[1] == '.bmp':
                            self.subdirArray2.append(dirName+'\\'+fname)
                            
		self.fileDisplay2.Clear()
		self.statusText.SetForegroundColour(wx.BLACK)
		self.blocker = False
		self.fileDisplay2.AppendText(self.rootDir2)
	# function for making sure the directory matches
	def CheckIfFilesMatch(self):
	    if(self.subdirArray1.__len__() != self.subdirArray2.__len__()):
	        self.statusText.SetValue("please enter same amount of files")
                self.blocker = True
                self.statusText.SetForegroundColour(wx.RED)
	        return False 
	    for f in self.subdirArray1:
	        if f.replace(self.rootDir1,self.rootDir2) not in self.subdirArray2:
	            self.statusText.SetValue("This file: " + f + " does not correspond to any file in parallel.")
                    self.blocker = True
                    self.statusText.SetForegroundColour(wx.RED)
                    return False
            for f in self.subdirArray2:
	        if f.replace(self.rootDir2,self.rootDir1) not in self.subdirArray1:
	            self.statusText.SetValue("This file: " + f + " does not correspond to any file in parallel.")
                    self.blocker = True
                    self.statusText.SetForegroundColour(wx.RED)
                    return False
        # function for averaging images
	def Average(self, event):
	    self.CheckIfFilesMatch()
	    if self.blocker:
	        return
	    self.count = 0
	    # save file
	    saveDialog = wx.DirDialog(self, "Choose a directory(Your files will be saved in same file names under this):", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
	    # cancel
            if saveDialog.ShowModal() == wx.ID_CANCEL:
                # update status
                self.statusText.SetValue("Did not save")
		self.statusText.SetForegroundColour(wx.BLACK)
	        # ok
	        return
	        
	    else:
	        savePath = saveDialog.GetPath()
	        # start reading file
	        for i in self.subdirArray1:
           	        postfix = i.replace(self.rootDir1, "")
           	        f = self.rootDir2+postfix
           	        if not os.path.isdir(os.path.dirname(savePath+postfix)):
           	            os.makedirs(os.path.dirname(savePath+postfix))
           	        currentSavePath = savePath+postfix
          		try:
         			# update status
         			self.statusText.SetValue("Processing...")
         			self.statusText.SetForegroundColour(wx.BLACK)
         			# try reading the files
         			self.im1 = Image.open(i)
         			self.im2 = Image.open(f)
         			self.count += 1
         			# convert to matrix
         			self.mat1 = numpy.array(self.im1)
         			self.mat2 = numpy.array(self.im2)
         			# convert to uint16 for addition
         			self.mat1 = self.mat1.astype('uint16')
         			self.mat2 = self.mat2.astype('uint16')
         			# get offset
         			try:
            				self.offset = int(self.offsetCtrl.GetValue())
         			except ValueError:
            				#throw error
            				self.statusText.SetValue("Error: please enter integer offset")
            				self.statusText.SetForegroundColour(wx.RED)
            				return
         			# add and convert back to image (with offset)
         			self.result = (self.mat1 + self.mat2 + self.offset)/2
         			self.result[self.result > 255] = 255
         			# convert back to uint 8 for saving
         			self.result = self.result.astype('uint8')
         			self.imResult = Image.fromarray(self.result)
         			# self.imResult = Image.blend(self.im1, self.im2, 1)
          		        self.imResult.save(currentSavePath,"bmp")
                                # update status
                  		self.statusText.SetValue("Saved image to " + currentSavePath)
                  		self.statusText.SetForegroundColour(wx.BLACK)
  		        except IOError:
         			# throw error
         			self.statusText.SetValue("Error: cannot read file : " + i + " or " + f)
         			self.statusText.SetForegroundColour(wx.RED)
   	    return

	# function for adding images
	def Add(self, event):
	    self.CheckIfFilesMatch()
	    if self.blocker:
	        return
	    self.count = 0
	    # save file
	    saveDialog = wx.DirDialog(self, "Choose a directory(Your files will be saved in same file names under this):", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
	    # cancel
            if saveDialog.ShowModal() == wx.ID_CANCEL:
                # update status
                self.statusText.SetValue("Did not save")
		self.statusText.SetForegroundColour(wx.BLACK)
	        # ok
	        return
	        
	    else:
	        savePath = saveDialog.GetPath()
	        # start reading file
	        for i in self.subdirArray1:
           	        postfix = i.replace(self.rootDir1, "")
           	        f = self.rootDir2+postfix
           	        if not os.path.isdir(os.path.dirname(savePath+postfix)):
           	            os.makedirs(os.path.dirname(savePath+postfix))
           	        currentSavePath = savePath+postfix
          		try:
         			# update status
         			self.statusText.SetValue("Processing...")
         			self.statusText.SetForegroundColour(wx.BLACK)
         			# try reading the files
         			self.im1 = Image.open(i)
         			self.im2 = Image.open(f)
         			self.count += 1
         			# convert to matrix
         			self.mat1 = numpy.array(self.im1)
         			self.mat2 = numpy.array(self.im2)
         			# convert to uint16 for addition
         			self.mat1 = self.mat1.astype('uint16')
         			self.mat2 = self.mat2.astype('uint16')
         			# get offset
         			try:
            				self.offset = int(self.offsetCtrl.GetValue())
         			except ValueError:
            				#throw error
            				self.statusText.SetValue("Error: please enter integer offset")
            				self.statusText.SetForegroundColour(wx.RED)
            				return
         			# add and convert back to image (with offset)
             			self.result = self.mat1 + self.mat2 + self.offset
             			self.result[self.result > 255] = 255
             			# convert back to uint 8 for saving
             			self.result = self.result.astype('uint8')
             			self.imResult = Image.fromarray(self.result)
             			#self.imResult = Image.blend(self.im1, self.im2, 1)
          		        self.imResult.save(currentSavePath,"bmp")
                                # update status
                  		self.statusText.SetValue("Saved image to " + currentSavePath)
                  		self.statusText.SetForegroundColour(wx.BLACK)
  		        except IOError:
         			# throw error
         			self.statusText.SetValue("Error: cannot read file : " + i + " or " + f)
         			self.statusText.SetForegroundColour(wx.RED)

	# function for subtracting images
	def Subtract(self, event):
	    self.CheckIfFilesMatch()
	    if self.blocker:
	        return
	    self.count = 0
	    # save file
	    saveDialog = wx.DirDialog(self, "Choose a directory(Your files will be saved in same file names under this):", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT);
	    # cancel
            if saveDialog.ShowModal() == wx.ID_CANCEL:
                # update status
                self.statusText.SetValue("Did not save")
		self.statusText.SetForegroundColour(wx.BLACK)
	        # ok
	        return
	        
	    else:
	        savePath = saveDialog.GetPath()
	        # start reading file
	        for i in self.subdirArray1:
           	        postfix = i.replace(self.rootDir1, "")
           	        f = self.rootDir2+postfix
           	        if not os.path.isdir(os.path.dirname(savePath+postfix)):
           	            os.makedirs(os.path.dirname(savePath+postfix))
           	        currentSavePath = savePath+postfix
          		try:
         			# update status
         			self.statusText.SetValue("Processing...")
         			self.statusText.SetForegroundColour(wx.BLACK)
         			# try reading the files
         			self.im1 = Image.open(i)
         			self.im2 = Image.open(f)
         			self.count += 1
         			# convert to matrix
         			self.mat1 = numpy.array(self.im1)
         			self.mat2 = numpy.array(self.im2)
         			# convert to uint16 for addition
         			self.mat1 = self.mat1.astype('uint16')
         			self.mat2 = self.mat2.astype('uint16')
         			# get offset
         			try:
            				self.offset = int(self.offsetCtrl.GetValue())
         			except ValueError:
            				#throw error
            				self.statusText.SetValue("Error: please enter integer offset")
            				self.statusText.SetForegroundColour(wx.RED)
            				return
         			# subtract and convert back to image (values less than 0 are set to 0)
             			self.result = self.offset + self.mat2 - self.mat1
             			self.result[self.result < 0] = 0
             			# convert back to uint 8 for saving
             			self.result = self.result.astype('uint8')
             			self.imResult = Image.fromarray(self.result)
             			#self.imResult = Image.blend(self.im1, self.im2, 1)
          		        self.imResult.save(currentSavePath,"bmp")
                                # update status
                  		self.statusText.SetValue("Saved image to " + currentSavePath)
                  		self.statusText.SetForegroundColour(wx.BLACK)
  		        except IOError:
         			# throw error
         			self.statusText.SetValue("Error: cannot read file : " + i + " or " + f)
         			self.statusText.SetForegroundColour(wx.RED)

# end class 
# ============================================================================================

# below is needed for all GUIs
if __name__== '__main__':
	app = wx.App(False) # application object (inner workings) PySimpleApp
	frame = imageCalc(parent = None) # frame object (what user sees)
	frame.Show() # show frame
	app.MainLoop() # run main loop	

