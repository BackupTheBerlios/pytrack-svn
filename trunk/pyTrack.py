##
##
## Thomas Schmid (t dot schmid at gmx dot net)
##
## python gps program to transfer and organize
## tracks from your gps
##
##
##
##
#from wxPython.wx import *
import wx
import time
import sys
sys.path.append("pygarmin")
import garmin

from Config import *
from TrackPanel import *
from TrackNotebook import *
from difdbi import *


class PyTrackFrame(wx.Frame):
    """ This class implements the main window """

    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        """ Initialize the class """
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        DBOpen('test.dat')
        self.db = CachedDb()

        self.parent = parent
        self.MakeWindow()
        self.RegisterEventHandlers()

        self.GPSInit = False

        #Main Sizer
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Right side of mainwindow
        self.mainNotebook = TrackNotebook(self, -1, 1)

        #Left side of mainwindow
        leftSizer = wx.BoxSizer(wx.VERTICAL)

        ## the chooser notebook
        self.chooserNotebook = wx.Notebook(self, -1, size=(200, 100))
        self.tp = TrackPanel(self.chooserNotebook, -1, self.mainNotebook)
        self.chooserNotebook.AddPage(self.tp, "Tracks")

        ## the action panel
        self.actionPanel = wx.GridSizer(2,2)

        id = wx.NewId()
        importButton = wx.Button(self, id, "Import")
        wx.EVT_BUTTON(self, id, self.OnNotYetImplemented)

        id = wx.NewId()
        exportButton = wx.Button(self, id, "Export")
        wx.EVT_BUTTON(self, id, self.OnNotYetImplemented)

        id = wx.NewId()
        getButton = wx.Button(self, id, "Get From GPS")
        wx.EVT_BUTTON(self, id, self.OnGetButton)

        id = wx.NewId()
        sendButton = wx.Button(self, id, "Send To GPS")
        wx.EVT_BUTTON(self, id, self.OnNotYetImplemented)

        self.actionPanel.Add(importButton, 0, wx.ALL, 5)
        self.actionPanel.Add(exportButton, 0, wx.ALL, 5)
        self.actionPanel.Add(getButton, 0, wx.ALL, 5)
        self.actionPanel.Add(sendButton, 0, wx.ALL, 5)

        leftSizer.Add(self.chooserNotebook, 1, wx.ALL|wx.EXPAND, 5)
        leftSizer.Add(self.actionPanel, 0, wx.ALL, 5)

        mainSizer.Add(leftSizer, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(mainSizer)
        self.SetAutoLayout(True)
        self.Layout()
        self.Fit()
        self.Center(wx.BOTH)

    def RegisterEventHandlers(self):
        wx.EVT_CLOSE(self,self.OnCloseWindow)

    def Show(self, show):
        wx.Frame.Show(self, show)

    def MakeWindow(self):
        """ Constructs the Window """
        sb = wx.StatusBar(self, -1)
        self.sb = sb
        self.SetStatusBar(sb)
        
        pass

    # Button Events
    def OnGetButton(self, event):
        max = 100

        self.InitGPS()
        msg = "GPS Product ID: %d Description: %s\n Receiving Tracks" % \
              (self.gps.prod_id, self.gps.prod_descs[0])

        dlg = wx.ProgressDialog("Connecting to GPS",
                                msg,
                                maximum = max,
                                parent=self,
                                style = wx.PD_CAN_ABORT | wx.PD_APP_MODAL)
        
        count = 0
        tracks = self.gps.getTracks()
        dlg.Update(50, "saving in database")

        for t in tracks:
            if t[0].trk_ident == "ACTIVE LOG":
                dlg2 = wx.TextEntryDialog(
                    self, 'Please provide a name for the active log:',
                    'ACTIVE LOG', 'ACTIVE LOG '+time.asctime(time.localtime()))

                if dlg2.ShowModal() == wx.ID_OK:
                    t[0].trk_ident == dlg2.GetValue()

                dlg2.Destroy()
            ret = self.db.WriteTrack(t)
            print ret
            if ret == -1:
                self.MessageDialog("Error while saving the track "+t[0].trk_ident, "DB error")
            elif ret == -2:
                #track name already exists
                while ret == -2:
                    dlg2 = wx.TextEntryDialog(
                        self, 'A track with this name already exists.\nPlease provide an other name:',
                        'Error: Track Name', t[0].trk_ident)

                    if dlg2.ShowModal() == wx.ID_OK:
                        t[0].trk_ident == dlg2.GetValue()
                        ret = self.db.WriteTrack(t)
                    else:
                        ret = 0
                    dlg2.Destroy()
                
        dlg.Destroy()
        self.tp.Update()
        
    # Callbacks
    def OnCloseWindow(self, event):
        self.Destroy()

        if(self.GPSInit):
            #self.phys.close()
            pass

    def OnNotYetImplemented(self, event):
        self.MessageDialog("Noch nicht implementiert", "Noch nicht implementiert")

    def OnExit(self,event):
        for win in self.editWindows:
            if win:
                win.Destroy()
        self.Destroy()

    #Dialogs

    def MessageDialog(self, text, title):
        messageDialog = wx.MessageDialog(self, text, title, wx.OK | wx.ICON_INFORMATION)
        messageDialog.ShowModal()
        messageDialog.Destroy()

    #Methods
    def InitGPS(self):
        if(not self.GPSInit):
            self.GPSInit = True
            #connect the serial link
            self.phys = garmin.SerialLink(serialDevice)
            #connect to the garmin
            self.gps = garmin.Garmin(self.phys)


##-------------- Main program

if __name__ == '__main__':
    app = wx.PySimpleApp()

    win = PyTrackFrame(None, -1, "pyTrack %s" % (VERSION),
                       size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
    win.Show(True)
    app.MainLoop()
