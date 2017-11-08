########################################################################################################
##  RaspiSim.py   -   Simulator Jig for Security Paper Sensor
##  Copyright (C) by xxx Co,Ltd. All rights reserved
##  
##  
##  Modification History
##  No, Date,           Name,       Description
##  ------------------------------------------------------
##  01, 2017/08/30,     JeonHS,     Designning
##  
##  
########################################################################################################
# encoding=utf-8

import wx
import sys
import glob
import serial    # for communication with serial port (http://pyserial.sf.net)
import time    # for time stuff
import datetime
import signal
import threading
import copy
import os


### Version Information
verMajor    = 0
verMinor    = 0
verPatch    = 1
buildDate   = '2017/09/28'



### Text for GUI
serialPort_ListStr  = []        ##SerialPortsCfg.Search_SerialPorts()      ### Search a Last Serial Port No.
baudRate_ListStr    = ['9600', '19200', '38400', '57600', '115200']      # 0:9600, 1:19200, 2:38400, 3:57600, 4:115200
dataBit_ListStr     = ['7', '8']                                         # '7':7data,  '8':8data
parityBit_ListStr   = ['N', 'O', 'E']                                    # 'N':No,  'O':Odd,  'E':Even
stopBit_ListStr     = ['1', '2']                                         # '1':1bit,  '2':2bit

### Data List for Serial Config Setting
serialPort_List  = copy.deepcopy(serialPort_ListStr)            # by deep copy
baudRate_List   = [9600, 19200, 38400, 57600, 115200]           # 0:9600, 1:19200, 2:38400, 3:57600, 4:115200
dataBit_List    = [7, 8]                                        # 0:7data, 1:8data
parityBit_List  = ['N', 'O', 'E']                               # 'N':No,  'O':Odd,  'E':Even
stopBit_List    = [1, 2]                                        # 0:1bit, 1:2bit


### Data Value for Serial Config Setting
comPortNo = 'rsv'   # COMx                  # Setting a Comm Port

### Default Config : Last comPortNo, 19200, 8data, Odd Parity, 1 stop bit
###    Type         : string          : int                    : int                     : string                  : int
com_Info = {'PortNo':comPortNo, 'Baud':baudRate_List[1], 'Data':dataBit_List[1], 'Parity':parityBit_List[1], 'Stop':stopBit_List[0]}  # Loading a Serial Port Information
#com_InfoTmp = copy.copy(com_Info)          # Shallow Copy : Only Copy to obj Address
com_InfoTmp = copy.deepcopy(com_Info)       # Deep Copy : Copy to obj Data Value

##print ('com_Info(Default):', com_Info)

##print ('Last ComNo:', serialPortList[serialPort_Size-1])
##print ('reserved ComNo:', serialPortList[:-1])

##### Global Obj
devInfo = {'Product':'unknown', 'Version':'00.00.00', 'SerialNo':'xxxxx'}
##devName = 'unknown'
##devVer  = '00.00.00'
##devSerNo = 'xxxxx'
##devInfo = {'Product':devName, 'Version':devVer, 'SerialNo':devSerNo}

ser = serial.Serial()                       ### Serial Open Mothod 1, by default constructor


dataLog = ''                                ### for File Save Data

class SerialPortsCfg():
    ##def __init__():
        ##self.SerialPortsCfg_InitSet()
        
    def Search_SerialPorts():
        # Lists serial port names   
        #   
        #    :raises EnvironmentError:   
        #        On unsupported or unknown platforms   
        #    :returns:   
        #        A list of the serial ports available on the system   
        #
        if sys.platform.startswith('win'):   
            ports = ['COM%s' % (i + 1) for i in range(256)]   
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):   
            # this excludes your current terminal "/dev/tty"   
            ports = glob.glob('/dev/tty[A-Za-z]*')   
        elif sys.platform.startswith('darwin'):   
            ports = glob.glob('/dev/tty.*')   
        else:   
            raise EnvironmentError('Unsupported platform')   
           
        result = []   
        for port in ports:   
            try:   
                ser = serial.Serial(port)   
                ser.close()   
                result.append(port)   
            except (OSError, serial.SerialException):   
                pass   
        return result   

    def SerialPortsCfg_InitSet():
        global com_Info, com_InfoTmp
        global serialPort_ListStr, serialPort_List, comPortNo
        
        serialPort_ListStr  = SerialPortsCfg.Search_SerialPorts()      ### Search a Last Serial Port No.
        serialPort_List  = copy.deepcopy(serialPort_ListStr)            # by deep copy
        
        
        ### Data Value for Serial Config Setting
        serialPort_ListSize = len(serialPort_ListStr)
        if (serialPort_ListSize) :
            comPortNo = serialPort_ListStr[serialPort_ListSize - 1]     ## COMx
        
        ### Default Config : Last comPortNo, 19200, 8data, Odd Parity, 1 stop bit
        ###    Type         : string          : int                    : int                     : string                  : int
        com_Info = {'PortNo':comPortNo, 'Baud':baudRate_List[1], 'Data':dataBit_List[1], 'Parity':parityBit_List[1], 'Stop':stopBit_List[0]}  # Loading a Serial Port Information
        #com_InfoTmp = copy.copy(com_Info)          # Shallow Copy : Only Copy to obj Address
        com_InfoTmp = copy.deepcopy(com_Info)       # Deep Copy : Copy to obj Data Value

    def SerialPortsCfg_Connect():
        global com_Info, com_InfoTmp
        global ser
        
        ##ser = serial.Serial()                                 ### Serial Open Mothod 1, by default constructor
        ser.port        = com_Info['PortNo']
        ser.baudrate    = com_Info['Baud']
        ser.bytesize    = com_Info['Data']
        ser.parity      = com_Info['Parity']
        ser.stopbits    = com_Info['Stop']
        ser.timeout     = 0              ## None : wait Forever, 0: Non-Blocking Mode, 1: Set Time out to x seconds
        ser.xonoff      = False
        ser.rtscts      = False
        ser.dsrdtr      = False
        
        ret = True
        try:
            ser.open()
        except:
            ret = False
        ##print ('----- serial Connect:', ser)
        ##print ('----- serial open?', ser.is_open)
        ##print ('com_InfoTmp: ', com_InfoTmp)
        ##print ('com_Info: ', com_Info)
        
        return ret

    def SerialPortsCfg_DisConnect():
        global com_Info, com_InfoTmp
        global ser
        
        ret = True
        try:
            ##ser = serial.Serial(com_Info['PortNo'])                                  ### Serial Open Mothod 1, by default constructor
            ser.close()
        except:
            ret = False
        ##print ('----- serial Disconnect:', ser)
        ##print ('----- serial open?', ser.is_open)
        ##print ('com_InfoTmp: ', com_InfoTmp)
        ##print ('com_Info: ', com_Info)
        
        return ret

    def SerialPortsCfg_Update():
        global com_Info, com_InfoTmp
        
        com_Info['PortNo']   = copy.deepcopy(com_InfoTmp['PortNo'])
        com_Info['Baud']     = copy.deepcopy(com_InfoTmp['Baud'])
        com_Info['Data']     = copy.deepcopy(com_InfoTmp['Data'])
        com_Info['Parity']   = copy.deepcopy(com_InfoTmp['Parity'])
        com_Info['Stop']     = copy.deepcopy(com_InfoTmp['Stop'])
        
    def SerialPortsCfg_Restore():
        global com_Info, com_InfoTmp
        
        com_InfoTmp['PortNo']   = copy.deepcopy(com_Info['PortNo'])
        com_InfoTmp['Baud']     = copy.deepcopy(com_Info['Baud'])
        com_InfoTmp['Data']     = copy.deepcopy(com_Info['Data'])
        com_InfoTmp['Parity']   = copy.deepcopy(com_Info['Parity'])
        com_InfoTmp['Stop']     = copy.deepcopy(com_Info['Stop'])
        
class Dialog_SerialPort_Config(wx.Dialog):
    global com_Info, com_InfoTmp
    global serialPort_ListStr, baudRate_ListStr, dataBit_ListStr, parityBit_ListStr, stopBit_ListStr
    
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title='Serial Port', size=(250, 250))     # Initialize a Dialog
        
        ### config variable init
        #com_InfoTmp = com_Info     # shallow copy
        SerialPortsCfg.SerialPortsCfg_Restore()
        
        self.InitGUI_SerialPortCfg()
        
    def InitGUI_SerialPortCfg(self):
        global serialPort_ListStr, serialPort_List
        
        ### Serial Port No UpDate!
        serialPort_ListStr  = SerialPortsCfg.Search_SerialPorts()      ### Search a Last Serial Port No.
        serialPort_List     = copy.deepcopy(serialPort_ListStr)
        
        ### Serial Port Configuration Item Name
        size_font = 13
        x=15
        y=15
        dt_x=0
        dt_y=30
        wx.StaticText(self, size_font, 'Port:',    pos=(x + dt_x*0 ,    y + dt_y*0))
        wx.StaticText(self, size_font, 'Baud:',    pos=(x + dt_x*1 ,    y + dt_y*1))
        wx.StaticText(self, size_font, 'Data:',    pos=(x + dt_x*2 ,    y + dt_y*2))
        wx.StaticText(self, size_font, 'Parity',   pos=(x + dt_x*3 ,    y + dt_y*3))
        wx.StaticText(self, size_font, 'Stop',     pos=(x + dt_x*4 ,    y + dt_y*4))
        
        ### Serial Port Configuration ComboBox for User Selection
        x=60
        y=15
        dt_x=0
        dt_y=30
        #wx.ComboBox : __init__ (self, parent, id=ID_ANY, value=””, pos=DefaultPosition, size=DefaultSize, choices=[], style=0, validator=DefaultValidator, name=ComboBoxNameStr)
        wx.ComboBox(self, 211, value=com_Info['PortNo'],    pos=(x+dt_x*0, y+dt_y*0), size=(120, -1), choices = serialPort_ListStr,  style = wx.CB_READONLY)           # Create a ComboBox : ComPort No
        wx.ComboBox(self, 212, value=str(com_Info['Baud']), pos=(x+dt_x*0, y+dt_y*1), size=(120, -1), choices = baudRate_ListStr,    style = wx.CB_READONLY)           # Create a ComboBox : Baud Rate
        wx.ComboBox(self, 213, value=str(com_Info['Data']), pos=(x+dt_x*0, y+dt_y*2), size=(120, -1), choices = dataBit_ListStr,     style = wx.CB_READONLY)           # Create a ComboBox : Data Bit
        wx.ComboBox(self, 214, value=com_Info['Parity'],    pos=(x+dt_x*0, y+dt_y*3), size=(120, -1), choices = parityBit_ListStr,   style = wx.CB_READONLY)           # Create a ComboBox : Parity Bit
        wx.ComboBox(self, 215, value=str(com_Info['Stop']), pos=(x+dt_x*0, y+dt_y*4), size=(120, -1), choices = stopBit_ListStr,     style = wx.CB_READONLY)           # Create a ComboBox : Stop Bit
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_ComPortNo,     id=211)             # Bind an event(EVT_COMBOBOX, id=211) to an event Handler Function(OnSelect_PortNo() Func.)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_BaudRate,      id=212)             # Bind an event(EVT_COMBOBOX, id=212) to an event Handler Function(OnSelect_BaudRate() Func.)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_DataBit,       id=213)             # Bind an event(EVT_COMBOBOX, id=213) to an event Handler Function(OnSelect_DataBit() Func.)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_ParityBit,     id=214)             # Bind an event(EVT_COMBOBOX, id=214) to an event Handler Function(OnSelect_ParityBit() Func.)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_StopBit,       id=215)             # Bind an event(EVT_COMBOBOX, id=215) to an event Handler Function(OnSelect_StopBit() Func.)
        ### Create a Buttons (OK / Cancel / Help)
        x=15
        y=170
        dt_x=70
        dt_y=0
        wx.Button(self, 216, 'OK',      pos=(x + dt_x*0,   y + dt_y*0), size=(60, -1))
        wx.Button(self, 217, 'Cancel',  pos=(x + dt_x*1,   y + dt_y*0), size=(60, -1))
        wx.Button(self, 218, 'Help',    pos=(x + dt_x*2,   y + dt_y*0), size=(60, -1))

        self.Bind(wx.EVT_BUTTON, self.OnOK_Dialog_SerialCfg,      id=216)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnOK_Dialog_SerialCfg() Func.)
        self.Bind(wx.EVT_BUTTON, self.OnCancel_Dialog_SerialCfg,  id=217)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnCancel_Dialog_SerialCfg() Func.)
        self.Bind(wx.EVT_BUTTON, self.OnHelp_Dialog_SerialCfg,    id=218)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnHelp_Dialog_SerialCfg() Func.)
        
        
    def OnOK_Dialog_SerialCfg(self, event):         # Event Callback Function by event(EVT_BUTTON)        
        SerialPortsCfg.SerialPortsCfg_Update()
        
        ##print ('--- serialCfg OK')
        ##print ('com_InfoTmp: ', com_InfoTmp)
        ##print ('com_Info: ', com_Info)
        
        self.Close()                # Frame Close
        
    def OnCancel_Dialog_SerialCfg(self, event):          # Event Callback Function by event (Pressed a No Button)
        SerialPortsCfg.SerialPortsCfg_Restore()
        
        ##print ('--- serialCfg Cancel')
        ##print ('com_InfoTmp: ', com_InfoTmp)
        ##print ('com_Info: ', com_Info)
        
        self.Close()                # Frame Close
        
    def OnHelp_Dialog_SerialCfg(self, event):        # Event Callback Function by event (Pressed a Help Button)
        # reserved.
        self.Close()                # Frame Close
        
    def OnSelect_ComPortNo(self, event):                                # Event Callback Function by event(EVT_COMBOBOX)
        item = event.GetSelection()                                     # Get Items from ComboBox
        #com_InfoTmp['PortNo'] = serialPort_List[item]                  # Shallow Copy
        com_InfoTmp['PortNo'] = copy.deepcopy(serialPort_List[item])    # deep Copy
        ##print ('com_InfoTmp: ', com_InfoTmp)
        
    def OnSelect_BaudRate(self, event):                                 # Event Callback Function by event(EVT_COMBOBOX)
        item = event.GetSelection()                                     # Get Items from ComboBox
        com_InfoTmp['Baud'] = copy.deepcopy(baudRate_List[item])        # deep Copy
        ##print ('com_InfoTmp: ', com_InfoTmp)
        
    def OnSelect_DataBit(self, event):                          # Event Callback Function by event(EVT_COMBOBOX)
        item = event.GetSelection()                             # Get Items from ComboBox
        com_InfoTmp['Data'] = copy.deepcopy(dataBit_List[item]) # deep Copy
        ##print ('com_InfoTmp: ', com_InfoTmp)
        
    def OnSelect_ParityBit(self, event):                                # Event Callback Function by event(EVT_COMBOBOX)
        item = event.GetSelection()                                     # Get Items from ComboBox
        com_InfoTmp['Parity'] = copy.deepcopy(parityBit_List[item])     # deep Copy
        ##print ('com_InfoTmp: ', com_InfoTmp)
        
    def OnSelect_StopBit(self, event):                              # Event Callback Function by event(EVT_COMBOBOX)
        item = event.GetSelection()                                 # Get Items from ComboBox
        com_InfoTmp['Stop'] = copy.deepcopy(stopBit_List[item])     # deep Copy
        ##print ('com_InfoTmp: ', com_InfoTmp)

tcp_ipAddress_Server = [13, 197, 48, 200]
tcp_ipAddress_Client = [13, 197, 48, 100]
tcp_PortNo  = 7000
##print (str(tcp_ipAddress_Server))

class Dialog_TcpNetwork_Config(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title='Tcp Network Configuration.', size=(330, 200))     # Initialize a Dialog
        
        ### config variable init
        
        self.InitGUI_TcpNetworkCfg()
        
    def InitGUI_TcpNetworkCfg(self):
        print ('Tcp Network Configuration')
        
        ### Fonts
        font_Sub = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        
        txtStatic = wx.StaticText(self, -1, 'IP Address(Server)',   pos=(20,  15), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No1
        txtStatic = wx.StaticText(self, -1, 'IP Address(Client)',   pos=(20,  45), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No1
        txtStatic = wx.StaticText(self, -1, 'Port Number',          pos=(20,  75), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No1
        self.txtCtrl_IpAddr_Server = wx.TextCtrl(self, -1, str(tcp_ipAddress_Server),   pos=(150,  10), size=(130, 20));        self.txtCtrl_IpAddr_Server.SetFont(font_Txt)            # User Data Send - No1 : Editor
        self.txtCtrl_IpAddr_Client = wx.TextCtrl(self, -1, str(tcp_ipAddress_Client),   pos=(150,  40), size=(130, 20));        self.txtCtrl_IpAddr_Client.SetFont(font_Txt)            # User Data Send - No1 : Editor
        self.txtCtrl_PortNumber    = wx.TextCtrl(self, -1, str(tcp_PortNo),             pos=(150,  70), size=(130, 20));        self.txtCtrl_PortNumber.SetFont(font_Txt)            # User Data Send - No1 : Editor
        
        ### Create a Buttons (OK / Cancel / Help)
        x=50
        y=110
        dt_x=70
        dt_y=0
        wx.Button(self, 221, 'OK',      pos=(x + dt_x*0,   y + dt_y*0), size=(60, -1))
        wx.Button(self, 222, 'Cancel',  pos=(x + dt_x*1,   y + dt_y*0), size=(60, -1))
        wx.Button(self, 223, 'Help',    pos=(x + dt_x*2,   y + dt_y*0), size=(60, -1))

        self.Bind(wx.EVT_BUTTON, self.OnOK_Dialog_TcpNetCfg,      id=221)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnOK_Dialog_TcpNetCfg() Func.)
        self.Bind(wx.EVT_BUTTON, self.OnCancel_Dialog_TcpNetCfg,  id=222)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnCancel_Dialog_TcpNetCfg() Func.)
        self.Bind(wx.EVT_BUTTON, self.OnHelp_Dialog_TcpNetCfg,    id=223)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnHelp_Dialog_TcpNetCfg() Func.)
        
        
    def OnOK_Dialog_TcpNetCfg(self, event):         # Event Callback Function by event(EVT_BUTTON)        
        print ('Tcp Net : Pushed OK.')
        
        self.Close()                # Frame Close
        
    def OnCancel_Dialog_TcpNetCfg(self, event):          # Event Callback Function by event (Pressed a No Button)
        print ('Tcp Net : Pushed Cancel.')
        
        self.Close()                # Frame Close
        
    def OnHelp_Dialog_TcpNetCfg(self, event):        # Event Callback Function by event (Pressed a Help Button)
        # reserved.
        self.Close()                # Frame Close
        
        
        

class Dialog_SaveMenu_Config(wx.Dialog):
    
    def __init__(self, parent, id, title):
        #super(Dialog_SaveMenu_Config, self).__init__(self, parent, id, title='Save Menu...', size=(350, 180))     # Initialize a Dialog
        wx.Dialog.__init__(self, parent, id, title='Save Menu...', size=(350, 180))     # Initialize a Dialog
        
        ### config variable init
        self.InitGUI_SaveMenuCfg()
        
    def InitGUI_SaveMenuCfg(self):

        ### Fonts
        font_Sub = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        
        ### Setting a Lay-out Text : System configuration
        ##currPath = os.getcwd()
        ##print (currPath)
        ##txtPath = '..\\'      ## Upper Path
        ##txtPath = '.\\'       ## Current Path
        ##txtPath = 'c:\\RaspiSim\\Log_Data\\' ## Absolute Path
        txtDirName = 'Log_Data'
        ##txtPath += txtDirName
        
        txtStatic               = wx.StaticText(self, -1, 'Save Path:',     pos=( 15,   30), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Sub)                 # Save Path:
        txtStatic               = wx.StaticText(self, -1, 'Save Name:',     pos=( 15,   60), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Sub)                 # Save Name:
        self.txtCtrl_savePath   = wx.TextCtrl(  self, -1, txtDirName,       pos=(90,  25),   size=(230, 20));           self.txtCtrl_savePath.SetFont(font_Txt)     # Text : Save Path
        self.txtCtrl_saveName   = wx.TextCtrl(  self, -1, 'Unknown',        pos=(90,  55),   size=(230, 20));           self.txtCtrl_saveName.SetFont(font_Txt)     # Text : Save Name
        
        ### Create a Buttons (OK / Cancel / Help)
        wx.Button(self, 230, 'OK',      pos=(100, 90), size=(60, -1))
        wx.Button(self, 231, 'Cancel',  pos=(180, 90), size=(60, -1))

        self.Bind(wx.EVT_BUTTON, self.OnOK_Dialog_SaveMenuCfg,      id=230)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnOK_Dialog_SerialCfg() Func.)
        self.Bind(wx.EVT_BUTTON, self.OnCancel_Dialog_SaveMenuCfg,  id=231)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnCancel_Dialog_SerialCfg() Func.)
        
        
    def OnOK_Dialog_SaveMenuCfg(self, event):         # Event Callback Function by event(EVT_BUTTON)
        global dataLog, devInfo
        
        ##txtFileName = 'test1'
        ##txtDirPath = self.txtCtrl_savePath.LabelText
        txtDirPath = '.\\'       ## Current Path
        txtDirName = self.txtCtrl_savePath.GetValue()
        if (os.path.exists(txtDirPath + txtDirName) == False):
            os.makedirs(txtDirName)

        txtDirPath += txtDirName + '\\'
        
        ##txtFileName = self.txtCtrl_saveName.LabelText
        txtFileName = self.txtCtrl_saveName.GetValue()
        txtFileType = 'txt'
        txtFile_All = txtDirPath + txtFileName + '.' + txtFileType
        f = open(txtFile_All, 'w')
        
        logHead = '### RaspiSim Log Data ###'
        logHead += '\n' * 2 + 'Log File Name: ' + '\t' + txtFile_All                   + '\n' * 1
        logHead += '\n' * 0 + 'LogSave Time: '  + '\t' + str(datetime.datetime.now())  + '\n' * 2
        
        ##logDeviceInfo  = '\n' * 1  + '[Device Information]' + '\n' * 1
        ##logDeviceInfo += '\n' * 0  + ' Product: '       + '\t' +    devInfo['Product']  +     '\n' * 1
        ##logDeviceInfo += '\n' * 0  + ' Version: '       + '\t' +    devInfo['Version']  +     '\n' * 1
        ##logDeviceInfo += '\n' * 0  + ' Serial No: '     + '\t' +    devInfo['SerialNo'] +     '\n' * 1
        
        ##dataLogTitle = '\n' * 1 + 'No\tTime Stamp\tDir\tRaw Data(Hex)'
        
        ##f.write(logHead + logDeviceInfo + dataLogTitle + dataLog)        
        f.write(logHead + dataLog)        
        
        f.close()
        self.Close()                # Frame Close
        
    def OnCancel_Dialog_SaveMenuCfg(self, event):          # Event Callback Function by event (Pressed a No Button)
        
        self.Close()                # Frame Close
        
        
        
class Dialog_Help_About(wx.Dialog):
    
    def __init__(self, parent, id, title):
        #super(Dialog_Help_About, self).__init__(self, parent, id, title='Help About...', size=(350, 180))     # Initialize a Dialog
        wx.Dialog.__init__(self, parent, id, title='Help About...', size=(350, 190))    # Initialize a Dialog
        
        ### config variable init
        self.InitGUI_HelpAbout()
        
    def InitGUI_HelpAbout(self):
        global verMajor, verMinor, verPatch, buildDate
        
        ### Build Date
        ##dateNow     = datetime.datetime.now()
        ##buildDate   = str(dateNow.year) + '/' + str(dateNow.month) + '/' + str(dateNow.day)
        ##buildDate   = str(2017) + '/' + str(9) + '/' + str(12)
        
        ### Fonts
        font_Title   = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,    underline=False)
        font_Sub     = wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,  underline=False)
        font_Txt     = wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,  underline=False)
        font_Comment = wx.Font( 6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,  underline=False)
        
        ### String...
        txtTitle        = 'RaspiSim'
        txtDescription  = 'Simulator for Raspberry PI Application Program'
        txtVersion      = 'Ver ' + str(verMajor) + '.' + str(verMinor) + '.' + str(verPatch)
        txtBuildDate    = 'Built on ' + buildDate
        txtAuthor       = 'JeonHS'
        txtOwner        = 'Copyright (C) by xxx Co,Ltd. All rights reserved.'
        txtEmail        = 'Email: rsv@rsv.com'

        txtStatic = wx.StaticText(self, -1, txtTitle,       pos=(135,  15), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Title)
        txtStatic = wx.StaticText(self, -1, txtDescription, pos=( 25,  40), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Sub)
        txtStatic = wx.StaticText(self, -1, txtVersion,     pos=( 25,  60), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Sub)
        txtStatic = wx.StaticText(self, -1, txtBuildDate,   pos=( 95,  60), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Sub)
        ##txtStatic = wx.StaticText(self, -1, txtAuthor,      pos=(295,  83), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Comment)
        txtStatic = wx.StaticText(self, -1, txtOwner,       pos=( 25,  80), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Txt)
        txtStatic = wx.StaticText(self, -1, txtEmail,       pos=( 25, 100), style=wx.ALIGN_CENTRE);    txtStatic.SetFont(font_Txt)
        
        ### Create a Buttons (OK)
        wx.Button(self, 921, 'OK',      pos=(140, 120), size=(60, -1))

        self.Bind(wx.EVT_BUTTON, self.OnOK_Dialog_HelpAbout,      id=921)            # Bind an event(EVT_BUTTON) to an event Handler Function(OnOK_Dialog_SerialCfg() Func.)
        
        
    def OnOK_Dialog_HelpAbout(self, event):         # Event Callback Function by event(EVT_BUTTON)
        self.Close()                # Frame Close
        
TX_STS_WAIT         = 0
TX_STS_ACK_WAIT     = 1
TX_STS_SEND_MSG     = 2
TX_STS_FAIL         = 3
TX_STS_SEND_SYNC    = 4

RX_STS_WAIT_HEAD    = 0
RX_STS_WAIT_LENGTH  = 1
RX_STS_WAIT_DATA    = 2
RX_STS_WAIT_SEQ     = 3
RX_STS_WAIT_SYNC    = 4

#####
DL_SEQ_IDLE                 = 0
DL_SEQ_ACK_WAIT             = 1
DL_SEQ_SYNC                 = 2     ## 0x16, 0x7F, 0x16
DL_SEQ_INIT_REQ_WAIT        = 3     ## 0x86
DL_SEQ_INIT_ACK             = 4     ## 0x87
DL_SEQ_DC_STS_UPDATE_WAIT   = 5     ## 0x41
DL_SEQ_SYS_CAP_UPDATE       = 6     ## 0x00
DL_SEQ_ACK                  = 9

DL_SEQ_DEV_CAP_ALL_REQ           = 10    ## 0x01, 0x00
DL_SEQ_DEV_CAP_FDC_REQ           = 11    ## 0x01, 0x01
DL_SEQ_DEV_CAP_INSRC_REQ         = 12    ## 0x01, 0x02
DL_SEQ_DEV_CAP_FDC_UPDATE_WAIT   = 13    ## 0x02, 0x01
DL_SEQ_DEV_CAP_INSRC_UPDATE_WAIT = 14    ## 0x02, 0x02
DL_SEQ_DEV_CAP_COMPLETE_WAIT     = 15    ## 0x02, 0xFF

DL_SEQ_DC_MODE_CHANGE       = 20    ## 0x48
DL_SEQ_DC_MODE_UPDATE_WAIT  = 21    ## 0x45
DL_SEQ_DC_STS_UPDATE_WAIT   = 23    ## 0x41

DL_SEQ_SW_LOAD_SET_SPEED    = 50    ## 0xEF
DL_SEQ_BLOCK_ENTER          = 51    ## 0xC4
DL_SEQ_BLOCK_READY_WAIT     = 52    ## 0xC7
DL_SEQ_BLOCK_START          = 53    ## 0xC0
DL_SEQ_BLOCK_SEG_SIZE_WAIT  = 54    ## 0xC8
DL_SEQ_BLOCK_REQ_WAIT       = 55    ## 0xC1
DL_SEQ_BLOCK_DATA_TRIGGER   = 56    ## 0xC2
DL_SEQ_BLOCK_DATA_MULTI_1   = 57    ## 0xC2
DL_SEQ_BLOCK_DATA_MULTI_2   = 58    ## 0xC2
DL_SEQ_BLOCK_DATA_MULTI_3   = 59    ## 0xC2
DL_SEQ_BLOCK_STS_UPDATE     = 60    ## 0xC6
DL_SEQ_BLOCK_COMPLETE       = 61    ## 0xC9
DL_SEQ_BLOCK_DATA_EMPTY     = 99    ## Internal

DL_SEQ_INIT_COMPLETE            = 250   ## 0x82     by DC Mode Update: 0x45, 0x001(Invalid)
DL_SEQ_INIT_COMPLETE_NORMAL     = 251   ## 0x82     by DC Mode Update: 0x45, 0x01(Normal Mode)
DL_SEQ_INIT_COMPLETE_DIAG_C     = 252   ## 0x82     by DC Mode Update: 0x45, 0x02(Custom Diag Mode)
DL_SEQ_INIT_COMPLETE_DIAG_S     = 253   ## 0x82     by DC Mode Update: 0x45, 0x03(Service Diag Mode)
DL_SEQ_INIT_COMPLETE_DOWNLOAD   = 254   ## 0x82     by DC Mode Update: 0x45, 0x04(SW Download Mode)

##### Instruction Code (Command ID)
ACK_CTRL            = 0xFF      ## Received ACK (for Internal Control)
INIT_REQ            = 0x86
INIT_ACK            = 0x87
DC_STS_UPDATE       = 0x41
SYS_CAP_UPDATE      = 0x00
DEV_CAP_ALL_REQ     = 0x01     ## 0x01, 0x00
DEV_CAP_ALL_UPDATE_WAIT  = 0x02
DEV_CAP_COMPLETE    = 0x02     ## 0x02, 0xFF
DC_MODE_CHANGE      = 0x48
DC_MODE_UPDATE      = 0x45
INIT_COMPLETE       = 0x82
DEV_STS_UPDATE      = 0xE1
DEV_CAP_REQ         = 0x01    ## 0x01, 0x0x(0x00: All,    0x01: FDC,    0x02: Input Src)
DEV_CAP_UPDATE      = 0x02    ## 0x02, 0x0x(0x00: rsv,    0x01: FDC,    0x02: Input Src,    0xFF: Complete)
POLL_REQ            = 0x88

SW_LOAD_SET_SPEED    = 0xEF
BLOCK_ENTER          = 0xC4
BLOCK_READY          = 0xC7
BLOCK_START          = 0xC0
BLOCK_SEG_SIZE       = 0xC8
BLOCK_REQ            = 0xC1
BLOCK_DATA           = 0xC2
BLOCK_STS_UPDATE     = 0xC6
BLOCK_COMPLETE       = 0xC9




class CommPacket():
    def __init__(self, parent, bufSize=128):
        self.parent = parent
        self.bufSize = bufSize

        self.Initialize_CommPacketCtrl()
    
    def Initialize_CommPacketCtrl(self):
        self.txBuf = []
        self.rxBuf = []
        ##for i in range(self.bufSize):
        ##    self.txBuf.append(0)
        ##    self.rxBuf.append(0)

        ## Create a Obj
        self.rxPacket = []
        self.longMsgEn = 0      ## Long Message Enable
        self.multiMsgEn = 0     ## Multi Message Enable
        
        self.txSts = TX_STS_WAIT
        self.rxSts = RX_STS_WAIT_HEAD
        self.txSeq = 0
        self.rxSeq = 0
        self.rxDataLen = 0
        self.rxDataCnt = 0
        self.rxCheckSum = 0

        self.dlSeq_Ctrl = DL_SEQ_IDLE
        
    def SendPar_Sync(self):
        ##buf = [0x16, 0x7F, 0x16]
        buf = []
        buf.append(0x16)
        buf.append(0x7F)
        buf.append(0x16)
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        self.Initialize_CommPacketCtrl()
        
        try:
            ser.write(buf)
            self.txSts = TX_STS_SEND_SYNC
            self.rxSts = RX_STS_WAIT_SYNC
            
        except:
            buf = []
            ##print (len(buf))
        
        return buf
    
    def SendPar_Ack(self):
        ##buf = [0x16, 0x7F, 0x16]
        buf = []
        ##buf.append(0x06 + seqBit*128)
        buf.append(0x06 + self.rxSeq*128)
        self.rxSeq = not self.rxSeq

        try:
            ser.write(buf)
        except:
            buf = []
            ##print (len(buf))
        
        return buf

    def SendPar_Packet(self, dataBuf):
        ## packet Format = [ Head, Length, cmd, D1, D2, ... Dn, checkSum ]
        length = len(dataBuf)
        buf = []
        
        ### Idx 0: Head
        if(length >= 0x40):     buf.append(0xE0)     ## Multi Msg
        else:                   buf.append(0xF0)     ## Long Msg
        checkSum = buf[0]

        ### Idx 1: Length
        buf.append(length)
        checkSum += buf[1]
        

        ### idx 2: Instruction Code (Command) 
        ### idx Dn: User Data
        for idx in range(length):
            buf.append(dataBuf[idx])
            checkSum += dataBuf[idx]

        checkSum = int(checkSum % 128) + (self.txSeq * 128)
        buf.append(checkSum)
        
        try:
            ser.write(buf)
        except:
            buf = []
            ##print (len(buf))

        ##print ('SendPar Packet:', buf)  ## for Debug
        return buf


        
    def Send_cmdPwrOn(self):
        #txBuf = [0x35, 0x01, 0x55, 0xAA, 0x30, 0xFF, 20, 2]    ### 0xA: Line Feed, 0xD: Carriage return
        #ser.write(txBuf)
        buf = [POLL_REQ]
        packet = self.SendPar_Packet(buf)

        return packet
        
    def Send_cmdFeedStart(self):
        buf = [POLL_REQ]
        packet = self.SendPar_Packet(buf)
        
        return packet
    
    def Send_userPacket(self, txBuf):
        buf = []
        for idx in range(len(txBuf)):
            buf.append(txBuf[idx])
        
        try:
            ser.write(buf)
        except:
            buf = []
        
        return buf
    
    def Rcv_readBuf(self): 
        ##if ser.isOpen() == False : return
        ##if ( not (ser.readable()) ): return (0)

        try:
            dataSize = ser.inWaiting()
        except:
            return (0)
        
        ##rawBuf = []
        ##self.rxBuf  = []
        ##if (dataSize > 0):
            ##print ('ser.inWaiting() Before:', ser.inWaiting())
            ##for idx in range(dataSize):
            ##    ##rawBuf += ser.read()
            ##    self.rxBuf += ser.read()
            ##self.rxBuf += ser.read(dataSize)
                
            ##print ('rawBuf:', rawBuf)
            ##self.rxBuf = copy.deepcopy(rawBuf)
            ##print('RxPacket:', self.rxBuf)
            ##RaspiSim_Frame.printCommLog_Control('Rx', self.rxBuf)     # Comm Log Display. typeError
            ##print ('ser.inWaiting() After:', ser.inWaiting())

        self.rxBuf += ser.read(dataSize)
           
        ##return len(self.rxBuf)
        return dataSize
     
    def Rcv_parsingPacket(self):
        ##self.rxPacket = []
        ret = False
        
        self.rxBufSize = len(self.rxBuf)
        if(self.rxBufSize > 0):
        
            self.parsingSts = 0     # 0: parsing Head,   1: parsing Data,   2: parsing Done,   3: parsing Remain
            self.parsingCnt = 0
            ##print ('rxBufSize:', self.rxBufSize, self.rxBuf, ' <-- by Rcv_parsingPacket()')
            for idx in range(self.rxBufSize):
                ##if(idx == 0): print('parsing rxBuf:', self.rxBuf, 'txSts:', self.txSts, 'rxSts:', self.rxSts)
                data = self.rxBuf.pop(0)
                ##print('parsing rxBuf:', self.rxBuf, 'data:', data, 'txSts:', self.txSts)
                
                ##if (self.txSts == TX_STS_SEND_SYNC or self.rxSts == RX_STS_WAIT_SYNC):  ## Wait Sync
                if (self.rxSts == RX_STS_WAIT_SYNC):  ## Wait Sync
                    if (data == 0x06):
                        self.txSts = TX_STS_WAIT
                        self.rxSts = RX_STS_WAIT_HEAD

                        self.txSeq = 0
                        self.rxSeq = 0

                        self.longMsgEn = 0     ## Long Message Enable
                        self.multiMsgEn = 0     ## Multi Message Enable
                        
                        self.rxPacket.append(data)
                        ret = True
                        break
                        
                elif (self.rxSts == RX_STS_WAIT_HEAD):      ## Parsing Head
                    if(data == 0xF0 or data == 0xE0):
                        if(self.multiMsgEn == 0):
                            self.rxPacket.clear()
                            self.rxPacket.append(data)
                            if(data == 0xE0):   self.multiMsgEn = 1
                            
                        if(data == 0xF0):   self.multiMsgEn = 0
                        self.rxDataLen = 0
                        self.rxDataCnt = 0
                        self.rxCheckSum = data
                        self.rxSts = RX_STS_WAIT_LENGTH
                    elif(data == 0x06 or data == 0x86):     ## Parsing Ack
                        self.rxPacket.append(data)
                        ##self.txSeq = int( (self.txSeq + 1) % 2 )
                        self.txSeq = not self.txSeq
                        ##print ('txSeq:', self.txSeq)
                        ret = True
                        break
                        
                elif (self.rxSts == RX_STS_WAIT_LENGTH):    ## Parsing Length
                    self.rxPacket.append(data)
                    self.rxDataLen = data
                    self.rxDataCnt = 0
                    self.rxCheckSum += data
                    self.rxSts = RX_STS_WAIT_DATA
                    
                elif (self.rxSts == RX_STS_WAIT_DATA):      ## Parsing Data
                    self.rxPacket.append(data)
                    self.rxDataCnt += 1
                    self.rxCheckSum += data
                    if(self.rxDataLen <= self.rxDataCnt):
                        self.rxSts = RX_STS_WAIT_SEQ
                elif (self.rxSts == RX_STS_WAIT_SEQ):       ## Parsing Checksum
                    self.rxPacket.append(data)
                    
                    checkSum = int(self.rxCheckSum % 128)
                    ##print ('checkSum:', checkSum)
                    if (checkSum == data):
                        seqBit = int(data / 128)
                        ##print ('checkSum OK:', checkSum, ', seqBit:', seqBit)

                        ##self.SendPar_Ack(seqBit)
                        ##if (self.rxSeq == seqBit):
                        ##    self.rxSeq = not self.rxSeq
                            
                    self.rxSts = RX_STS_WAIT_HEAD
                    if(self.multiMsgEn == 0):
                        ret = True
                        break
        
        ##print('parsing rxPacket:', self.rxPacket, ', txSts:', self.txSts, ', rxSts:', self.rxSts)
        ##print ('parsing rxPacket:', self.rxPacket, ', rxSts:', self.rxSts, datetime.datetime.now(), ', ret:', ret)
        
        return ret
    
    def Rcv_packetClear(self):
        ## Variable Initialize
        ##del rxPacket[:]
        ##print ('parsingCnt:', self.parsingCnt)
        ##for i in range(self.parsingCnt):
        ##    dummy = self.rxPacket.pop(0)
            
        ## Variable Initialize
        self.rxPacket = []
        self.parsingSts = 0
        self.parsingCnt = 0

##fileOpen = open('.\\DownLoad_File\\DL_Img.bin', 'r+b')     ## r+ : Read or over Write Mode,     w+ : Read or new Write Mode,   a+ : Read or File Add Mode,   options(t: text Mode, b: Binary Mode)
##rdImg = fileOpen.read()


SYS_CTRL_MODE_IDLE          = 0     ## SetUp

##### Serial Control
SYS_CTRL_MODE_DEV_IDLE      = 0x10
SYS_CTRL_MODE_DEV_NORMAL    = 0x11
SYS_CTRL_MODE_DEV_START     = 0x12
SYS_CTRL_MODE_DEV_DOWNLOAD  = 0x13
SYS_CTRL_MODE_DEV_RSV_0x04  = 0x14     ## Dev rsv
SYS_CTRL_MODE_DEV_RSV_0x05  = 0x15
## ...
SYS_CTRL_MODE_DEV_RSV_0x0F  = 0x1F     ## Dev rsv

##### TCP IP Control
SYS_CTRL_MODE_TCPNET_IDLE       = 0x20
SYS_CTRL_MODE_TCPNET_RSV_0x01   = 0x21
## ...
SYS_CTRL_MODE_TCPNET_RSV_0x0F   = 0x2F

##### Web Server Control
SYS_CTRL_MODE_WEBSERVER_IDLE        = 0x30
SYS_CTRL_MODE_WEBSERVER_RSV_0x01    = 0x31
## ...
SYS_CTRL_MODE_WEBSERVER_RSV_0x0F    = 0x3F




class RaspiSim_Frame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(800, 600))
        self.panel = wx.Panel(self, -1, (0, 0), (800, 600), style=wx.DEFAULT_FRAME_STYLE)  # Create a Panel
        panel = self.panel

        self.dlSeq_Ctrl = DL_SEQ_IDLE
        self.dlSeq_Pre  = DL_SEQ_IDLE
        self.dlSeq_Next = DL_SEQ_IDLE
        self.dlBlockCnt = 0x50
        self.sysCtrlMode = SYS_CTRL_MODE_IDLE    ## 0: SYS_CTRL_MODE_IDLE,   1: DevCtrl Normal,   2: DevCtrl Start,   3: DevCtrl Download,   4~9: DevCtrl rsv,   10: TcpNet_rsv00,   11: TcpNet_rsv01
        
        self.InitGUI_Frame(panel)

        self.commPacket = CommPacket(self)
        
        self.swTimer_Init()
        
    def InitGUI_Frame(self, panel):
        #panel = wx.Panel(self, -1)  # Create a Panel
        ### reserved Menu Bar(File)  event id : 1xx
        ### reserved Menu Bar(SetUp) event id : 2xx
        ### reserved Menu Bar(Help)  event id : 9xx
        ### reserved LayOut-SysCfg   event id : 3xx
        ### reserved LayOut-DevCtrl  event id : 4xx
        ### reserved LayOut-UserCtrl event id : 5xx
        ### reserved LayOut-CommLog  event id : 6xx
        ### reserved System Control  event id : 7xx

        #   ####### Setting a Menu Bar ######
        menuBar = wx.MenuBar()                                                              # Create a MenuBar Obj
        #
        # Setting a Menu : file Menu for SerialPort
        file    = wx.Menu()                                                                 # Create a menu obj : file
        file.AppendSeparator()                                                              # Added Separator of menu
        #file.Append(110, "&Open ", "Open a new document")                                    # Added menu : file /Open (id=110)
        file.Append(120, "&Save", "Save the document")                                      # Added menu : file /Save (id=120)
        file.AppendSeparator()                                                              # Added Separator of menu
        quit = wx.MenuItem(file, 190, '&Quit\tCtrl+Q', 'Quit the Application')              # Added menu : quit (id=190)
        #quit.SetBitmap(wx.Image('icons/texit.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap())  # Added a Bitmap Icons for quit menu        <-- Dropped by release(*.exe) build Error
        file.Append(quit)                                                                   # Added menu : file /quit obj
        menuBar.Append(file, '&File')                                                       # Added file menu to the menuBar Obj
        #
        # Setting a Menu : setup Menu for SerialPort
        setup           = wx.Menu()                                                         # Create a menu obj : setup
        setup.AppendSeparator()                                                             # Added Separator of menu
        setup_submenu   = wx.Menu()                                                         # Create a menu obj : submenu
        setup_submenu.Append(241, 'rsv Item1', kind=wx.ITEM_RADIO)                          # Added sub Menu : setup /rsv setup3 /item1 (id=241)    <-- in used Radio Button Type
        setup_submenu.Append(242, 'rsv Item2', kind=wx.ITEM_RADIO)                          # Added sub Menu : setup /rsv setup3 /item2 (id=242)    <-- in used Radio Button Type
        setup_submenu.Append(243, 'rsv Item3', kind=wx.ITEM_RADIO)                          # Added sub Menu : setup /rsv setup3 /item3 (id=243)    <-- in used Radio Button Type
        ##serialCfg = wx.MenuItem(setup, 210, 'Serial Port...', 'Serial Port Configuration')  # Added menu : setup /SerialPort (id=210)
        ##setup.Append(serialCfg)
        setup.Append(210, 'Serial Port...', 'Serial Port Configuration')                    # Added menu : setup /SerialPort (id=210)
        setup.Append(220, 'TCP Network',    'TCP Network Configuration')                    # Added menu : setup /TCP Network (id=220)
        setup.AppendSeparator()                                                             # Added Separator of menu
        setup.Append(230, 'rsv setup2', 'rsv comments', kind=wx.ITEM_CHECK)                 # Added menu : setup /rsv setup2 (id=230)               <-- in used Check Box Type
        setup.Append(240, 'rsv setup3', setup_submenu)                                      # Added menu : setup /rsv setup3  (id=240)              <-- in used sub menu
        menuBar.Append(setup, '&SetUp')                                                     # Added a setup menu to the menuBar Obj
        #
        # Setting a Menu : help Menu
        help    = wx.Menu()                                                                 # Create a MenuBar obj for help menu
        ##help.Append(910, "&Help",       "Help...")                                          # Added menu : Help /Help  (id=910)
        help.AppendSeparator()                                                              # Added Separator of menu
        help.Append(920, "&About...",   "About RaspiSim...")                                  # Added menu : Help /About (id=990)
        menuBar.Append(help, '&Help')                                                       # Added a help menu to the menuBar Obj
        #
        self.SetMenuBar(menuBar)                                                            # Setting a menuBar Obj
        
        
        ### Setting a etc...
        self.Centre()                   # Frame align : Center
        self.CreateStatusBar()          # Create a Status Bar
        

        #### Setting a Layout
        self.InitGUI_LayoutSysCfg(panel)
        self.InitGUI_LayoutDevCtrl(panel)
        self.InitGUI_LayoutUserCtrl(panel)
        self.InitGUI_LayoutCommLog(panel)
        
       
        ### Linking a Event Function & Menu ID
        self.Bind(wx.EVT_MENU, self.OnSave, id=120)                 # Bind an event(EVT_MENU, id=120) to an event Handler Function(OnSave() Func.)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=190)                 # Bind an event(EVT_MENU, id=190) to an event Handler Function(OnQuit() Func.)
        self.Bind(wx.EVT_MENU, self.OnSerialPortConfig, id=210)     # Bind an event(EVT_MENU, id=210) to an event Handler Function(OnSerialPortConfig() Func.)
        self.Bind(wx.EVT_MENU, self.OnTcpNetworkConfig, id=220)     # Bind an event(EVT_MENU, id=220) to an event Handler Function(OnTcpNetworkConfig() Func.)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=920)            # Bind an event(EVT_MENU, id=920) to an event Handler Function(OnHelpAbout() Func.)
       
    def OnSave(self, event):                                        # Event Callback Function by event(EVT_MENU, id=120)
        dia = Dialog_SaveMenu_Config(self, -1, '')                  # Create a Dialog
        val = dia.ShowModal()                                       # Show a Modal of Dialog
        dia.Destroy()                                               # Destroy Dialog
        
    def OnQuit(self, event):                                        # Event Callback Function by event(EVT_MENU, id=190)
        self.Close()
        
    def OnSerialPortConfig(self, event):                            # Event Callback Function by event(EVT_MENU, id=210)
        dia = Dialog_SerialPort_Config(self, -1, '')                # Create a Dialog
        val = dia.ShowModal()                                       # Show a Modal of Dialog
        dia.Destroy()                                               # Destroy Dialog

    def OnTcpNetworkConfig(self, event):                            # Event Callback Function by event(EVT_MENU, id=220)
        dia = Dialog_TcpNetwork_Config(self, -1, '')                # Create a Dialog
        val = dia.ShowModal()                                       # Show a Modal of Dialog
        dia.Destroy()                                               # Destroy Dialog

    def OnHelpAbout(self, event):                                   # Event Callback Function by event(EVT_MENU, id=920)
        dia = Dialog_Help_About(self, -1, '')                       # Create a Dialog
        val = dia.ShowModal()                                       # Show a Modal of Dialog
        dia.Destroy()                                               # Destroy Dialog
        
        
    ###
    def InitGUI_LayoutSysCfg(self, panel):
        #panel = wx.Panel(self, -1)  # Create a Panel

        ### Fonts
        font_Title   = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,   underline=True)
        font_Sub     = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt     = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Comment = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        txt_comInfo = '(' + com_Info['PortNo']+'/'+str(com_Info['Baud'])+'/'+str(com_Info['Data'])+'/'+str(com_Info['Parity'])+'/'+str(com_Info['Stop'])+')'    # string - (COMx/38400/8/N/1)
        
        ### Setting a Lay-out Text : System configuration
        txtStatic = wx.StaticText(panel, -1, 'Serial',                          pos=( 15,   5), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)               # Serial
        txtStatic = wx.StaticText(panel, -1, 'Device Information',              pos=(160,   5), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)               # Device Information
        txtStatic = wx.StaticText(panel, -1, 'Communication Status',            pos=(350,   5), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)               # Communication Status
        self.txtCtrl_serComments = wx.StaticText(panel, -1, txt_comInfo,        pos=( 20,  28), style=wx.ALIGN_CENTRE);     self.txtCtrl_serComments.SetFont(font_Comment)   # Serial - Comments (COMx/38400/8/N/1)
        txtStatic = wx.StaticText(panel, -1, 'Product:',                        pos=(165,  35), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Device Information - Product
        txtStatic = wx.StaticText(panel, -1, 'Version:',                        pos=(165,  60), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Device Information - Version
        txtStatic = wx.StaticText(panel, -1, 'Serial No:',                      pos=(165,  85), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Device Information - Serial No
        self.txtCtrl_product    = wx.TextCtrl(panel, -1, devInfo['Product'],    pos=(220,  30), size=(80, 20));                         self.txtCtrl_product.SetFont(font_Txt)      # Device Information - Product : Editor
        self.txtCtrl_version    = wx.TextCtrl(panel, -1, devInfo['Version'] ,   pos=(220,  55), size=(80, 20));                         self.txtCtrl_version.SetFont(font_Txt)      # Device Information - Version : Editor
        self.txtCtrl_serialNo   = wx.TextCtrl(panel, -1, devInfo['SerialNo'],   pos=(220,  80), size=(80, 20));                         self.txtCtrl_serialNo.SetFont(font_Txt)     # Device Information - Serial No : Editor
        self.txtCtrl_CommSts    = wx.TextCtrl(panel, -1, 'msg_CommSts...',      pos=(350,  30), size=(180, 70), style=wx.TE_MULTILINE); self.txtCtrl_CommSts.SetFont(font_Txt)      # Communication Status - msg_CommSts
        self.ButtonConnect      = wx.Button(panel, 310,  'Connect',             pos=( 20,  45), size=(90, 50));                         self.Bind(wx.EVT_BUTTON, self.OnConnect, id=310)    # Bind an event(EVT_BUTTON) to an event Handler Function(OnConnect() Func.)
        
        self.ButtonConnect.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,   underline=False))
        self.ButtonConnect.SetForegroundColour('Red')
        ##self.ButtonConnect.SetBackgroundColour('Red')
        
    
        ### Setting a Lay-out Line : Communication Log
        #self.Line_SysCfgTopSer = wx.StaticLine(panel, -1,      pos=( 10,  15), size=(110,  2));                    # Create a Static Line
        self.Line_SysCfgTop     = wx.StaticLine(panel, -1,      pos=( 10,  15), size=(525,  2));                    # Create a Static Line
        self.Line_SysCfgLeft    = wx.StaticLine(panel, -1,      pos=( 10,  15), size=(  2, 90));                    # Create a Static Line
        self.Line_SysCfgRight   = wx.StaticLine(panel, -1,      pos=(535,  15), size=(  2, 90));                    # Create a Static Line
        self.Line_SysCfgCol1    = wx.StaticLine(panel, -1,      pos=(130,  15), size=(  2, 90));                    # Create a Static Line
        self.Line_SysCfgCol2    = wx.StaticLine(panel, -1,      pos=(320,  15), size=(  2, 90));                    # Create a Static Line
        self.Line_SysCfgBottom  = wx.StaticLine(panel, -1,      pos=( 10, 105), size=(525,  2));                    # Create a Static Line
        
    def OnConnect(self, event):         # Event Callback Function by event(EVT_BUTTON, id=200)
        global com_Info, com_InfoTmp

        ## Up-Date Serial Comments label
        self.txtCtrl_serComments.Label = '(' + com_Info['PortNo']+'/'+str(com_Info['Baud'])+'/'+str(com_Info['Data'])+'/'+str(com_Info['Parity'])+'/'+str(com_Info['Stop'])+')'    # string - (COMx/38400/8/N/1)
        
        ##print ('button Label: ', self.ButtonConnect.Label)
        txt_connect = self.ButtonConnect.Label
        
        if txt_connect == 'Connect' :
            conSts = SerialPortsCfg.SerialPortsCfg_Connect()            # Serial Port Open
            if (conSts == True):
                self.sysCtrlMode = SYS_CTRL_MODE_DEV_IDLE
                
                self.ButtonConnect.LabelText = 'DisConnect'
                ##print ('--- Connect:', ser)
            
                self.ButtonConnect.SetForegroundColour('Blue')
                ##self.ButtonConnect.SetBackgroundColour('Blue')
        else :
            conSts = SerialPortsCfg.SerialPortsCfg_DisConnect()         # Serial Port Close
            if (conSts == True):
                self.sysCtrlMode = SYS_CTRL_MODE_IDLE
                
                self.ButtonConnect.LabelText = 'Connect'
                ##print ('--- DisConnect:', ser)
                
                self.ButtonConnect.SetForegroundColour('Red')
                ##self.ButtonConnect.SetBackgroundColour('Red')
        
        ### Time Delay (Are you need?)
        time.sleep(3/1000)  # [unit: sec]

        ### Timer Start for Receive Data Check
        if ser.isOpen():
            checkTime = 100
            ##checkTime += 1000   ## Added a 1000ms for Debug
            ##self.timerCommCtrl_Rcv_rxBufCheck.StartOnce(10 + checkTime)   # Timer Start [unit: ms]
            ##self.timerCommCtrl_RcvPacketDataPop.Start(checkTime)                              # Timer Start [unit: ms]
        else:
            self.timerCommCtrl_Rcv_rxBufCheck.Stop()
            self.timerCommCtrl_RcvPacketDataPop.Stop()
        
        ### Display a Communication Status
        msgLog = com_Info['PortNo']
        if com_Info['PortNo'] == 'rsv':
            msgLog = 'CommPort Error!'
        else:
            if ser.isOpen() :   msgLog += ' Connected()'
            else:               msgLog += ' Disconnected()'
            
        #self.txtCtrl_CommSts.Label = msgLog
        self.txtCtrl_CommSts.AppendText('\n' + msgLog)
        self.txtCtrl_CommSts.Update()
            
    ###
    def InitGUI_LayoutDevCtrl(self, panel):
        #panel = wx.Panel(self, -1)  # Create a Panel

        ### Fonts
        font_Title   = wx.Font(10, wx.FONTFAMILY_DEFAULT,   wx.FONTSTYLE_NORMAL,    wx.FONTWEIGHT_BOLD,     underline=True)
        font_Sub     = wx.Font( 8, wx.FONTFAMILY_DEFAULT,   wx.FONTSTYLE_NORMAL,    wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt     = wx.Font( 8, wx.FONTFAMILY_DEFAULT,   wx.FONTSTYLE_NORMAL,    wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Msg     = wx.Font( 9, wx.FONTFAMILY_DEFAULT,   wx.FONTSTYLE_NORMAL,    wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Comment = wx.Font( 7, wx.FONTFAMILY_DEFAULT,   wx.FONTSTYLE_NORMAL,    wx.FONTWEIGHT_NORMAL,   underline=False)
 
        ### Setting a Lay-out Text : Device Control
        txtStatic               = wx.StaticText(panel, -1,  'Device Control',   pos=( 15, 115), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)                           # Device Control
        self.ButtonDevPwr       = wx.Button(panel, 410,     'Dev_PWR\nON',      pos=( 20, 145), size=(90, 50));             self.Bind(wx.EVT_BUTTON, self.OnDevPwr,    id=410)     # Bind an event(EVT_BUTTON) to an event Handler Function(OnDevPwr() Func.)
        self.ButtonDevStart     = wx.Button(panel, 420,     'Dev_Start',        pos=(120, 145), size=(90, 50));             self.Bind(wx.EVT_BUTTON, self.OnDevStart,   id=420)     # Bind an event(EVT_BUTTON) to an event Handler Function(OnDevStart() Func.)
        self.ButtonDevDownLoad  = wx.Button(panel, 430,     'Dev_DownLoad',     pos=(220, 145), size=(90, 50));             self.Bind(wx.EVT_BUTTON, self.OnDevDownLoad, id=430);     self.ButtonDevDownLoad.SetForegroundColour('Black')     # Bind an event(EVT_BUTTON) to an event Handler Function(OnDevDownLoad() Func.)
        self.txtCtrl_DevSts     = wx.TextCtrl(panel, -1,    '\nDev Status...',  pos=(320, 145), size=(210, 50), style=wx.TE_CENTER | wx.TE_MULTILINE | wx.TE_NO_VSCROLL);   self.txtCtrl_DevSts.SetFont(font_Msg)   # Device Control - Status

        txtStatic               = wx.StaticText(panel, -1,  'Img Path :',         pos=(255, 130), style=wx.ALIGN_RIGHT);     txtStatic.SetFont(font_Sub);   txtStatic.SetForegroundColour('Gray')   # Device Control
        txtStatic               = wx.StaticText(panel, -1,  'Img Name :',         pos=(255, 195), style=wx.ALIGN_RIGHT);     txtStatic.SetFont(font_Sub);   txtStatic.SetForegroundColour('Gray')   # Device Control
        self.txtCtrl_DL_ImgPath = wx.TextCtrl(  panel, -1,  '.\\DownLoad_File\\', pos=(320, 130), size=(210, 15), style=wx.TE_LEFT);   self.txtCtrl_DL_ImgPath.SetFont(font_Txt);  self.txtCtrl_DL_ImgPath.SetForegroundColour('Gray') # Device Control - Status
        self.txtCtrl_DL_ImgName = wx.TextCtrl(  panel, -1,  'DL_Img.bin',         pos=(320, 195), size=(210, 15), style=wx.TE_LEFT);   self.txtCtrl_DL_ImgName.SetFont(font_Txt);  self.txtCtrl_DL_ImgName.SetForegroundColour('Gray') # Device Control - Status

        ### Setting a Lay-out Line : Device Control
        self.Line_DevCtrlTop     = wx.StaticLine(panel, -1,      pos=( 10, 125), size=(525,  2));                    # Create a Static Line
        self.Line_DevCtrlLeft    = wx.StaticLine(panel, -1,      pos=( 10, 125), size=(  2, 90));                    # Create a Static Line
        self.Line_DevCtrlRight   = wx.StaticLine(panel, -1,      pos=(535, 125), size=(  2, 90));                    # Create a Static Line
        self.Line_DevCtrlBottom  = wx.StaticLine(panel, -1,      pos=( 10, 215), size=(525,  2));                    # Create a Static Line
        
    def OnDevPwr(self, event):         # Event Callback Function by event(EVT_BUTTON, id=410)
        if ser.isOpen():
            txt_DevDownLoad = self.ButtonDevDownLoad.Label
            if (txt_DevDownLoad == 'Dev_DownLoad\nCancel'): return;

            txt_DevPwr = self.ButtonDevPwr.Label
            if (txt_DevPwr == 'Dev_PWR\nOFF'):

                self.ButtonDevPwr.Label = 'Dev_PWR\nON'
                ## reserved...
                ## Down Load Stop
                ## Setting a Button
                self.ButtonDevPwr.SetForegroundColour('Black')
                self.ButtonDevStart.SetForegroundColour('Black')
                self.ButtonDevDownLoad.SetForegroundColour('Black')
                return;

            ## Setting a Button : Button
            self.sysCtrlMode = SYS_CTRL_MODE_DEV_NORMAL
            self.ButtonDevPwr.LabelText = 'Dev_PWR\nOFF'
            self.ButtonDevPwr.SetForegroundColour('Black')
            self.ButtonDevStart.SetForegroundColour('Black')
            self.ButtonDevDownLoad.SetForegroundColour('Gray')
            
            ##### Sending a Power On Packet
            packet = self.commPacket.Send_cmdPwrOn()            # Send to Power On Command
            
            packetSize = len(packet)
            if (packetSize > 0):
                ##### Setting a time out Function
                ##txDlyTime = int((1000 * 11 * packetSize) / com_Info['Baud'] + 0.5)
                ##txDlyTime += 1000*100   ## Added a 1000ms for Debug
                ##self.timerCommCtrl_RcvInitTimeOut.StartOnce(1000 + txDlyTime)   # Timer Start [unit: ms]
                ##self.printCommLog_Control('Tx', packet)                         # Comm Log Display
                
                ## Setting a txt Font & Color : DevSts
                txtTag = 'Device PWR [Power On] Request'       # 'DevPwr Request'
                txtColour = ['Black', 'White']
                
            else:
                ## Setting a txt Font & Color : DevSts
                txtTag = 'Comm Packet NG!'
                txtColour = ['Red', 'White']
                
        else:
            ## Setting a txt Font & Color : DevSts
            txtTag = 'Serial Port Error!'
            txtColour = ['Red', 'White']

        ### Display a Device Status
        self.txtCtrl_DevSts_UpDate(txtTag, txtColour)

    def txtCtrl_DevSts_UpDate(self, txtTag, txtColour):
        ### Display a Device Status
        self.txtCtrl_DevSts.SetForegroundColour(txtColour[0])   ## Text Color
        self.txtCtrl_DevSts.SetBackgroundColour(txtColour[1])   ## Background Color
        self.txtCtrl_DevSts.Label = ''                  # Label text Clear
        self.txtCtrl_DevSts.AppendText('\n' + txtTag)        
        self.txtCtrl_DevSts.Update()
            
    def OnDevStart(self, event):         # Event Callback Function by event(EVT_BUTTON, id=420)
        if ser.isOpen():
            txt_DevDownLoad = self.ButtonDevDownLoad.Label
            if (txt_DevDownLoad == 'Dev_DownLoad\nCancel'): return;

            self.sysCtrlMode = SYS_CTRL_MODE_DEV_START
            
            packet = self.commPacket.Send_cmdFeedStart()    # Send to Power On Command
            
            packetSize = len(packet)
            if (packetSize > 0):
                ##### Setting a time out Function
                txDlyTime = int((1000 * 11 * packetSize) / com_Info['Baud'] + 0.5)
                ##txDlyTime += 1000*100   ## Added a 1000ms for Debug
                self.timerCommCtrl_RcvAckTimeOut.StartOnce(40 + 30 + txDlyTime)    # Timer Start [unit: ms]
                
                ##### Display a Packet Data
                self.printCommLog_Control('Tx', packet)         # Comm Log Display
                
                ### Display a Device Status
                msg = 'Device Start Request'
                txtColour = ['Black', 'White']
                
            else:
                ### Display a Device Status
                msg = 'Comm Packet NG!'
                txtColour = ['Red', 'White']
            
        else:
            ### Display a Device Status
            msg = 'Serial Port Error!'
            txtColour = ['Red', 'White']

        ### Display a Device Status
        self.txtCtrl_DevSts_UpDate(msg, txtColour)
            
            
    def OnDevDownLoad(self, event):         # Event Callback Function by event(EVT_BUTTON, id=410)
        global dataLog

        if (not ser.isOpen()):
            ### Display a Device Status
            txtTag = 'Serial Port Error!'
            txtColour = ['Red', 'White']
            self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
            return
        
        txt_DevPwr = self.ButtonDevPwr.Label
        if (txt_DevPwr == 'Dev_PWR\nOFF'): return;

        txt_DevDownLoad = self.ButtonDevDownLoad.Label
        if (txt_DevDownLoad == 'Dev_DownLoad\nCancel'):
            self.ButtonDevDownLoad.Label = 'Dev_DownLoad'

            ## Down Load Control Timer Stop
            self.timerCommCtrl_Rcv_rxBufCheck.Stop()
            self.timerCommCtrl_RcvPacketDataPop.Stop()
            self.timerCommCtrl_RcvAckTimeOut.Stop()         # Timer Start [unit: ms]
            self.timerCommCtrl_RcvInitTimeOut.Stop()        # Timer Start [unit: ms]
            self.timerCommCtrl_RcvDataTimeOut.Stop()        # Timer Start [unit: ms]

            
            ## Setting a Button
            self.ButtonDevPwr.SetForegroundColour('Black')
            self.ButtonDevStart.SetForegroundColour('Black')
            self.ButtonDevDownLoad.SetForegroundColour('Black')
            return;
        
        ## Setting a Button
        self.sysCtrlMode = SYS_CTRL_MODE_DEV_DOWNLOAD
        self.ButtonDevDownLoad.Label = 'Dev_DownLoad\nCancel'
        self.ButtonDevPwr.SetForegroundColour('Gray')
        self.ButtonDevStart.SetForegroundColour('Gray')
        self.ButtonDevDownLoad.SetForegroundColour('Black')


        ##### Loading a Download Image
        checkSts = self.DownLoadCtrl_ImgFileLoad()
        if(checkSts == 1):    ## file Check Status : 0: File Type(*.bin) Error,   1: File Type OK & File Open OK,   2: File Open Error
            self.DownLoadCtrl_Init()            ## Setting a DL_SEQ_SYNC
            self.DownLoadCtrl_SendPacket()      ## Send a Sync
            ##self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_START )    ## Added a for Debug
            
            ##self.timerCommCtrl_Rcv_rxBufCheck.StartOnce(20)   # Timer Start [unit: ms]

        ### Display a Device Status
        if(  checkSts == 0): txtTag = 'Down Load File Type(*.bin) Error!'   ## 0: File Type(*.bin) Error
        elif(checkSts == 1): txtTag = 'Down Load File OK!'                  ## 1: File Type OK & File Open OK, 
        elif(checkSts == 2): txtTag = 'Down Load File Open Error!'          ## 2: File Open Error
        else:                txtTag = 'Down Load Ctrl Logic Error!'          ##  rsv
        if(checkSts == 1):  txtColour = ['Black', 'White']
        else:               txtColour = ['Red', 'White']
        
        ### Display a Device Status
        self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
        
        return      ## for Debug : No Display a Analyze Data & No Save a Data Log 
        
        ## Communication Load Rate Initialize
        if (self.txtCtrl_CommLog_LoadRate > 0) : self.txtCtrl_CommLog_LoadRate = 0

        msgLog = '\n' * 1       ## for Seperate Line
        self.txtCtrl_CommLog.AppendText(msgLog)
        self.txtCtrl_CommLog_Analyze.AppendText(msgLog)
        
        ####### Save a Data Log
        msgLog = '-' * 64 + '\n' * 1
        dataLog += copy.deepcopy(msgLog)     ### Save a Message Log
        
    def DownLoadCtrl_ImgFileLoad(self):
        ##global rdImg
        if (self.sysCtrlMode != SYS_CTRL_MODE_DEV_DOWNLOAD): return
        
        checkSts = 0     ## file Check Status : 0: File Type(*.bin) Error,   1: File Type OK & File Open OK,   2: File Open Error
        
        ##txtFileName = 'test1'
        ##txtDirPath = self.txtCtrl_savePath.LabelText
        ##txtDirPath = '.\\'       ## Current Path
        txtDirPath = ''
        txtDirName = txtDirPath + self.txtCtrl_DL_ImgPath.GetValue()
        ##print('txtDirNam:', txtDirPath)
        if (os.path.exists(txtDirName) == False):
            os.makedirs(txtDirName)
        
        ##txtFileName = self.txtCtrl_saveName.LabelText
        txtFileName = self.txtCtrl_DL_ImgName.GetValue()
        txtFileType = 'bin'
        ##txtFileType = 'txt'
        txtFileNameStr = str(txtFileName)
        checkSts = int(txtFileNameStr.endswith(txtFileType))
        ##print ('File Type(*.bin) Status:', checkSts)

        if (checkSts):
            txtFile_All = txtDirName + txtFileName
            ##print ('File All:', txtFile_All)

            try:
                ##f = open(txtFile_All, 'w')
                ##f = open(txtFile_All, 'r+')     ## r+ : Read or over Write Mode,     w+ : Read or new Write Mode
                ##f = open(txtFile_All, 'r+', encoding='UTF8')     ## r+ : Read or over Write Mode,     w+ : Read or new Write Mode,   a+ : Read or File Add Mode,   options(t: text Mode, b: Binary Mode)
                f = open(txtFile_All, 'r+b')     ## r+ : Read or over Write Mode,     w+ : Read or new Write Mode,   a+ : Read or File Add Mode,   options(t: text Mode, b: Binary Mode)
                rd = f.read()
                self.rdImg = rd
                ##print ('fileObj:',      f)
                ##print ('rdObj size:',   len(rd))
                ##print ('rdObj:\n',      rd)
                ##print ('rdObj[:5]:',    rd[:5])
                ##print ('rdObj[:1]:',    rd[:1])
                ##print ('rdObj[3:5]:',   rd[3:5])
                ##print ('rdObj[180:]:',  rd[180:])
                ##f.writelines('test')
                                
                f.close()
                
            except:
                checkSts += 1

        return checkSts


    def Get_DownLoadCtrl_Sts(self):
        return self.dlSeq_Ctrl
    
    ## Download pre Sequence Up-Date
    def DownLoadCtrl_RxSeqAckSet(self, nextSeq):
        ##self.dlSeq_Pre  = self.dlSeq_Ctrl
        self.dlSeq_Ctrl = nextSeq
        
    def DownLoadCtrl_RxSeqUserkSet(self, seqSts):
        ##self.dlSeq_Pre  = self.dlSeq_Ctrl
        self.dlSeq_Ctrl = seqSts

    def DownLoadCtrl_RxSeqSet(self, nextSeq):
        ##self.dlSeq_Pre  = copy.deepcopy(self.dlSeq_Ctrl)
        ##self.dlSeq_Pre  = DL_SEQ_ACK_WAIT
        self.dlSeq_Pre  = self.dlSeq_Ctrl
        self.dlSeq_Ctrl = nextSeq
        
        return (1)

    def DownLoadCtrl_SeqCtrl(self, cmd, para):
        if (self.sysCtrlMode != SYS_CTRL_MODE_DEV_DOWNLOAD): return
        
        currSeq = self.dlSeq_Ctrl
        preSeq = self.dlSeq_Pre
        ##print ('DL Seq Ctrl ( ', 'preSeq:', self.dlSeq_Pre, ', SeqCtrl:', self.dlSeq_Ctrl, ', cmd:', cmd, ', para:', para, ' )')

        refreshCmd = 0
        ## Ack Control
        if(cmd == ACK_CTRL):
            if(  preSeq == DL_SEQ_SYS_CAP_UPDATE):          refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_DEV_CAP_ALL_REQ )
            elif(preSeq == DL_SEQ_DEV_CAP_ALL_REQ):         refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_DEV_CAP_COMPLETE_WAIT )
            elif(preSeq == DL_SEQ_SW_LOAD_SET_SPEED):       refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_ENTER )
            elif(preSeq == DL_SEQ_BLOCK_DATA_MULTI_1):
                if(self.dlBlockSize <= self.dlBlockCnt):    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_EMPTY )
                else:
                    blockDataSize = self.dlBlockSize - self.dlBlockCnt
                    if(blockDataSize > 0x40):               refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_MULTI_2 )
                    else:                                   refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_MULTI_3 )
                    
            elif(preSeq == DL_SEQ_BLOCK_DATA_MULTI_2):      refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_MULTI_3 )
            
        else:
            ##self.DownLoadCtrl_RxSeqAckSet( DL_SEQ_ACK )
            ##self.DownLoadCtrl_SendPacket()
            
            packet = self.commPacket.SendPar_Ack()
            self.DownLoadCtrl_TxSeqAckSet()
            

        ## Command Control
        if(cmd == INIT_REQ):                        refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_ACK )
        
        elif(cmd == DC_STS_UPDATE):
            if(  preSeq == DL_SEQ_INIT_ACK):        refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_SYS_CAP_UPDATE )
            elif(preSeq >= DL_SEQ_INIT_COMPLETE):   refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_SW_LOAD_SET_SPEED )
            
        elif(cmd == DEV_CAP_UPDATE):                ## 0x02, 0x00(0x00: rsv,    0x01: FDC,    0x02: Input Src,    0xFF: Complete)
            if(para == 0xFF):                       refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_DC_MODE_CHANGE )
            
        elif(cmd == DC_MODE_UPDATE):
            if(preSeq == DL_SEQ_DC_MODE_CHANGE):    ## 0x45, 0x00(0: Invalid,   1: Normal,   2: Custom Diag,   3: Service Diag,   4: SW Download,   etc: reserved)
                if(  para == 0):                    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE )
                elif(para == 1):                    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_NORMAL )
                elif(para == 2):                    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_DIAG_C )
                elif(para == 3):                    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_DIAG_S )
                elif(para == 4):                    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_DOWNLOAD )
                else:                               refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE )
                
            elif(preSeq == DL_SEQ_INIT_ACK):        refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_DOWNLOAD )
            refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_INIT_COMPLETE_DOWNLOAD )

        elif(cmd == BLOCK_READY):
            ##if(  preSeq == DL_SEQ_BLOCK_ENTER):             refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_START )
            refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_START )
            
        elif(cmd == BLOCK_SEG_SIZE):
            rxData   = self.commPacket.rxPacket
            dataSize = len(rxData)
            if(dataSize > 8):   self.dlBlockPacketSize = rxData[8]
            self.DownLoadCtrl_RxSeqUserkSet( DL_SEQ_BLOCK_REQ_WAIT )
            
        elif(cmd == BLOCK_REQ):
            if(  preSeq == DL_SEQ_BLOCK_START):             refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_TRIGGER ) ## 1st :  8byte Block Data
            elif(preSeq == DL_SEQ_BLOCK_DATA_TRIGGER or 
                 ##preSeq == DL_SEQ_BLOCK_DATA_MULTI_1 or       ## Control by ACK
                 ##preSeq == DL_SEQ_BLOCK_DATA_MULTI_2 or       ## Control by ACK
                 preSeq == DL_SEQ_BLOCK_DATA_MULTI_3 ):
                 if(self.dlBlockSize > self.dlBlockCnt):    refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_MULTI_1 )
                 else:                                      refreshCmd = self.DownLoadCtrl_RxSeqSet( DL_SEQ_BLOCK_DATA_EMPTY )
                 
        ##elif(cmd == BLOCK_STS_UPDATE):  ## reserved...
        ##elif(cmd == BLOCK_COMPLETE):    ## reserved...

        ## Packet Send by Seq Change
        if(refreshCmd == 1):
            self.DownLoadCtrl_SendPacket()


    def DownLoadCtrl_TxSeqAckSet(self):
        ##self.dlSeq_Pre  = copy.deepcopy(self.dlSeq_Ctrl)
        self.dlSeq_Ctrl  = self.dlSeq_Pre
        ##self.dlSeq_Pre = DL_SEQ_ACK_WAIT      ## dlSeq_Pre is not change.
        
    def DownLoadCtrl_TxSeqUserSet(self, seqSts):
        self.dlSeq_Ctrl  = seqSts
        
    def DownLoadCtrl_TxSeqSet(self):
        ##self.dlSeq_Pre  = copy.deepcopy(self.dlSeq_Ctrl)
        self.dlSeq_Pre  = self.dlSeq_Ctrl
        self.dlSeq_Ctrl = DL_SEQ_ACK_WAIT
        
    def DownLoadCtrl_Init(self):
        self.dlSeq_Ctrl = DL_SEQ_SYNC
        self.dlSeq_Pre  = DL_SEQ_IDLE
        self.dlSeq_Next = DL_SEQ_IDLE
        self.dlBlockCnt = 0x50
        self.dlBlockPacketSize = 0x80
        self.dlBlockSize = 0

    def DownLoadCtrl_SendPacket(self):
        global com_Info
        ##global rdImg
        
        imgObj = self.rdImg        
        ##print ('imgObj:', imgObj)

        ##if (not ser.isOpen()):
        ##    ### Display a Device Status
        ##    txtTag = 'Serial Port Error!'
        ##    txtColour = ['Red', 'White']
        ##    self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
        ##    return

        ##dlSeq_Curr = self.dlSeq_Ctrl
        dlSeq_Curr = self.Get_DownLoadCtrl_Sts()
        ##dlSeq_Curr = DL_SEQ_IDLE
        if (dlSeq_Curr == DL_SEQ_IDLE):
            ##print ('DL Sequence IDLE')
            return;
        
        packet = []
        flashSizeStr = 0x00030400
        if(dlSeq_Curr == DL_SEQ_SYNC):
            packet = self.commPacket.SendPar_Sync()
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_ACK):
            packet = self.commPacket.SendPar_Ack()
            self.DownLoadCtrl_TxSeqAckSet()
                
        elif(dlSeq_Curr == DL_SEQ_INIT_ACK):
            buf = [INIT_ACK]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_SYS_CAP_UPDATE):
            productCode = 0x03  ## 0:Teak/Parma, 1:Chamonix, 2:Wenge, 3:Phin, 4:Matt, 15:Other
            buf = [SYS_CAP_UPDATE, 0x00, 0x00, 0x00, 0x00, 0x00, productCode]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_DEV_CAP_ALL_REQ):
            reqPara = 0x00  ## All Request
            buf = [DEV_CAP_REQ, reqPara, 0x00, 0x00]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_DEV_CAP_FDC_REQ):
            reqPara = 0x01  ## FDC Request
            buf = [DEV_CAP_REQ, reqPara, 0x00, 0x00]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_DEV_CAP_INSRC_REQ):
            reqPara = 0x02  ## Input Source Request
            buf = [DEV_CAP_REQ, reqPara, 0x00, 0x00]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_DC_MODE_CHANGE):
            buf = [DC_MODE_CHANGE, 0x04]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr >= DL_SEQ_INIT_COMPLETE):
            buf = [INIT_COMPLETE]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_SW_LOAD_SET_SPEED):
            ## 9.6K(0x0001),   19.2K(0x0002),   38.4K(0x0020),   56k(0x0080),   115.2K(0x8000)
            speedUpper = 0x00
            speedLower = 0x02
            buf = [SW_LOAD_SET_SPEED, 0x02, 0x00, 0x00, speedUpper, speedLower]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()

        elif(dlSeq_Curr == DL_SEQ_BLOCK_ENTER):
            buf = [BLOCK_ENTER, 0x02, 0x00, 0x00, 0x00]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()

        elif(dlSeq_Curr == DL_SEQ_BLOCK_START):
            buf = [BLOCK_START, 0x02, 0x00, 0x00, 0x00, 0x03, 0x04, 0x00]
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
            self.dlBlockSize = len(imgObj)
            ##print ('imgObj Size:', self.dlBlockSize)
            
        elif(dlSeq_Curr == DL_SEQ_BLOCK_DATA_TRIGGER):
            ## Packet Format : BLOCK DATA(0xC2) [ Cmd,     Target,     Instance,     Module,     Length2,     Length1,     Length0,     D1, D2, ... Dn ]
            length = [0x00, 0x00, 0x08]
            buf = [BLOCK_DATA, 0x02, 0x00, 0x00, length[0], length[1], length[2]]
            dataSize = length[0]*65536 + length[1]*256 + length[2]
                
            ## Checking a Data Size
            blockDataSize = self.dlBlockSize - self.dlBlockCnt
            if(dataSize > blockDataSize):   dataSize = blockDataSize

            ##buf.append(imgObj[self.dlBlockCnt:dataSize])
            blockDataSize = self.dlBlockSize - self.dlBlockCnt
            if(dataSize > blockDataSize):   dataSize = blockDataSize
            for idx in range(dataSize):
                buf.append(imgObj[self.dlBlockCnt+idx])
            self.dlBlockCnt += dataSize
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_BLOCK_DATA_MULTI_1):
            ## Packet Format : BLOCK DATA(0xC2) [ Cmd,     Target,     Instance,     Module,     Length2,     Length1,     Length0,     D1, D2, ... Dn ]
            length = [0x00, 0x00, 0x80]
            buf = [BLOCK_DATA, 0x02, 0x00, 0x00, length[0], length[1], length[2]]
            dataSize = 0x40 - len(buf)      ## 0x40 - 7 = 57
            
            ## Checking a Data Size
            blockDataSize = self.dlBlockSize - self.dlBlockCnt
            if(dataSize > blockDataSize):   dataSize = blockDataSize

            ##buf.append(imgObj[self.dlBlockCnt:dataSize])
            ##buf += imgObj[self.dlBlockCnt:dataSize]
            for idx in range(dataSize):
                buf.append(imgObj[self.dlBlockCnt+idx])
            self.dlBlockCnt += dataSize
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()

            ##print ('BLK M1:', datetime.datetime.now())

        elif(dlSeq_Curr == DL_SEQ_BLOCK_DATA_MULTI_2):
            ## Packet Format : BLOCK DATA(0xC2) [ Cmd,     Target,     Instance,     Module,     Length2,     Length1,     Length0,     D1, D2, ... Dn ]
            buf = []
            dataSize = 0x40                 ## 0x40
                
            ## Checking a Data Size
            blockDataSize = self.dlBlockSize - self.dlBlockCnt
            if(dataSize > blockDataSize):   dataSize = blockDataSize
                
            ##buf.append(imgObj[self.dlBlockCnt:dataSize])
            for idx in range(dataSize):
                buf.append(imgObj[self.dlBlockCnt+idx])
            self.dlBlockCnt += dataSize
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
        elif(dlSeq_Curr == DL_SEQ_BLOCK_DATA_MULTI_3):
            buf = []
            dataSize = 0x07                 ## 0x07     <-- Remainder Multi-Packet Data : 0x80 = ~_MULTI_1(0x40-7) + ~_MULTI_2(0x40) + ~_MULTI_3(0x07)
                
            ## Checking a Data Size
            blockDataSize = self.dlBlockSize - self.dlBlockCnt
            if(dataSize > blockDataSize):   dataSize = blockDataSize
                
            ##buf.append(imgObj[self.dlBlockCnt:dataSize])
            for idx in range(dataSize):
                buf.append(imgObj[self.dlBlockCnt+idx])
            self.dlBlockCnt += dataSize
            packet = self.commPacket.SendPar_Packet(buf)
            self.DownLoadCtrl_TxSeqSet()
            
            ##print ('BLK M3:', datetime.datetime.now())

        elif(dlSeq_Curr == DL_SEQ_BLOCK_DATA_EMPTY):
            ####### Save a Data Log
            buf = [0xFF, 99]                             ## packet for Internal Control : Block Data Empty
            self.printCommLog_Control('Inner', buf)      ## Comm Log Display

        packetSize = len(packet)
        if (packetSize > 0):
        
            ##### Setting a time out Function
            txDlyTime = int((1000 * 11 * packetSize) / com_Info['Baud'] + 0.5)
            txDlyTime += 0   ## Added a 1000ms for Debug
            self.timerCommCtrl_Rcv_rxBufCheck.StartOnce(6 + txDlyTime)   # Timer Start [unit: ms]

            ##print ('dlSeq_Ctrl:', self.dlSeq_Ctrl, 'dlSeq_Pre:', self.dlSeq_Pre)      ## for Debug

            ##### Setting a time out Function
            ##txDlyTime = int((1000 * 11 * packetSize) / com_Info['Baud'] + 0.5)
            ##txDlyTime += 1000*100   ## Added a 1000ms for Debug
            ##self.timerCommCtrl_RcvAckTimeOut.StartOnce(40 + 30 + txDlyTime)    # Timer Start [unit: ms]

            ##### Display a Packet Data
            ##print('txPacket:', packet)
            self.printCommLog_Control('Tx', packet)         # Comm Log Display
                            
            ## Setting a txt Font & Color : DevSts
            txtTag = 'Par Send Data Size: ' + str(packetSize)
            txtColour = ['Black', 'White']

        else:
            ## Setting a txt Font & Color : DevSts
            txtTag = 'Par Send Packet NG!'
            txtColour = ['Red', 'White']
            
            
        ### Display a Device Status
        self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
        
        
        
    ###
    def InitGUI_LayoutUserCtrl(self, panel):
        #panel = wx.Panel(self, -1)  # Create a Panel

        ### Fonts
        font_Title   = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,     underline=True)
        font_Sub     = wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt     = wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Comment = wx.Font( 7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        
        ### Setting a Lay-out Text : User Control
        txtStatic = wx.StaticText(panel, -1, 'User Data Send(Hex)',     pos=(570,   5), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)               # User Data Send (type: Hex)
        txtStatic = wx.StaticText(panel, -1, 'No1',                     pos=(575,  35), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No1
        txtStatic = wx.StaticText(panel, -1, 'No2',                     pos=(575,  60), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No2
        txtStatic = wx.StaticText(panel, -1, 'No3',                     pos=(575,  85), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No3
        txtStatic = wx.StaticText(panel, -1, 'No4',                     pos=(575, 110), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No4
        txtStatic = wx.StaticText(panel, -1, 'No5',                     pos=(575, 135), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No5
        txtStatic = wx.StaticText(panel, -1, 'No6',                     pos=(575, 160), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No5
        ##txtStatic = wx.StaticText(panel, -1, 'ms',                      pos=(785,  45), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No1 Delay Time Unit [ms]
        ##txtStatic = wx.StaticText(panel, -1, 'ms',                      pos=(785,  70), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No2 Delay Time Unit [ms]
        ##txtStatic = wx.StaticText(panel, -1, 'ms',                      pos=(785,  95), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No3 Delay Time Unit [ms]
        ##txtStatic = wx.StaticText(panel, -1, 'ms',                      pos=(785, 120), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - No4 Delay Time Unit [ms]
        ##txtStatic = wx.StaticText(panel, -1, 'cnt',                     pos=(785, 145), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # User Data Send - Repeat Count Unit [cnt]
        self.txtCtrl_Send1      = wx.TextCtrl(panel, -1, 'AA 11',       pos=(600,  30), size=(90, 20));        self.txtCtrl_Send1.SetFont(font_Txt)            # User Data Send - No1 : Editor
        self.txtCtrl_Send2      = wx.TextCtrl(panel, -1, 'AA 22',       pos=(600,  55), size=(90, 20));        self.txtCtrl_Send2.SetFont(font_Txt)            # User Data Send - No2 : Editor
        self.txtCtrl_Send3      = wx.TextCtrl(panel, -1, 'AA 33',       pos=(600,  80), size=(90, 20));        self.txtCtrl_Send3.SetFont(font_Txt)            # User Data Send - No3 : Editor
        self.txtCtrl_Send4      = wx.TextCtrl(panel, -1, 'AA 44',       pos=(600, 105), size=(90, 20));        self.txtCtrl_Send4.SetFont(font_Txt)            # User Data Send - No4 : Editor
        self.txtCtrl_Send5      = wx.TextCtrl(panel, -1, 'AA 55',       pos=(600, 130), size=(90, 20));        self.txtCtrl_Send5.SetFont(font_Txt)            # User Data Send - No5 : Editor
        self.txtCtrl_Send6      = wx.TextCtrl(panel, -1, 'AA 66',       pos=(600, 155), size=(90, 20));        self.txtCtrl_Send6.SetFont(font_Txt)            # User Data Send - No6 : Editor
        ##self.txtCtrl_Send1_DlyT = wx.TextCtrl(panel, -1, '0',           pos=(740,  40), size=(40, 20),  style=wx.ALIGN_RIGHT);  self.txtCtrl_Send1_DlyT.SetFont(font_Txt)       # User Data Send - No1 Delay Time : Editor
        ##self.txtCtrl_Send2_DlyT = wx.TextCtrl(panel, -1, '0',           pos=(740,  65), size=(40, 20),  style=wx.ALIGN_RIGHT);  self.txtCtrl_Send2_DlyT.SetFont(font_Txt)       # User Data Send - No2 Delay Time : Editor
        ##self.txtCtrl_Send3_DlyT = wx.TextCtrl(panel, -1, '0',           pos=(740,  90), size=(40, 20),  style=wx.ALIGN_RIGHT);  self.txtCtrl_Send3_DlyT.SetFont(font_Txt)       # User Data Send - No3 Delay Time : Editor
        ##self.txtCtrl_Send4_DlyT = wx.TextCtrl(panel, -1, '0',           pos=(740, 115), size=(40, 20),  style=wx.ALIGN_RIGHT);  self.txtCtrl_Send4_DlyT.SetFont(font_Txt)       # User Data Send - No4 Delay Time : Editor
        ##self.txtCtrl_RepeatCnt  = wx.TextCtrl(panel, -1, '0',           pos=(740, 140), size=(40, 20),  style=wx.ALIGN_RIGHT);  self.txtCtrl_RepeatCnt.SetFont(font_Txt)        # User Data Send - Repeat Counter : Editor
        self.ButtonUserSend1    = wx.Button(panel, 510, 'Send1',        pos=(695,  30), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend1,    id=510) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend1() Func.)
        self.ButtonUserSend2    = wx.Button(panel, 520, 'Send2',        pos=(695,  55), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend2,    id=520) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend2() Func.)
        self.ButtonUserSend3    = wx.Button(panel, 530, 'Send3',        pos=(695,  80), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend3,    id=530) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend3() Func.)
        self.ButtonUserSend4    = wx.Button(panel, 540, 'Send4',        pos=(695, 105), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend4,    id=540) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend4() Func.)
        self.ButtonUserSend5    = wx.Button(panel, 550, 'Send5',        pos=(695, 130), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend5,    id=550) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend5() Func.)
        self.ButtonUserSend6    = wx.Button(panel, 560, 'Send6',        pos=(695, 155), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSend6,    id=560) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSend6() Func.)
        self.ButtonUserSendAll  = wx.Button(panel, 590, 'Send All',     pos=(695, 180), size=(65, 20));     self.Bind(wx.EVT_BUTTON, self.OnUserSendAll,  id=590) # Bind an event(EVT_BUTTON) to an event Handler Function(OnUserSendAll() Func.)

        ### Setting a Lay-out Line : User Control
        self.Line_UserCtrlTop     = wx.StaticLine(panel, -1,     pos=(565,  15), size=(200,   2));                    # Create a Static Line
        self.Line_UserCtrlLeft    = wx.StaticLine(panel, -1,     pos=(565,  15), size=(  2, 195));                    # Create a Static Line
        self.Line_UserCtrlRight   = wx.StaticLine(panel, -1,     pos=(765,  15), size=(  2, 195));                    # Create a Static Line
        self.Line_UserCtrlBottom  = wx.StaticLine(panel, -1,     pos=(565, 210), size=(200,   2));                    # Create a Static Line
        
    def Send_UserData(self, idx):
        global com_Info
        
        ##print ('UserSend')
        if ser.isOpen():
            userData = ''
            if   (idx == 1):    userData += self.txtCtrl_Send1.GetValue()
            elif (idx == 2):    userData += self.txtCtrl_Send2.GetValue()
            elif (idx == 3):    userData += self.txtCtrl_Send3.GetValue()
            elif (idx == 4):    userData += self.txtCtrl_Send4.GetValue()
            elif (idx == 5):    userData += self.txtCtrl_Send5.GetValue()
            elif (idx == 6):    userData += self.txtCtrl_Send6.GetValue()
            else:               
                userData += self.txtCtrl_Send1.GetValue() + ' '
                userData += self.txtCtrl_Send2.GetValue() + ' '
                userData += self.txtCtrl_Send3.GetValue() + ' '
                userData += self.txtCtrl_Send4.GetValue() + ' '
                userData += self.txtCtrl_Send5.GetValue() + ' '
                userData += self.txtCtrl_Send6.GetValue() + ' '
            
            data = userData.split()
            ##print (userData)
            ##print (data[0])
            ##print (int(data[0], 16))
            ##print (len(data))

            txBuf = []
            ##txBuf = [0x35, 0x01, 0x55, 0xAA, 0x30, 0xFF, 20, 2]    ### 0xA: Line Feed, 0xD: Carriage return
            for i in range(len(data)):
                txBuf.append(int(data[i], 16))
            ##print ('txBuf:', txBuf)
            packet = self.commPacket.Send_userPacket(txBuf)  # Send to User Data
            
            packetSize = len(packet)
            if (packetSize > 0):
                txDlyTime = int((1000 * 11 * packetSize) / com_Info['Baud'] + 0.5)
                txDlyTime += 1000*100   ## Added a 1000ms for Debug
                ##print('txDlyTime:', txDlyTime)
                self.timerCommCtrl_RcvAckTimeOut.StartOnce(40 + 30 + txDlyTime)    # Timer Start [unit: ms]

                self.printCommLog_Control('Tx', packet)             # Comm Log Display
                
                ## Setting a Font & Color
                txtTag = 'Send a User Data '            # 'User Data Send'
                if (idx > 6):       txtTag += 'All'
                else:               txtTag += str(idx)
                txtColour = ['Black', 'White']

            else:
                ## Setting a Font & Color
                txtTag = 'Comm Packet NG!'
                txtColour = ['Red', 'White']

        else:
            ## Setting a Font & Color
            txtTag = 'Serial Port Error!'
            txtColour = ['Red', 'White']
            
            
        ### Display a Device Status
        self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
        

    def OnUserSend1(self, event):         # Event Callback Function by event(EVT_BUTTON, id=510)
        ##print ('UserSend1')
        self.Send_UserData(1)
    def OnUserSend2(self, event):         # Event Callback Function by event(EVT_BUTTON, id=520)
        ##print ('UserSend2')
        self.Send_UserData(2)
    def OnUserSend3(self, event):         # Event Callback Function by event(EVT_BUTTON, id=530)
        ##print ('UserSend3')
        self.Send_UserData(3)
    def OnUserSend4(self, event):         # Event Callback Function by event(EVT_BUTTON, id=540)
        ##print ('UserSend4')
        self.Send_UserData(4)
    def OnUserSend5(self, event):         # Event Callback Function by event(EVT_BUTTON, id=550)
        ##print ('UserSend5')
        self.Send_UserData(5)
    def OnUserSend6(self, event):         # Event Callback Function by event(EVT_BUTTON, id=560)
        ##print ('UserSend6')
        self.Send_UserData(6)
    def OnUserSendAll(self, event):       # Event Callback Function by event(EVT_BUTTON, id=590)
        ##print ('UserSendAll')
        self.Send_UserData(9)
        
    def InitGUI_LayoutCommLog(self, panel):
        #panel = wx.Panel(self, -1)  # Create a Panel

        ### Fonts
        font_Title   = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,     underline=True)
        font_Sub     = wx.Font( 9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Txt     = wx.Font( 9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        font_Comment = wx.Font( 7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,   underline=False)
        
        ### Setting a Lay-out Text 
        self.ButtonCommLogClear      = wx.Button(panel, 600, 'Clear',         pos=(700, 230), size=(70, 20));   self.Bind(wx.EVT_BUTTON, self.OnCommLogClear,      id=600) # Bind an event(EVT_BUTTON) to an event Handler Function(OnCommLogClear() Func.)
        self.ButtonCommLogVisibleAck = wx.Button(panel, 610, 'InVisible Ack', pos=(600, 230), size=(90, 20));   self.Bind(wx.EVT_BUTTON, self.OnCommLogVisibleAck, id=610) # Bind an event(EVT_BUTTON) to an event Handler Function(OnCommLogAckClear() Func.)
        txtStatic = wx.StaticText(panel, -1, 'Communication Log',   pos=( 15, 225), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Title)               # Communication Log
        txtStatic = wx.StaticText(panel, -1, 'No',                  pos=( 30, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - No
        txtStatic = wx.StaticText(panel, -1, 'Time',                pos=( 95, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Time Stamp
        txtStatic = wx.StaticText(panel, -1, 'Dir',                 pos=(155, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Direction (Source)
        txtStatic = wx.StaticText(panel, -1, 'Raw Data(Hex)',       pos=(260, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Raw Data
        txtStatic = wx.StaticText(panel, -1, 'No',                  pos=(430, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - No
        ##txtStatic = wx.StaticText(panel, -1, 'Time',                pos=(495, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Time Stamp
        ##txtStatic = wx.StaticText(panel, -1, 'Dir',                 pos=(555, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Direction (Source)
        ##txtStatic = wx.StaticText(panel, -1, 'Protocol Analyzer',   pos=(630, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Decription
        txtStatic = wx.StaticText(panel, -1, 'Protocol Analyzer',   pos=(555, 255), style=wx.ALIGN_CENTRE);     txtStatic.SetFont(font_Sub)                 # Communication Log - Decription
        
        ### Setting a Lay-out Text : Communication Log
        self.txtCtrl_CommLog            = wx.TextCtrl(panel, -1, '', pos=( 25+0,   275), size=(400,     230),   style=wx.TE_MULTILINE);   self.txtCtrl_CommLog.SetFont(font_Txt)           # Text Control
        self.txtCtrl_CommLog_Analyze    = wx.TextCtrl(panel, -1, '', pos=( 25+400, 275), size=(740-400, 230),   style=wx.TE_MULTILINE);   self.txtCtrl_CommLog_Analyze.SetFont(font_Txt)   # Text Control
        self.txtCtrl_CommLog_LoadRate   = 0
        self.txtCtrl_CommLog_LoadRate_Ana = 0       ## Not used.
        self.txtCtrl_CommLog_VisibleAck = 0
        
        ### Setting a Lay-out Line : Communication Log
        self.Line_CommLogTop1     = wx.StaticLine(panel, -1,        pos=( 20, 250),     size=(750, 2))      # Create a Static Line
        self.Line_CommLogTop2     = wx.StaticLine(panel, -1,        pos=( 20, 270),     size=(750, 2))      # Create a Static Line
        self.Line_CommLogLeft     = wx.StaticLine(panel, -1,        pos=( 20, 250),     size=(  2, 260))    # Create a Static Line
        self.Line_CommLogRight    = wx.StaticLine(panel, -1,        pos=(770, 250),     size=(  2, 260))    # Create a Static Line
        self.Line_CommLogBottom   = wx.StaticLine(panel, -1,        pos=( 20, 510),     size=(750, 2))      # Create a Static Line
        self.Line_CommLogTopCol1  = wx.StaticLine(panel, -1,        pos=( 70, 250),     size=(  2, 20))     # Create a Static Line
        self.Line_CommLogTopCol2  = wx.StaticLine(panel, -1,        pos=(135, 250),     size=(  2, 20))     # Create a Static Line
        self.Line_CommLogTopCol3  = wx.StaticLine(panel, -1,        pos=(190, 250),     size=(  2, 20))     # Create a Static Line
        self.Line_CommLogTopCol4  = wx.StaticLine(panel, -1,        pos=(405+ 20, 250), size=(  2, 20))     # Create a Static Line
        self.Line_CommLogTopCol5  = wx.StaticLine(panel, -1,        pos=(405+ 70, 250), size=(  2, 20))     # Create a Static Line
        ##self.Line_CommLogTopCol6  = wx.StaticLine(panel, -1,        pos=(405+135, 250), size=(  2, 20))     # Create a Static Line
        ##self.Line_CommLogTopCol7  = wx.StaticLine(panel, -1,        pos=(405+190, 250), size=(  2, 20))     # Create a Static Line

    def OnCommLogClear(self, event):         # Event Callback Function by event(EVT_BUTTON, id=600)
        self.txtCtrl_CommLog.Label = ''             # Label text Clear
        self.txtCtrl_CommLog_Analyze.Label = ''     # Label text Clear

    def OnCommLogVisibleAck(self, event):         # Event Callback Function by event(EVT_BUTTON, id=610)
        txt_DevPwr = self.ButtonDevPwr.Label
        if (txt_DevPwr == 'Dev_PWR\nOFF'): return;

        txt_AckOnOff = self.ButtonCommLogVisibleAck.Label
        if (txt_AckOnOff == 'Visible Ack'):
            self.ButtonCommLogVisibleAck.Label = 'InVisible Ack'
            self.txtCtrl_CommLog_VisibleAck = 0
        else:
            self.ButtonCommLogVisibleAck.Label = 'Visible Ack'
            self.txtCtrl_CommLog_VisibleAck = 1
            
      
    def printCommLog_Control(self, dirTxRx, packet):
        global dataLog, devInfo

        ####### Invisible Ack Message
        pSize = len(packet)
        if(self.txtCtrl_CommLog_VisibleAck == 0):
            if(pSize == 1): return;     ## Invisible Ack
        
        self.txtCtrl_CommLog_LoadRate += 1      # Increase a Load Rate
        
        timeNow = datetime.datetime.now()
        timeNow_ms = int(timeNow.hour*60*60*1000 + timeNow.minute*60*1000 + timeNow.second*1000 + timeNow.microsecond/1000)

        ####### Display Type : Decimal
        ##log_All = txtCtrl_CommLog.AppendText('\n' + msgLog)
        ##for i in range(len(packet)):
        ##    log_All += str(packet[i])
        ##    log_All += ' '
        ##print ("Log format Dec: ", log_All)
        ##self.txtCtrl_CommLog.AppendText('\n'+log_All)
        ##self.txtCtrl_CommLog.Update()
        
        if (self.txtCtrl_CommLog_LoadRate == 1):
            devInfo['Product'] = copy.deepcopy( self.txtCtrl_product.GetValue() )
            devInfo['Version'] = copy.deepcopy( self.txtCtrl_version.GetValue() )
            devInfo['SerialNo']= copy.deepcopy( self.txtCtrl_serialNo.GetValue() )
            
            logDeviceInfo  = '\n' * 1 + '[Device Information]'  + '\n' * 1
            logDeviceInfo += '\n' * 0 + ' Product: '            + '\t' +    devInfo['Product']  +     '\n' * 1
            logDeviceInfo += '\n' * 0 + ' Version: '            + '\t' +    devInfo['Version']  +     '\n' * 1
            logDeviceInfo += '\n' * 0 + ' Serial No: '          + '\t' +    devInfo['SerialNo'] +     '\n' * 1
            
            dataLogTitle   = '\n' * 1 + 'No\tTime Stamp\tDir\tAnalyze Data' +     '\n' * 1
        else :
            logDeviceInfo = ''
            dataLogTitle  = ''
        
        
        ####### Added a Log Tag : No    Time Stamp    Dir    Analyze Data
        log_Tag     = str(self.txtCtrl_CommLog_LoadRate) + '\t' + str(timeNow_ms) + '\t' + dirTxRx + '\t'                   # Log Tag : Time Stamp, Communication Direction(Tx or Rx)
        
        if (dirTxRx == 'Inner'):
            head = packet[0]    ## used internal Control ID             : only 0xFF
            cmd  = packet[1]    ## used internal Control Command    :
            msgAna = 'id(' + str(cmd) + '): '
            if(head == 0xFF):           ## packet for Internal Control
                ## Setting a txt Font & Color : DevSts
                if(cmd == 1):           ## packet for Internal Control : RcvAckTimeOut
                    msgAna += 'Rcv Ack Time Out'
                    txtColour = ['Red', 'White']

                elif(cmd == 2):       ## packet for Internal Control : RcvInitTimeOut
                    msgAna += 'Dev_PWR Check NG'
                    txtColour = ['Red', 'White']

                elif(cmd == 3):     ## packet for Internal Control : RcvDataTimeOut
                    msgAna += 'Receive Data Error'
                    txtColour = ['Red', 'White']

                elif(cmd == 99):     ## packet for Internal Control : Block Data Empty
                    msgAna += 'DownLoad Block Data Empty'
                    txtColour = ['Red', 'White']
                    
                else:
                    msgAna += 'Unknown Cmd'
                    txtColour = ['Black', 'White']
            else:
                msgAna += 'Unknown ID'
                txtColour = ['Black', 'White']
                
            ### Display a Device Status
            self.txtCtrl_DevSts_UpDate(msgAna, txtColour)
        
        else:   ## dirTxRx is 'Tx' or 'Rx'
            ####### Display Raw Data
            ##log_Data    = str.join("", (" 0x%02X" % i for i in packet[:15]))      # Convert to Hex Format
            ##log_Data    = str.join("", (" %02X" % i for i in packet[:15]))          # Convert to Hex Format (missing a 0x)
            ##log_Data    = str.join("", (" %02X" % i for i in packet[:(64+5)]))          # Convert to Hex Format (missing a 0x), packet Size is 69 <-- 0x64(Max Data Size) + 3(Head, Length, CheckSum) + 2(margin)
            ##log_Data    = str.join("", (" %02X" % i for i in packet[:8]))          # Convert to Hex Format (missing a 0x), packet Size is 69 <-- 0x64(Max Data Size) + 3(Head, Length, CheckSum) + 2(margin)
            log_Data    = str.join("", (" %02X" % i for i in packet[:]))          # Convert to Hex Format (missing a 0x), packet Size is 69 <-- 0x64(Max Data Size) + 3(Head, Length, CheckSum) + 2(margin)
            ##print ('Log Format Hex: ', log_Tag, log_Data)
            msgLog = log_Tag + log_Data + '\n' * 1
            self.txtCtrl_CommLog.AppendText(msgLog)
            ##self.txtCtrl_CommLog.Update()

            ##return      ##  for Debug : No Display a Analyze Data & No Save a Data Log
        
            ####### Display Analyze Data
            if(packet[0] == 0x16 and packet[1] == 0x7F and packet[2] == 0x16): msgAna = 'Par Sync'
            else:
                if(pSize > 2):          ## packet Size is 3 over
                    head    = packet[0]
                    length  = packet[1]
                    cmd     = packet[2]

                    if(  cmd == INIT_REQ            ):      msgAna = 'INIT_REQ'
                    elif(cmd == INIT_ACK            ):      msgAna = 'INIT_ACK'
                    elif(cmd == DC_STS_UPDATE       ):      msgAna = 'DC_STS_UPDATE'
                    elif(cmd == SYS_CAP_UPDATE      ):      msgAna = 'SYS_CAP_UPDATE'
                    elif(cmd == DEV_CAP_ALL_REQ     ):      msgAna = 'DEV_CAP_ALL_REQ'      ## 0x01, 0x00
                    elif(cmd == DEV_CAP_ALL_UPDATE_WAIT):   msgAna = 'DEV_CAP_ALL_UPDATE_WAIT'
                    elif(cmd == DEV_CAP_COMPLETE    ):      msgAna = 'DEV_CAP_COMPLETE'     ## 0x02, 0xFF
                    elif(cmd == DC_MODE_CHANGE      ):      msgAna = 'DC_MODE_CHANGE'
                    elif(cmd == DC_MODE_UPDATE      ):      msgAna = 'DC_MODE_UPDATE'
                    elif(cmd == INIT_COMPLETE       ):      msgAna = 'INIT_COMPLETE'
                    elif(cmd == DEV_STS_UPDATE      ):      msgAna = 'DEV_STS_UPDATE'
                    elif(cmd == DEV_CAP_REQ         ):      msgAna = 'DEV_CAP_REQ'          ## 0x01, 0x0x(0x00: All,    0x01: FDC,    0x02: Input Src)
                    elif(cmd == DEV_CAP_UPDATE      ):      msgAna = 'DEV_CAP_UPDATE'       ## 0x02, 0x0x(0x00: rsv,    0x01: FDC,    0x02: Input Src,    0xFF: Complete)
                    elif(cmd == POLL_REQ            ):      msgAna = 'Poll Request'
                    
                    elif(cmd == SW_LOAD_SET_SPEED   ):      msgAna = 'SW_LOAD_SET_SPEED'
                    elif(cmd == BLOCK_ENTER         ):      msgAna = 'BLOCK_ENTER'
                    elif(cmd == BLOCK_READY         ):      msgAna = 'BLOCK_READY'
                    elif(cmd == BLOCK_START         ):      msgAna = 'BLOCK_START'
                    elif(cmd == BLOCK_SEG_SIZE      ):      msgAna = 'BLOCK_SEG_SIZE'
                    elif(cmd == BLOCK_REQ           ):      msgAna = 'BLOCK_REQ'
                    elif(cmd == BLOCK_DATA          ):      msgAna = 'BLOCK_DATA'
                    elif(cmd == BLOCK_STS_UPDATE    ):      msgAna = 'BLOCK_STS_UPDATE'
                    elif(cmd == BLOCK_COMPLETE      ):      msgAna = 'BLOCK_COMPLETE'
                    else                             :      msgAna = 'unknown'
                elif(pSize == 1):       ## packet Size is 1
                    msgAna = 'ACK'
                else:                   ## packet Size is 0 or 2
                    msgAna = 'unknown'

        
        ####### Display Analyze Data
        log_Tag = str(self.txtCtrl_CommLog_LoadRate) + '\t'
        msgLog = log_Tag + msgAna + '\n' * 1
        self.txtCtrl_CommLog_Analyze.AppendText(msgLog)
        self.txtCtrl_CommLog_Analyze.Update()
          
        
        ####### Save a Data Log
        #dataLog += '\n' + self.txtCtrl_CommLog.LabelText        ### NG
        #dataLog += '\n' + copy.deepcopy(self.txtCtrl_CommLog.LabelText)    ### NG
        #dataLog += '\n' + msgLog     ### Save a Message Log
        dataLog += copy.deepcopy(logDeviceInfo + dataLogTitle + msgLog)     ### Save a Message Log
        
    def swTimer_Init(self):
        ### Setting a Event Timer for Rcv Data Check
        self.timerCommCtrl_Rcv_rxBufCheck = wx.Timer(self, id=700)                                          # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_Rcv_rxBufCheck, self.timerCommCtrl_Rcv_rxBufCheck, id=700)    # Setting a Callback Function by Event Timer
        #self.timerCommCtrl_Rcv_rxBufCheck.Start(25)                                                        # Timer Start [unit: ms]
        
        self.timerCommCtrl_RcvAckTimeOut = wx.Timer(self, id=710)                                           # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_RcvAckTimeOut, self.timerCommCtrl_RcvAckTimeOut, id=710)      # Setting a Callback Function by Event Timer
        #self.timerCommCtrl_RcvAckTimeOut.Start(50)                                                        # Timer Start [unit: ms]
        
        self.timerCommCtrl_RcvInitTimeOut = wx.Timer(self, id=720)                                          # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_RcvInitTimeOut, self.timerCommCtrl_RcvInitTimeOut, id=720)    # Setting a Callback Function by Event Timer
        #self.timerCommCtrl_RcvInitTimeOut.Start(250)                                                       # Timer Start [unit: ms]
        
        self.timerCommCtrl_RcvDataTimeOut = wx.Timer(self, id=730)       ## Not used...                                   # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_RcvDataTimeOut, self.timerCommCtrl_RcvDataTimeOut, id=730)    # Setting a Callback Function by Event Timer
        #self.timerCommCtrl_RcvDataTimeOut.Start(10)                                                       # Timer Start [unit: ms]
        
        ### Setting a Event Timer for Sequence Control Rcv Packet Data Check
        self.timerCommCtrl_RcvPacketDataPop = wx.Timer(self, id=740)                                            # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_RcvPacketDataPop, self.timerCommCtrl_RcvPacketDataPop, id=740)    # Setting a Callback Function by Event Timer
        #self.timerCommCtrl_RcvPacketDataPop.Start(25)                                                        # Timer Start [unit: ms]
    
        ### Setting a Event Timer for System Up-Date
        self.timerCommLog_SysUpDate = wx.Timer(self, id=790)                                              # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_SysUpDate, self.timerCommLog_SysUpDate, id=790)             # Setting a Callback Function by Event Timer
        self.timerCommLog_SysUpDate.Start(1000)                                                            # Timer Start [unit: ms]
        
        ### Setting a Event Timer for Working Test
        self.timerCommLog_TimeStamp = wx.Timer(self, id=799)                                         # Setting a Timer
        self.Bind(wx.EVT_TIMER, self.CallBack_CommLog_TimeStamp, self.timerCommLog_TimeStamp, id=799)     # Setting a Callback Function by Event Timer
        ##self.timerCommLog_TimeStamp.Start(3000)                                                      # Timer Start [unit: ms]

    
    def Rcv_packetDataPop(self):
        rxData = []
            
        ##print ('rxPacket:', self.commPacket.rxPacket, 'rxBuf:', self.commPacket.rxBuf)        ## for Debug
        ##rxData = copy.deepcopy(self.commPacket.rxPacket)
        rxData   = self.commPacket.rxPacket
        dataSize = len(rxData)
        
        cmd = ACK_CTRL  ## Received Ack
        para = 0
        if(dataSize > 1):
            if(dataSize > 2):    cmd  = rxData[2]  ## Received Packet: Cmd
            if(dataSize > 3):    para = rxData[3]  ## Received Packet: Para

        ##if(cmd == BLOCK_REQ): print ('BLK REQ:', datetime.datetime.now())

        ##### System Control
        if (self.sysCtrlMode == SYS_CTRL_MODE_DEV_DOWNLOAD):     self.DownLoadCtrl_SeqCtrl(cmd, para)

        ##if (cmd == ACK_CTRL):
        ##    ### Display a Device Status
        ##    txtTag = 'Received ACK'
        ##    txtColour = ['Black', 'White']
        ##    
        ##    ### Display a Device Status
        ##    self.txtCtrl_DevSts_UpDate(txtTag, txtColour)
                    
        self.printCommLog_Control('Rx:', self.commPacket.rxPacket)  ## Display Comm Log for Receive Packet Data

        ##self.timerCommCtrl_RcvDataTimeOut.Stop()        # Timer Start [unit: ms]
        self.commPacket.Rcv_packetClear()

        return (len(self.commPacket.rxBuf))     ## Remained rx Data

    
    def CallBack_Rcv_rxBufCheck(self, event):          # Event Callback Function by event(EVT_TIMER, id=700.)
        rdDataSize = self.commPacket.Rcv_readBuf()
        
        if(self.commPacket.Rcv_parsingPacket()):        ## Received Data Parsing( rxBuf -> rxPacket) ok?
            ##### Received Data Packet Control
            self.Rcv_packetDataPop()

        
        self.timerCommCtrl_Rcv_rxBufCheck.StartOnce(10)   # Timer Start [unit: ms]
        ##print ('rx Period', datetime.datetime.now())
        
        ##if (rdDataSize > 0):
            ##self.timerCommCtrl_RcvAckTimeOut.Stop()         # Timer Start [unit: ms]
            ##self.timerCommCtrl_RcvInitTimeOut.Stop()        # Timer Start [unit: ms]
            
            ##packet_MaxSize = 256    ## maximmum packet Size
            ##rxPacketMaxDlyTime = int((1000 * 11 * packet_MaxSize) / com_Info['Baud'] + 0.5)        ## 73.833 (<-- 38.4kbps)
            ####rxPacketMaxDlyTime += 1000*100   ## Added a 1000ms for Debug
            ####print('rxPacketMaxDlyTime:', rxPacketMaxDlyTime)
            
            ##self.timerCommCtrl_RcvDataTimeOut.StartOnce(50 + 50 + rxPacketMaxDlyTime)                                                       # Timer Start [unit: ms]
            ##self.printCommLog_Control('Rx:', self.commPacket.rxBuf)         # Comm Log Display
                

    def CallBack_RcvAckTimeOut(self, event):           # Event Callback Function by event(EVT_TIMER, id=710.)
        global dataLog

        self.commPacket.Rcv_packetClear()

        ####### Save a Data Log
        packet = [0xFF, 1]                              ## packet for Internal Control : RcvAckTimeOut
        self.printCommLog_Control('Inner', packet)      ## CoprintCommLog_Control    
        
    def CallBack_RcvInitTimeOut(self, event):           # Event Callback Function by event(EVT_TIMER, id=720.)
        global dataLog
        
        self.commPacket.Rcv_packetClear()
        
        ####### Save a Data Log
        packet = [0xFF, 2]                              ## packet for Internal Control : RcvInitTmeOut
        self.printCommLog_Control('Inner', packet)      ## Comm Log Display
        
    def CallBack_RcvDataTimeOut(self, event):           # Event Callback Function by event(EVT_TIMER, id=730.)
        global dataLog

        self.commPacket.Rcv_packetClear()
        
        ####### Save a Data Log
        packet = [0xFF, 3]                              ## packet for Internal Control : RcvDataTmeOut
        self.printCommLog_Control('Inner', packet)      ## Comm Log Display

    def CallBack_RcvPacketDataPop(self, event):         # Event Callback Function by event(EVT_TIMER, id=740.)
        remainedData = self.Rcv_packetDataPop()
        
        if(remainedData > 0):
            checkDlyTime = 0
            ##checkTime += 1000   ## Added a 1000ms for Debug
            self.timerCommCtrl_RcvPacketDataPop.StartOnce(5 + checkDlyTime)                              # Timer Start [unit: ms]
        else:
            self.timerCommCtrl_RcvPacketDataPop.Stop()
            self.timerCommCtrl_Rcv_rxBufCheck.StartOnce(5)   # Timer Start [unit: ms]


    def CallBack_SysUpDate(self, event):                ## Event Callback Function by event(EVT_TIMER, id=790)
        global com_Info
        
        ## Up-Date Current Time
        timeNow = datetime.datetime.now()
        timeNowStr = str(timeNow)
        self.SetStatusText(timeNowStr[:19])
        
        ## Up-Date Serial Comments label
        self.txtCtrl_serComments.Label = '(' + com_Info['PortNo']+'/'+str(com_Info['Baud'])+'/'+str(com_Info['Data'])+'/'+str(com_Info['Parity'])+'/'+str(com_Info['Stop'])+')'    # string - (COMx/38400/8/N/1)
    
    def CallBack_CommLog_TimeStamp(self, event):       # Event Callback Function by event(EVT_TIMER, id=799)
        timeNow = datetime.datetime.now()
        timeNow_ms = int(timeNow.hour*60*60*1000 + timeNow.minute*60*1000 + timeNow.second*1000 + timeNow.microsecond/1000)
        txtCommData_All = '\n' + str(timeNow_ms) + ':\t' + 'TxRx' + ':\t' + 'Raw Data...'
        txtAnalyze_All  = '\n' + str(timeNow_ms) + ':\t' + 'Analysis...'
        self.txtCtrl_CommLog.AppendText(txtCommData_All)
        self.txtCtrl_CommLog_Analyze.AppendText(txtAnalyze_All)
        self.txtCtrl_CommLog.Update()
        self.txtCtrl_CommLog_Analyze.Update()
    
class RaspiSim_App(wx.App):
    def OnInit(self):
        frame = RaspiSim_Frame(None, -1, 'RaspiSim Menu')     # Create a Frame Widget
        frame.Centre()                                  # Frame align : Center (frame.Center() == fram Centre())
        frame.Show()                                    # Show a Frame
        self.SetTopWindow(frame)
        
        return True
        
##def main():
if __name__ == '__main__':

    SerialPortsCfg.SerialPortsCfg_InitSet()
    app = wx.App()                  # Create a Application Obj / wx.App Class initialize 
    mainApp = RaspiSim_App(app)       # Create a Frame Widget Obj
    mainApp.MainLoop()              # Application Main Loop


##if __name__ == '__main__':
##    main()
    
#"""

