import wx
import garmin

import matplotlib
matplotlib.use('WX')
from matplotlib.backends.backend_wx import Toolbar, FigureCanvasWx,\
     FigureManager
import matplotlib.matlab
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
import matplotlib.numerix as numpy

from difdbi import *

class PlotPanel(wx.Panel):
    def __init__(self, parent, id, trackId):
        wx.Panel.__init__(self, parent, id)

        self.trackId = trackId

        DBOpen()
        self.db = CachedDb()

        #self.state="timealt"
        #self.state="timedistance"
        self.state="timespeed"
        
        self.fig = Figure((5,4), 75)
        self.canvas = FigureCanvasWx(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        # Create a figure manager to manage things
        self.figmgr = FigureManager(self.canvas, 1, self)
        self.axes = self.figmgr.add_subplot(111)
        self.axes.hold(0)
        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        self.plotTimeAltitude()
        self.UpdatePanel(self.trackId)
        
    def plotTimeAltitude(self):
        time = []
        alt = []
        tplist = self.db.ListTrackPoints(self.trackId)
        for tp in tplist:
            time.append(int(tp[4])-int(tplist[0][4]))
            alt.append(tp[3])
        self.axes.plot(time, alt)
        self.axes.grid(True)
        self.axes.set_xlabel("Seconds")
        self.axes.set_ylabel("Meters")
        self.axes.set_title("Time / Altitude Graph")

        self.toolbar.update()
        self.Refresh()

    def plotTimeSpeed(self):
        time = []
        speed = []
        tplist = self.db.ListTrackPoints(self.trackId)
        p2 = False
        for tp in tplist:
            currentTime = int(tp[4])-int(tplist[0][4])
            if not p2:
                p2 = garmin.D301()
                p2.slon = tp[1]
                p2.slat = tp[2]
                p2.alt = tp[3]
                speed.append(0)
            else:
                p1 = garmin.D301()
                p1.slon = tp[1]
                p1.slat = tp[2]
                p1.alt = tp[3]
                if currentTime-lastTime > 0:
                    speed.append(3.6*garmin.distance(p1, p2)/(currentTime-lastTime))
                else:
                    speed.append(0)
                p2=p1
            lastTime = currentTime
            time.append(currentTime)
        self.axes.plot(time, speed)
        self.axes.grid(True)
        self.axes.set_xlabel("Seconds")
        self.axes.set_ylabel("km/s")
        self.axes.set_title("Time / Speed Graph")

        self.toolbar.update()
        self.Refresh()

    def plotTimeTotalDistance(self):
        time = []
        distance = []
        tplist = self.db.ListTrackPoints(self.trackId)
        p2 = False
        for tp in tplist:
            time.append(int(tp[4])-int(tplist[0][4]))
            if not p2:
                lastDistance=0
                p2 = garmin.D301()
                p2.slon = tp[1]
                p2.slat = tp[2]
                p2.alt = tp[3]
            else:
                p1 = garmin.D301()
                p1.slon = tp[1]
                p1.slat = tp[2]
                p1.alt = tp[3]
                lastDistance+=garmin.distance(p1, p2)
                p2=p1
            distance.append(lastDistance)
        self.axes.plot(time, distance)
        self.axes.grid(True)
        self.axes.set_xlabel("Seconds")
        self.axes.set_ylabel("Meters")
        self.axes.set_title("Time / Total Distance Graph")

        self.toolbar.update()
        self.Refresh()

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an 
        # unmanaged toolbar in your frame
        return self.toolbar
    
    def UpdatePanel(self, trackId):
        self.trackId = trackId

        if self.state=="timealt":
            self.plotTimeAltitude()
        elif self.state == "timedistance":
            self.plotTimeTotalDistance()
        elif self.state == "timespeed":
            self.plotTimeSpeed()
            
if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    frame = wx.Frame(None, -1, "Test Plot")
    sizer=wx.BoxSizer(wx.VERTICAL)
    plotPanel = PlotPanel(frame, -1, 2)
    sizer.Add(plotPanel, 1, wx.ALL|wx.EXPAND, 5)
    frame.SetSizer(sizer)
    frame.Layout()
    frame.Fit()
    frame.Show()
    app.MainLoop()
