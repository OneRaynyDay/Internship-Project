import wx
import wx.lib.scrolledpanel
import csv
import re
import numpy as np
import plotly
from matplotlib.figure import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from PIL import Image as im

class DarkNoiseGrapher(wx.Frame):
    
    #defining the size of the grapher
    PADDING = (100,100)
    SPACE_BETWEEN_SIZER = (100,100)
    SPACE_BETWEEN_BUTTON = (20,20)
    OPTION_NAME = ["Avg", "Other"]
    SPECIAL_OPTIONS = ["Gain"]
    OPTION_MAP = {"Avg":["Avg"], "Other":["Gb","Gr","R", "B"]}
    MY_DPI = 160;
    X_CONST = 0;
    Y_CONST = 1;
    FILE_LIST = ["No file selected", "Open..."]
    comboBoxDict = {};
    fileDict = {};

    def __init__(self, parent, frameSize):
        #setting the window size for good
        self.windowSize = np.subtract(frameSize,self.PADDING)
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Dark Noise Grapher v1.0.0", size = self.windowSize)
        self.mp = wx.Panel(self, wx.ID_ANY)
        
        #create GUI
        self.createSizers()
        self.createFileSelection()
        self.createStatusBar()
        self.createNoisePanel()
        #self.createComboBox() #We currently don't need it to show.
        self.createOptionButtons()
        self.createListCtrl()
        self.createMeasurement()
        self.createScreenShotButton()
        self.finishLayout()
        
        #Settings some things to none or empty
        self.XComboBoxDict = {}
        self.YComboBoxDict = {}
        self.listCtrlComboBox = None
        
        self.resetGlobals()
        
        #binding to events
        #self.Bind(wx.EVT_SIZE, self.onSize)

#===================================GUI=======================================
    def createSizers(self):
        '''creates sizers for the entire program. This must be executed before 
        the other GUI's are loaded.'''
        #=====creating the basic sizers(Split frame into 2)=====
        self.frameGridSizer = wx.GridSizer(1, 0, *self.SPACE_BETWEEN_SIZER) 
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        self.frameGridSizer.Add(self.leftSizer)
        self.frameGridSizer.Add(self.rightSizer)
        
        #=====creating the next level sizers(adding vertically stacked sizers in each side)=====
        #--left side--
        self.fileSelectSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.optionSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #=====RADIO BUTTON SIZER======
        self.radioButtonSizer = wx.GridSizer(1, 2, *self.SPACE_BETWEEN_BUTTON)
        
        self.panelX = wx.lib.scrolledpanel.ScrolledPanel(self.mp,-1, size=np.divide(self.windowSize,5), style=wx.SIMPLE_BORDER)
        self.panelX.SetupScrolling()
        self.panelY = wx.lib.scrolledpanel.ScrolledPanel(self.mp,-1, size=np.divide(self.windowSize,5), style=wx.SIMPLE_BORDER)
        self.panelY.SetupScrolling()
        
        self.XComboBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.YComboBoxSizer = wx.BoxSizer(wx.VERTICAL)
        
	self.radioButtonSizer.Add(self.panelX,1, wx.GROW)
        self.radioButtonSizer.Add(self.panelY,1, wx.GROW)
       
        self.panelX.SetSizer(self.XComboBoxSizer)
        self.panelX.Layout()
        self.panelY.SetSizer(self.YComboBoxSizer)
        self.panelY.Layout()
        #=====END OF RADIO BUTTON SIZER======
        self.graphSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #=========RESULT SIZER==========
        self.resultSizer = wx.GridSizer(1, 2, *self.SPACE_BETWEEN_BUTTON)
        
        self.panelXPost = wx.lib.scrolledpanel.ScrolledPanel(self.mp,-1, size=np.divide(self.windowSize,7), style=wx.SIMPLE_BORDER)
        self.panelXPost.SetupScrolling()
        self.panelYPost = wx.lib.scrolledpanel.ScrolledPanel(self.mp,-1, size=np.divide(self.windowSize,7), style=wx.SIMPLE_BORDER)
        self.panelYPost.SetupScrolling()
       
        self.xPostSizer = wx.GridSizer(3,0)
        self.yPostSizer = wx.GridSizer(3,0)
        
        self.resultSizer.Add(self.panelXPost,1, wx.GROW)
        self.resultSizer.Add(self.panelYPost,1, wx.GROW)
        
        self.panelXPost.SetSizerAndFit(self.xPostSizer)
        self.panelXPost.Layout()
        self.panelYPost.SetSizer(self.yPostSizer)
        self.panelYPost.Layout()
        #=======END OF RESULT SIZER=======
        self.leftSizer.Add(self.fileSelectSizer, 0, wx.ALL, 5)
        self.leftSizer.Add(self.optionSizer, 0, wx.ALL, 5)
        self.leftSizer.Add(self.radioButtonSizer, 0, wx.ALL, 5)
        self.leftSizer.Add(self.graphSizer, 0, wx.ALL, 5)
        self.leftSizer.Add(self.resultSizer, 0, wx.ALL, 5)
        #--right side--
        self.statisticSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.measurementSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.screenshotSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.rightSizer.Add(self.statisticSizer, 0, wx.ALL, 5)
        self.rightSizer.Add(self.measurementSizer, 0, wx.ALL, 5)
        self.rightSizer.Add(self.screenshotSizer, 0, wx.ALL, 5)
    
    def createMeasurement(self):
        # create the gridsizer to hold everything in
        self.dispsizer = wx.FlexGridSizer(3, 3, 5, 5)
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
        
        self.dispsizer.Add(wx.StaticText(self.mp, -1, ""))
	self.dispsizer.Add(self.lefttext)
	self.dispsizer.Add(self.righttext)
        self.dispsizer.Add(self.xtext)
	self.dispsizer.Add(self.leftxdisp)
	self.dispsizer.Add(self.rightxdisp)
        self.dispsizer.Add(self.ytext)
	self.dispsizer.Add(self.leftydisp)
	self.dispsizer.Add(self.rightydisp)
	
	self.measurementSizer.Add(self.dispsizer)
    def createOptionButtons(self):
        self.resetButton = wx.Button(self.mp, id=-1, label='Clear Canvas', size=(100,-1), style=wx.ALIGN_RIGHT)
        self.resetButton.Bind(wx.EVT_BUTTON, self.resetCanvas)

        self.avgOptionButton = wx.RadioButton(self.mp, -1, self.OPTION_NAME[0], (10, 10), style=wx.RB_GROUP)
        self.avgOptionButton.Name = self.OPTION_NAME[0]
        self.Bind(wx.EVT_RADIOBUTTON, self.onCheckOption, id=self.avgOptionButton.GetId())
        
        self.otherOptionButton = wx.RadioButton(self.mp, -1, self.OPTION_NAME[1], (10, 10))
        self.otherOptionButton.Name = self.OPTION_NAME[1]
        self.Bind(wx.EVT_RADIOBUTTON, self.onCheckOption, id=self.otherOptionButton.GetId())
        
        self.optionSizer.Add(self.avgOptionButton)
        self.optionSizer.Add(self.otherOptionButton)
        self.optionSizer.Add(self.resetButton)
        
    def createFileSelection(self):
        '''creates the file selection that is required to open file system'''
        # file selection
        self.fileDisplay = wx.Choice(self.mp, -1, size=(580,-1), choices = self.FILE_LIST)
	self.fileDisplay.SetSelection(0)
	self.fileDisplay.Bind(wx.EVT_CHOICE, self.selectFile)
	self.fileSelectSizer.Add(self.fileDisplay)
	
    def createStatusBar(self):
        '''creates status bar and sets initial message'''
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetStatusText("Ready")
    
    def createNoisePanel(self):
        '''creates the noise panel from ==Matplot Graph=='''
        self.noisePanel = NoisePanel(self.mp, self)
        self.graphSizer.Add(self.noisePanel)
    
    def createListCtrl(self):
        '''creates the listctrl, the dynamically loading is loadListCtrl()'''
        self.dataListCtrlX = wx.ListCtrl(self.mp, -1, size=(np.divide(self.windowSize,4)[0], np.divide(self.windowSize, 1.4)[1]), style=wx.LC_REPORT)
        self.dataListCtrlY = wx.ListCtrl(self.mp, -1, size=(np.divide(self.windowSize,4)[0], np.divide(self.windowSize, 1.4)[1]), style=wx.LC_REPORT)
        self.statisticSizer.Add(self.dataListCtrlX)
        self.statisticSizer.Add(self.dataListCtrlY)
    
    def createScreenShotButton(self):
        self.screenshotSizer.Add(wx.StaticText(self.mp, -1, "Click for a screenshot"))
        self.screenshotButton = wx.Button(self.mp, id=-1, label='Screenshot', size=(100,-1))
        self.screenshotSizer.Add(self.screenshotButton)
    def finishLayout(self):   
        self.mp.SetAutoLayout(True)
	self.mp.SetSizer(self.frameGridSizer)
	self.mp.Layout()
	self.Layout()

#================================Computation===================================
    def onCheckOption(self, event):
        #first try to remove all selected buttons
        for xbutt in self.XButtonPostfixGroup:
            if(xbutt.GetValue()):
                xbutt.SetValue(False)
                self.setPostfixVal(None, btn=xbutt)
                
        for ybutt in self.YButtonPostfixGroup:
            if(ybutt.GetValue()):
                ybutt.SetValue(False)
                self.setPostfixVal(None, btn=ybutt)

        button = event.GetEventObject()
        name = button.Name
        #val = button.GetValue() this is not really necessary - postpone code
        for field in self.OPTION_MAP[name]:
            for buttonX in self.XButtonPostfixGroup:
                if buttonX.Name.endswith(field) or any(buttonX.Name.endswith(option) for option in self.SPECIAL_OPTIONS):
                    for buttonY in self.YButtonPostfixGroup:
                        if buttonY.Name.endswith(field) or any(buttonY.Name.endswith(option) for option in self.SPECIAL_OPTIONS):
                            buttonX.SetValue(True)
                            self.setPostfixVal(None, btn=buttonX)
                            buttonY.SetValue(True)
                            self.setPostfixVal(None, btn=buttonY)
        
    def onSize(self, event):
        '''Try to change the size of the matplotlib
        CURRENTLY NOT IN USE'''
        self.noisePanel.changeSize(*self.GetClientSize())
    def selectFile(self, event):
        '''Opens the textfile and then delegates tasks for reading the file and initial loading'''
	if self.fileDisplay.GetCurrentSelection() == 1: # Open
	   wildcard = "TEXT files (*.txt)|*.txt"
	   fileDialog = wx.FileDialog(None, "Select a Text file", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
	   
	   if fileDialog.ShowModal() == wx.ID_CANCEL:
	       self.fileDisplay.SetSelection(0)
	       return
	   
	   #get the file
	   self.filePaths = fileDialog.GetPaths()
	   #set GUI's
	   self.FILE_LIST[0] = str(self.filePaths)
	   self.fileDisplay.SetItems(self.FILE_LIST)
	   self.destroyComboBox()
	   self.readText(self.filePaths)#read the file 
	   self.graph(event)#graph it
	   self.createComboBox(self.filePaths)
	   for fileItem in self.filePaths:
	       self.loadComboBox(self.fileDict[fileItem], self.XComboBoxDict[fileItem], endFields = ["B"]+self.SPECIAL_OPTIONS)
	       self.loadComboBox(self.fileDict[fileItem], self.YComboBoxDict[fileItem], endFields = ["B"]+self.SPECIAL_OPTIONS)
	   
	elif self.fileDisplay.GetCurrentSelection() == 0: # original file
	   # do nothing
	   return
	   
    def readText(self, paths):
        '''reads the csv file into a very important variable:
        @Param coordinateDict is a dictionary with the key name and an array of values associated with it
        e.x. : key: 'Gain', value: [3,3,1,2,4]'''
        for path in paths:
            f = open(path, 'rU')
            csv_reader = csv.reader(f)
            #getting x and y scales
            line1=csv_reader.next()
            self.x = (float(re.split('=',line1[2])[1]), float(re.split('=',line1[3])[1]))
            self.y = (float(re.split('=',line1[4])[1]), float(re.split('=',line1[5])[1]))
            
            csv_reader.next()
            line2 = csv_reader.next()[0].split('\t')
            coordinateDict = {} #dict of arrays of values
            coordinateLineNum = {} #dict of column num
            
            count = 0#count for the column num
            for line in line2:
                coordinateDict[line] = [] #empty array, but it is an array
                coordinateLineNum[line] = count
                count += 1
            for line in csv_reader:
                #each val from each line
                linesplit = line[0].split('\t')
                #each key in the map
                for key in line2:
                    try:
                        coordinateDict[key].append(float(linesplit[coordinateLineNum[key]])) #this means "get the number at this line 
                                                                                                #where the map's field would align at"
                    except ValueError:
                        print "Value Error occured while trying to read in array! Line: " + coordinateLineNum[key].__str__() + " field: " + key.__str__()
            
            for key in coordinateDict:
                coordinateDict[key] = np.array(coordinateDict[key])
            self.fileDict[path] = coordinateDict
    def destroyComboBox(self):
        #for fileItem in self.XComboBoxDict:
        #    self.XComboBoxDict[fileItem].Destroy()
        #for fileItem in self.YComboBoxDict:
        #    self.YComboBoxDict[fileItem].Destroy()
        self.XComboBoxSizer.DeleteWindows()
        self.YComboBoxSizer.DeleteWindows()
        if self.listCtrlComboBox != None:
            self.listCtrlComboBox.Destroy()
            self.listCtrlComboBox = None
        self.XComboBoxDict = {}
        self.YComboBoxDict = {}
        self.YSelected = {};
        self.XSelected = {};
        
    def createComboBox(self, fileList):
        for fileItem in fileList:
            self.XComboBoxSizer.Add(wx.StaticText(self.panelX, -1, fileItem, style=wx.ALIGN_RIGHT))
            self.XComboBoxDict[fileItem] = wx.ComboBox(self.panelX, -1, style=wx.CB_DROPDOWN)
            self.XComboBoxDict[fileItem].Name = "X"
            self.YComboBoxSizer.Add(wx.StaticText(self.panelY, -1, fileItem, style=wx.ALIGN_RIGHT))
            self.YComboBoxDict[fileItem] = wx.ComboBox(self.panelY, -1, style=wx.CB_DROPDOWN)
            self.YComboBoxDict[fileItem].Name = "Y"
            self.XComboBoxDict[fileItem].Bind(wx.EVT_COMBOBOX, self.onSelect)
            self.YComboBoxDict[fileItem].Bind(wx.EVT_COMBOBOX, self.onSelect)
            self.XComboBoxSizer.Add(self.XComboBoxDict[fileItem])
            self.YComboBoxSizer.Add(self.YComboBoxDict[fileItem])
            self.panelX.Layout()
            self.panelY.Layout()
            self.mp.Layout()
    
    def loadComboBox(self, dictionary, comboBox, removeFields = [""], endFields = [""]):
        for key in dictionary:
            if any(key == case for case in removeFields): # we know this has no fields
                continue
            if any(key.endswith(case) for case in endFields): #This is the start of a group
                comboBox.Append(re.split(" ", key)[0])
    
    def onSelect(self, event):
        '''set values of the coordinates for the graph according to the select button and radio button'''
        
        comboBox = event.GetEventObject()
        item = comboBox.GetStringSelection()
        if comboBox.Name.startswith("X"): #it's an X button
            self.XSelected = {}
            self.XCoordinates = {} #empty it
            self.XButtonPostfix = []
            self.XSelected["name"] = item

            for cmbBox in self.XComboBoxDict:
                if(self.XComboBoxDict[cmbBox] == comboBox):
                    self.XSelected["path"] = cmbBox
                    for key in self.fileDict[cmbBox]:
                        if key.startswith(item): 
                            self.XButtonPostfix.append(re.split(" ", key)[-1])
                                    
        elif comboBox.Name.startswith("Y"):
            self.YSelected = {}
            self.YCoordinates = {} #empty it
            self.YButtonPostfix = []
            self.YSelected["name"] = item
            
            for cmbBox in self.YComboBoxDict:
                if(self.YComboBoxDict[cmbBox] == comboBox):
                    self.YSelected["path"] = cmbBox
                    for key in self.fileDict[cmbBox]:
                        if key.startswith(item):
                            self.YButtonPostfix.append(re.split(" ", key)[-1])
                    
        if self.YButtonPostfix.__len__() != 0 and self.XButtonPostfix.__len__() != 0:
            self.loadCheckBoxes()
        #self.graph(event)
        
    def loadCheckBoxes(self):
        self.deleteAllCheckboxes()
        #removing all previous buttons first
        for count, val in enumerate(self.XButtonPostfixGroup):
            val.Destroy()
        for count, val in enumerate(self.YButtonPostfixGroup):
            val.Destroy()
            
        #Empty out the previous boxes
        self.XButtonPostfixGroup = []
        self.YButtonPostfixGroup = []
        
        for postfix in self.XButtonPostfix:
            self.XButtonPostfixGroup.append(wx.CheckBox(self.panelXPost, -1 ,postfix, (10,10)))
            self.Bind(wx.EVT_CHECKBOX, self.setPostfixVal, id = self.XButtonPostfixGroup[-1].GetId())
            self.XButtonPostfixGroup[-1].Name = "X" + postfix
        for postfix in self.YButtonPostfix:
            self.YButtonPostfixGroup.append(wx.CheckBox(self.panelYPost, -1 ,postfix, (10,10)))
            self.Bind(wx.EVT_CHECKBOX, self.setPostfixVal, id = self.YButtonPostfixGroup[-1].GetId())
            self.YButtonPostfixGroup[-1].Name = "Y" + postfix

        #add the buttons
        self.addButtonsToGroup(self.XButtonPostfixGroup, self.xPostSizer, specialCase = self.SPECIAL_OPTIONS, eventFunc=self.setPostfixVal)
        self.addButtonsToGroup(self.YButtonPostfixGroup, self.yPostSizer, specialCase = self.SPECIAL_OPTIONS, eventFunc=self.setPostfixVal)

        #finalize the layout
        self.resetOptionLayout()
    
    def addButtonsToGroup(self, btnGroup, sizer, specialCase = [""], eventFunc=None):
        for button in btnGroup:
            sizer.Add(button,0, wx.ALL, 5)
            if specialCase != [""] and any(button.Name.endswith(case) for case in specialCase):
                button.SetValue(True)
                eventFunc(None, btn=button)
                button.Hide()
    
    def setPostfixVal(self, event, btn = None): 
        '''sets value of the checkbox buttons'''
        if(btn == None):
            button = event.GetEventObject()
        else:
            button = btn
            
        state = button.GetValue()
        buttonName = button.Name
        if state: #is the checkbox checked? Yes it is!
            if buttonName.startswith("X"): #it's an X button and we have to add it to the list
                self.XPostfixSelected.append(button)
            elif buttonName.startswith("Y"):
                self.YPostfixSelected.append(button)
        else: #is the checkbox checked? No it's not!
            if buttonName.startswith("X"): #it's an X button and we have to add it to the list
                self.XPostfixSelected.remove(button)
            elif buttonName.startswith("Y"):
                self.YPostfixSelected.remove(button)

        if self.XPostfixSelected.__len__() != 0 and self.YPostfixSelected.__len__() != 0:
            self.plotTitle = self.XSelected["name"] + " vs. " + self.YSelected["name"]
            self.loadCoordinateValues()
        else:
            self.clearListCtrl()
    
    def loadCoordinateValueHelper(self, coordinates, selectedPostfix, selected, prefix):
        for postfix in selectedPostfix:
            pref = selected["name"]
            postf = re.split(prefix, postfix.Name)[-1]
            if(pref != postf):
                name = pref+" "+postf
            else:
                name = pref
            coordinates[name] = self.fileDict[selected["path"]][name];
    def loadCoordinateValues(self):
        self.XCoordinates = {}
        self.YCoordinates = {}
        self.loadCoordinateValueHelper(self.XCoordinates, self.XPostfixSelected, self.XSelected, "X")
        self.loadCoordinateValueHelper(self.YCoordinates, self.YPostfixSelected, self.YSelected, "Y")
        self.graph(None)
        
    def graph(self, event): 
        if self.XCoordinates.__len__() == 0 or self.YCoordinates.__len__() == 0:
            self.statusBar.SetStatusText("Graph Axes not loaded yet")
            return
        
   	self.PlotChosen(self.XCoordinates, self.YCoordinates)
        return	
        
    def PlotChosen(self, X, Y):
        self.noisePanel.clear()
        for innerX in X:
            postfix = re.split(" " , innerX)[-1]
            for innerY in Y:
                if innerY.endswith(postfix) or any((innerY == member or innerX == member) for member in self.SPECIAL_OPTIONS):
                    self.noisePanel.axes.plot(X[innerX], Y[innerY])
        self.noisePanel.setTitle(self.plotTitle)
        self.noisePanel.display()
        if self.listCtrlComboBox != None:
            self.listCtrlComboBox.Destroy()
            self.listCtrlComboBox = None
        self.populateListCtrl(False, X, Y)
    
    #================RESETTING THE CANVAS AND RESETTING FUNCTIONS==================
    def resetCanvas(self, event):
        self.deleteAllCheckboxes()
        self.noisePanel.clear()
        self.clearListCtrl()
        if self.listCtrlComboBox != None:
            self.listCtrlComboBox.Destroy()
            self.listCtrlComboBox = None
        self.loadListCtrlComboBox(self.filePaths)
        #self.populateListCtrl(True, None, None)
        
        
    def clearListCtrl(self):
        self.dataListCtrlX.ClearAll()
        self.dataListCtrlY.ClearAll()
    def loadListCtrlComboBox(self, fileList):
        self.listCtrlComboBox = wx.ComboBox(self.mp, -1, choices = fileList, style=wx.CB_DROPDOWN)
        self.listCtrlComboBox.Bind(wx.EVT_COMBOBOX, self.changeListCtrlDefault)
        self.optionSizer.Add(self.listCtrlComboBox)
        self.currentSelectedFile = fileList[0]
        self.populateListCtrl(True, None, None)
        self.mp.Layout()
    def changeListCtrlDefault(self, event):
        self.currentSelectedFile = event.GetEventObject().GetStringSelection()
        self.populateListCtrl(True, None, None)
    def resetOptionLayout(self):
        self.panelXPost.Layout()
        self.panelYPost.Layout()
	self.mp.Layout()
    def deleteAllCheckboxes(self):
        for button in self.XButtonPostfixGroup:
            button.Destroy()
        for button in self.YButtonPostfixGroup:
            button.Destroy()
        self.XButtonPostfixGroup = []
        self.YButtonPostfixGroup = []
        self.XPostfixSelected = []
        self.YPostfixSelected = []
    def createStringItems(self, startIndex, var, prefix, listCtrl):
        for index,inner in enumerate(var):
            if index >= startIndex:
                listCtrl.InsertColumn(index-startIndex, prefix + inner)
        startLength = 0
        for index, inner in enumerate(var):
            if index >= startIndex:
                for i, val in enumerate(var[inner]):
                    if index == startIndex:
                        listCtrl.InsertStringItem(i, str(val))
                        startLength += 1
                    elif i < startLength:
                        listCtrl.SetStringItem(i, index-startIndex, str(val))
                    
    def populateListCtrl(self, isCleared, X, Y):
        '''populates the listCtrl object with the given X and Y. If
        the canvas was recently cleared, it would get populated with all of the options'''
        
        if isCleared:
            #change the size of the widget
            #self.dataListCtrlX.SetSize(size=(np.divide(self.windowSize,2)[0], np.divide(self.windowSize, 1.2)[1]))
            #self.dataListCtrlX.PostSizeEventToParent()
            #put everything in the X column   
            self.dataListCtrlX.ClearAll()
            self.dataListCtrlX.SetDimensions(x = 0, y = 0, width=np.divide(self.windowSize,2)[0], height=np.divide(self.windowSize, 1.4)[1])
            self.dataListCtrlY.Show(False)
            self.mp.Layout()
            self.createStringItems(1, self.fileDict[self.currentSelectedFile], "", self.dataListCtrlX)
        else:
            self.dataListCtrlY.Show(True)
            self.dataListCtrlX.SetDimensions(x = 0, y = 0, width=np.divide(self.windowSize,4)[0], height=np.divide(self.windowSize, 1.4)[1])
            self.mp.Layout()
            self.dataListCtrlX.ClearAll()
            self.dataListCtrlY.ClearAll()
            self.createStringItems(0, X, "X ", self.dataListCtrlX)
            self.createStringItems(0, Y, "Y ", self.dataListCtrlY)
            
    def clearColor(self, listCtrl, color):
        for column in range(listCtrl.GetItemCount()):
            if listCtrl.GetItemBackgroundColour(column) == color:
                listCtrl.SetItemBackgroundColour(column, wx.WHITE)
    def resetGlobals(self):
        self.XButtonPostfixGroup = []
        self.YButtonPostfixGroup = []
        self.XButtonPostfix = []
        self.YButtonPostfix = []
        self.XSelected = {}
        self.YSelected = {}
        self.XPostfixSelected = []
        self.YPostfixSelected = []
        self.XCoordinates = {}
        self.YCoordinates = {}
#===========================Matplot Graph======================================
class NoisePanel(wx.Panel):
	flag = None
	decimals = 4
	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, id=wx.ID_ANY)

		self.frame = frame
		# create a panel
		self.panel = wx.Panel(self, wx.ID_ANY)
		# set color of graph background to white
		self.figure = plt.figure(facecolor="white")
		self.frameSize = np.divide(frame.GetClientSize(), self.frame.MY_DPI)
		self.figure.set_size_inches(self.frameSize, forward=True)
		# define canvas
		self.canvas = FigureCanvas(self.panel, -1, self.figure)
		# add a plot to the axes
		self.axes = self.figure.add_subplot(111)
		self.axes.grid()
		# add the canvas to a sizer for alignment
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas, 0, wx.ALL, 5)
		
		# draw vertical lines
		self.leftxline, = self.axes.plot([0], [0], color='b')
		self.rightxline, = self.axes.plot([0], [0], color='r')
		self.leftyline, = self.axes.plot([0], [0], color='b')
		self.rightyline, = self.axes.plot([0], [0], color='r')
		
		# define callbacks for mouse click, move and release events
		self.click = self.canvas.mpl_connect('button_press_event', self.OnClick)
		self.move = self.canvas.mpl_connect('motion_notify_event', self.OnMove)
		self.release = self.canvas.mpl_connect('button_release_event', self.OnRelease)

		# refresh layout and sizers
		self.panel.SetAutoLayout(True)
		self.panel.SetSizer(self.sizer)
		self.panel.Layout()
		self.sizer.Fit(self.panel)
        
        def changeSize(self, x, y):
            self.frameSize = np.divide([x,y], self.frame.MY_DPI)
            self.figure.set_size_inches(self.frameSize, forward=True)
            self.panel.SetSizer(self.sizer)
	    self.panel.Layout()
	
        def manageLines(self, xData, yData, yBound, xBound, clr, event):
            # remove old lines
            if clr == 'r':
                try:
                    self.rightxline.remove()
                    self.rightyline.remove()
                except Exception: pass
                # define new lines
                self.rightxline, = self.axes.plot(xData, yBound, color=clr)
                self.rightyline, = self.axes.plot(xBound, yData, color=clr)
                # redraw the graph
                self.canvas.draw()
                # update the values
                self.frame.rightxdisp.SetValue(str(format(event.xdata, "."+str(self.decimals)+"f")))
                self.frame.rightydisp.SetValue(str(format(event.ydata, "."+str(self.decimals)+"f")))
            else:
                try:
                    self.leftxline.remove()
                    self.leftyline.remove()
                except Exception: pass
                # define new lines
                self.leftxline, = self.axes.plot(xData, yBound, color=clr)
                self.leftyline, = self.axes.plot(xBound, yData, color=clr)
                # redraw the graph
                self.canvas.draw()
                # update the values
                self.frame.leftxdisp.SetValue(str(format(event.xdata, "."+str(self.decimals)+"f")))
                self.frame.leftydisp.SetValue(str(format(event.ydata, "."+str(self.decimals)+"f")))
        
        def processGeneralMouseMovements(self, event, flagVal, needToVerify):
                # check to make sure that the mouse is being clicked
                if needToVerify:
          		if self.flag is None: return
          		if event.xdata is None: return
		# define local variables for convenience
		xdata = event.xdata
		ydata = event.ydata
		xbound = self.axes.get_xbound()
		ybound = self.axes.get_ybound()
		if event.button == 1: # left click (blue lines)
			self.manageLines([xdata, xdata], [ydata, ydata], [ybound[0], ybound[1]], [xbound[0], xbound[1]], 'b', event)
		if event.button == 3: # right click (red lines)
			self.manageLines([xdata, xdata], [ydata, ydata], [ybound[0], ybound[1]], [xbound[0], xbound[1]], 'r', event)
		# highlight the corresponding data entry in the side data box
		self.flag = flagVal
		self.highlightData(event.button)
        # callback when mouse clicks down
	# draws horizontal and vertical lines at cursor positions
	def OnClick(self, event):
		self.processGeneralMouseMovements(event, 1, False)
	
	# callback when mouse moves after it clicks down (same as click down)
	# draws horizontal and vertical lines at cursor positions
	def OnMove(self, event):
	        self.processGeneralMouseMovements(event, self.flag, True)

	# callback when mouse click releases (same as click down)
	# draws horizontal and vertical lines at cursor positions
	def OnRelease(self, event):
		self.processGeneralMouseMovements(event, None, False)
	def highlightData(self, flag):
	    
	    if flag == 1: # left click (blue lines) 
	        self.frame.clearColor(self.frame.dataListCtrlX, wx.BLUE)
	        self.frame.clearColor(self.frame.dataListCtrlY, wx.BLUE)
	        self.highlightDataLoad(self.frame.leftxdisp, wx.BLUE)
            elif flag == 3:
                self.frame.clearColor(self.frame.dataListCtrlX, wx.RED)
	        self.frame.clearColor(self.frame.dataListCtrlY, wx.RED)
	        self.highlightDataLoad(self.frame.rightxdisp, wx.RED)
	def highlightDataLoad(self, disp, color):
	    val = disp.GetValue()
	    fVal = {}
	    for key in self.frame.XCoordinates:
                copyList = [abs(float(x) - float(val)) for x in list(self.frame.XCoordinates[key])]
	        fVal[key] = (self.frame.XCoordinates[key][copyList.index(min(copyList))])
                count = self.frame.dataListCtrlX.GetItemCount()
                for column in range(self.frame.dataListCtrlX.GetColumnCount()):
                    for rows in range(count):
                        listItem = self.frame.dataListCtrlX.GetItem(itemId=rows, col=column)
                        valItem = self.frame.dataListCtrlY.GetItem(itemId=rows, col=column)
                        try:
                            if fVal[re.split("X ",self.frame.dataListCtrlX.GetColumn(column).GetText())[-1]] == float(listItem.GetText()):
                                listItem.SetBackgroundColour(color)
                                self.frame.dataListCtrlX.SetItem(listItem)
                                valItem.SetBackgroundColour(color)
                                self.frame.dataListCtrlY.SetItem(valItem)
                        except KeyError:
                            print "Error: doesn't have this key"
	def setTitle(self, name):
	    self.figure.suptitle(name)
        def display(self):
	    #self.figure.axes.grid()
            self.canvas.draw()
        def clear(self):
            self.axes.cla()
            self.canvas.draw()        
if __name__ == '__main__':
    app = wx.App()
    frameSize = wx.DisplaySize()

    DarkNoiseGrapher(None, frameSize).Show()
    app.MainLoop()  