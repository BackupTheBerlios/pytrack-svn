import wx
import wx.lib.plot
import garmin

from difdbi import *

class PlotPanel(wx.Panel):
    def __init__(self, parent, id, trackId):
        wx.Panel.__init__(self, parent, id)

        self.trackId = trackId

        DBOpen()
        self.db = CachedDb()

        #double pack the plotCanvas into panel or we will
        #get a problem with the size...
        self.plotPanel = wx.Panel(self, -1)
        self.plotPlotPanel = wx.Panel(self.plotPanel, -1)
        self.canvas = wx.lib.plot.PlotCanvas(self.plotPanel)
        self.canvas.SetSize((200, 200))
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.canvas, 1, wx.GROW)
        self.plotPanel.SetSizer(s)
        

        # Create a Choice to select the graph
        self.graphs = ["Time / Altitude",
                       "Distance / Altitude",
                       "Time / Total Distance",
                       "Time / Speed"]
        self.state = self.graphs[0]
        self.ch = wx.Choice(self, -1, choices = self.graphs)
        self.ch.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnGraphChosen, self.ch)

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Add the Choice at the top.
        sizer.Add(self.ch, 0, wx.GROW)
        # This way of adding to sizer allows resizing
        sizer.Add(self.plotPanel, 1, wx.BOTTOM|wx.TOP|wx.GROW, 2)
        
        self.SetSizer(sizer)
        self.Fit()

        self.Bind(wx.EVT_SIZE, self.OnSize)
         
        self.plotTimeAltitude()
        self.UpdatePanel(self.trackId)

    def OnSize(self, event):
        #we have to manually adjust the plot canvas size
        self.canvas.SetSize(self.plotPanel.GetClientSize())
        
    def plotTimeAltitude(self):
        """ Plot a Time / Altitude Graph with  """
        time = []
        alt = []
        #get the list of trackpoints
        tplist = self.db.ListTrackPoints(self.trackId)
        for tp in tplist:
            #calculate each time and altitude and add them into a list
            time.append(int(tp[4])-int(tplist[0][4]))
            alt.append(tp[3])

        self.PlotData("Time / Altitude", "Time in min", "Altitude in m", time, alt)
        

    def plotTimeSpeed(self):
        """ Plot a Time / Speed Graph with  """
        time = []
        speed = []
        tplist = self.db.ListTrackPoints(self.trackId)
        p2 = False
        for tp in tplist:
            currentTime = int(tp[4])-int(tplist[0][4])
            if not p2:
                #if p2 does not exist yet, we are at the first point
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
                #check that we don't divide by 0
                if currentTime-lastTime > 0:
                    speed.append(3.6*garmin.distance(p1, p2)/(currentTime-lastTime))
                else:
                    speed.append(0)
                p2=p1
            lastTime = currentTime
            time.append(currentTime)

        self.PlotData("Time / Speed", "Time in min", "Speed in km/h", time, speed)

    def plotDistanceAltitude(self):
        """ Plot a Distance / Altitude Graph """
        distance = []
        alt = []
        tplist = self.db.ListTrackPoints(self.trackId)
        p2 = False
        for tp in tplist:
            alt.append(int(tp[3]))
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

        self.PlotData("Distance / Altitude", "Distance in m", "Altitude in m", distance, alt)

    def plotTimeTotalDistance(self):
        """ Plot a Time / Total Distance Graph """
        time = []
        distance = []
        tplist = self.db.ListTrackPoints(self.trackId)
        p2 = False
        for tp in tplist:
            time.append(int(tp[4]) - int(tplist[0][4]))
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

        self.PlotData("Time / Distance", "Time in min", "Distance in m", time, distance)

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an 
        # unmanaged toolbar in your frame
        return self.toolbar
    
    def UpdatePanel(self, trackId):
        """ This method updates everything s.t. it represents
        the data for the given trackId. """
        self.trackId = trackId

        if self.state==self.graphs[0]:
            self.plotTimeAltitude()
        elif self.state == self.graphs[1]:
            self.plotDistanceAltitude()
        elif self.state == self.graphs[2]:
            self.plotTimeTotalDistance()
        elif self.state == self.graphs[3]:
            self.plotTimeSpeed()

    def OnGraphChosen(self, event):
        """ This method is called when a new item is selected from
        the Choice of graphs. It updates the graph accordingly. """
        self.state = event.GetString()
        self.UpdatePanel(self.trackId)
        
    def resetDefaults(self):
        """Just to reset the fonts back to the PlotCanvas defaults"""
        self.canvas.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.NORMAL))
        self.canvas.SetFontSizeAxis(10)
        self.canvas.SetFontSizeLegend(7)
        self.canvas.SetXSpec('auto')
        self.canvas.SetYSpec('auto')

    def PlotData(self, title, xaxis, yaxis, xData, yData):
        #we have to check this or plot will crash...
        if min(yData) != max(yData) and min(xData) != min(yData):

            data1 = []
            for i in range(len(xData)):
                data1.append((xData[i], yData[i]))

            lines = wx.lib.plot.PolyLine(data1, colour='red')

            self.resetDefaults()
            self.canvas.Draw(wx.lib.plot.PlotGraphics([lines], title, xaxis, yaxis))
        else:
            self.canvas.Clear()

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
