import wx
import sys
sys.path.append("garmin")
import garmin
from difdbi import *
from TrackPointTable import *

class TrackNotebook(wx.Notebook):
    """
    This class implements all the nifty things you can
    do with a track like displaying it, removing, adding points
    etc
    """

    def __init__(self, parent, id, trackId):
        wx.Notebook.__init__(self, parent, id, size=(200, 200))
        self.trackId = trackId

        self.tplp = TrackPointListPanel(self, -1, trackId)
        self.AddPage(self.tplp, "TrackPoints")

        self.sp = StatisticsPanel(self, -1, trackId)
        self.AddPage(self.sp, "Statistics")

        self.lp = LabelPanel(self, -1, trackId)
        self.AddPage(self.lp, "Labels")

    def SetTrackId(self, id):
        """ Sets a new track id and updates the panels. """
        self.trackId = id
        self.tplp.Update(self.trackId)
        self.sp.Update(self.trackId)
        self.lp.Update(self.trackId)

class TrackPointListPanel(wx.Panel):
    """
    This panel is used to show a list of the trackpoints for the
    associated track.
    """

    def __init__(self, parent, id, trackId):
        wx.Panel.__init__(self, parent, id)

        self.trackId = trackId
        
        DBOpen()
        self.db = CachedDb()

        #visual stuff
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.trackPointTable = TrackPointTable(self)
        mainSizer.Add(self.trackPointTable, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        #buttons to remove/add trackpoints
        lowerSizer = wx.BoxSizer(wx.HORIZONTAL)

        id = wx.NewId()
        deletePointButton = wx.Button(self, id, "Remove Point")
        wx.EVT_BUTTON(self, id, self.OnDeletePointButton)
        lowerSizer.Add(deletePointButton, 0, wx.ALL, 5)

        id = wx.NewId()
        self.applyChangesButton = wx.Button(self, id, "Apply Changes")
        self.applyChangesButton.Enable(False)
        wx.EVT_BUTTON(self, id, self.OnApplyChanges)
        lowerSizer.Add(self.applyChangesButton, 0, wx.ALL, 5)

        mainSizer.Add(lowerSizer, 0, wx.ALL, 0)
        
        self.SetSizer(mainSizer)
        self.Update(self.trackId)

    def Update(self, trackId):
        """ Update the content of the trackpoints table. """
        self.trackId = trackId
        trackPoints = self.db.ListTrackPoints(self.trackId)
        self.trackPointTable.Setup(trackPoints)
        

    def OnDeletePointButton(self, event):
        self.db.DeleteTrackPoints(self.trackPointTable.grid.GetGridCursorTrackId())
        #self.Update(self.trackId)
        self.applyChangesButton.Enable(True)

    def OnApplyChanges(self, event):
        self.db.Commit()
        self.applyChangesButton.Enable(False)

class StatisticsPanel(wx.Panel):
    """
    This panel is used to show statistics of an
    associated track.
    """

    def __init__(self, parent, id, trackId):
        wx.Panel.__init__(self, parent, id)
        self.trackId = trackId

        DBOpen()
        self.db = CachedDb()

        self.totalDistanceLabel = wx.StaticText(self, -1, " m", (120, 10), (120,-1), style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.totalTimeLabel = wx.StaticText(self, -1, " min", (120, 30), (120,-1), style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.averageSpeedLabel = wx.StaticText(self, -1, " km/h", (120, 50), (120,-1), style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        self.Update(self.trackId)

        wx.StaticText(self, -1, "Total Distance:", (20, 10))
        wx.StaticText(self, -1, "Total Time: ", (20, 30))
        wx.StaticText(self, -1, "Average Speed: ", (20, 50))
        
    def Update(self, trackId):
        self.trackId = trackId
        trackPoints = self.db.ListTrackPoints(self.trackId)
        p2 = False
        totalDistance = 0
        for tp in trackPoints:
            p1 = garmin.D301()
            p1.slon = tp[1]
            p1.slat = tp[2]
            p1.alt = tp[3]
            if p2:
                totalDistance += garmin.distance(p1, p2)
            p2=p1
        self.totalDistance = totalDistance
        self.totalTime = int(trackPoints[-1][4])-int(trackPoints[0][4])
        if self.totalTime != 0:
            self.averageSpeed=(totalDistance/1000.0)/(self.totalTime/3600.0)
        else:
            self.averageSpeed=0
        self.totalDistanceLabel.SetLabel("%7.1f m"%(self.totalDistance,))
        self.totalTimeLabel.SetLabel("%d h %d min %d s"%(self.totalTime/3600,self.totalTime%3600/60,self.totalTime%60))
        self.averageSpeedLabel.SetLabel("%7.1f km/h"%(self.averageSpeed,))
        
        
class LabelPanel(wx.Panel):
    """
    This panel is used to show labels of an
    associated track.
    """

    def __init__(self, parent, id, trackId):
        wx.Panel.__init__(self, parent, id)
        self.trackId = trackId

        DBOpen()
        self.db = CachedDb()

         #visual stuff
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        mainSizer.Add(self.lc, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        self.lc.InsertColumn(0, "Id")
        self.lc.InsertColumn(1, "Name")
        self.lc.InsertColumn(2, "description")

        lowerSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.labelNameBox = wx.ComboBox(self, -1)
        lowerSizer.Add(self.labelNameBox)

        id = wx.NewId()
        addLabelButton = wx.Button(self, id, "Add Label")
        wx.EVT_BUTTON(self, id, self.OnAddLabelButton)
        lowerSizer.Add(addLabelButton, 0, wx.ALL, 5)

        id = wx.NewId()
        deleteLabelButton = wx.Button(self, id, "Delete Label")
        wx.EVT_BUTTON(self, id, self.OnDeleteLabelButton)
        lowerSizer.Add(deleteLabelButton, 0, wx.ALL|wx.ALIGN_RIGHT, 5)

        mainSizer.Add(lowerSizer, 0, wx.ALL|wx.EXPAND, 0)

        self.Update(self.trackId)

        self.SetSizer(mainSizer)

    def Update(self, trackId):
        self.trackId = trackId

        self.lc.DeleteAllItems()
        labels = self.db.ListLabels(self.trackId)
        for id, label, descr in labels:
            index = self.lc.InsertStringItem(sys.maxint, str(id))
            self.lc.SetStringItem(index, 1, str(label))
            self.lc.SetStringItem(index, 2, str(descr))
        self.lc.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        #update labelnamebox
        self.labelNameBox.Clear()
        labels = self.db.ListLabels()
        for id, label, description in labels:
            self.labelNameBox.Append(label)

    def OnAddLabelButton(self, event):
        if self.labelNameBox.GetValue() != "":
            self.db.AddLabel(self.trackId, self.labelNameBox.GetValue(), "")
        self.Update(self.trackId)

    def OnDeleteLabelButton(self, event):
        print self.lc.GetStringSelection()
