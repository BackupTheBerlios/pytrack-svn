import wx
import difdbi

# The control/widget containing the drawing. It is white and has no border. It
# is not necessary to defined its positon and size, since these parameters are
# set up by the layout constraints mechanism. However, I forced the control
# to have no border.
class DrawMapWindow(wx.Window):

    def __init__(self, parent, id, trackId):
        sty = wx.NO_BORDER
        wx.Window.__init__(self, parent, id, style=sty)
        self.parent = parent
        self.SetBackgroundColour(wx.WHITE)
        self.SetCursor(wx.CROSS_CURSOR)

        #initialize some vars
        self.trackId = trackId
        difdbi.DBOpen()
        self.db = difdbi.CachedDb()
        self.onPaintDone = False
        # Some initalisation, just to reminds the user that a variable
        # called self.BufferBmp exists. See self.OnSize().
        self.BufferBmp = None

        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)

        self.UpdateTrack(self.trackId)

    # OnSize is fired at the application start or when the frame is resized.
    # The OnSize event is fired BEFORE the OnPaint event. wx.Windows
    # handles the events in this order. This is not due to the fact,
    # that the code line wx.EVT_SIZE(...) is placed before the line
    # wx.EVT_PAINT(...).
    # The procedure OnSize() is the right place to define the
    # BufferBmp and its size. self.BufferBmp is the picture in memory,
    # which contains your drawing. self.BufferBmp is also used as a flag,
    # a None value indicates no picture.
    #
    def OnSize(self, event):
        # Get the size of the drawing area in pixels.
        self.wi, self.he = self.GetSizeTuple()
        # Create BufferBmp and set the same size as the drawing area.
        self.BufferBmp = wx.EmptyBitmap(self.wi, self.he)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.BufferBmp)
        # Drawing job
        ret = self.DoSomeDrawing(memdc)
        if not ret:  #error
            self.BufferBmp = None
            wx.MessageBox('Error in drawing', 'CommentedDrawing', wx.OK | wx.ICON_EXCLAMATION)
        #memdc.SelectObject(wx.NullBitmap) #is this important?


    # OnPaint is executed at the app start, when resizing or when
    # the application windows becomes active. OnPaint copies the
    # buffered picture, instead of preparing (again) the drawing job.
    # This is the trick, copying is very fast.
    # Note: if you forget to define the dc in this procedure,
    # (no dc = ... code line), the application will run in
    # an infinite loop. This is a common beginner's error. (I think)
    # BeginDrawing() and EndDrawing() are for windows platforms (see doc).
    def OnPaint(self, event):
        self.onPaintDone = True
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        if self.BufferBmp != None:
            dc.DrawBitmap(self.BufferBmp, 0, 0, True)
        else:
            pass
        dc.EndDrawing()


    # The function defines the drawing job. Everything is drawn on the dc.
    # In that application, the dc corresponds to the BufferBmp.
    # At this point, I will introduce a small complication, that is
    # in fact quite practical. It may happen, the drawing is not
    # working correctly. Either there is an error in the drawing job
    # or the data you want to plot can not be drawn correctly. A typical
    # example is the plotting of 'scientific data'. The data are not (or
    # may not be) scaled correctly, that leads to errors, generally integer
    # overflow errors.
    # To circumvent this, the procedure returns True, if the drawing succeed.
    # It returns False, if the drawing fails. The returned value may be used
    # later.
    def DoSomeDrawing(self, dc):
        try:

            dc.BeginDrawing()

            # Clear everything
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.Clear()
            
            dc.SetPen(wx.Pen(wx.RED, 1, wx.SOLID))
            #calculate factors for drawing
            dcwi, dche = dc.GetSizeTuple()
            factorx = dcwi/(self.slonDelta-2)
            factory = -dche/(self.slatDelta-2)
            shiftx = 1
            shifty = dche - 1
            lastPoint = {}
            #draw the track
            for [slon, slat] in self.trackPoints:
                if lastPoint:
                    x1 = int((lastPoint["slon"]-self.slonMin)*factorx) + shiftx
                    y1 = int((lastPoint["slat"]-self.slatMin)*factory) + shifty
                    x2 = int((slon-self.slonMin)*factorx) + shiftx
                    y2 = int((slat-self.slatMin)*factory) + shifty
                    dc.DrawLine(x1, y1, x2, y2)
                lastPoint["slon"] = slon
                lastPoint["slat"] = slat
                                

            dc.EndDrawing()
            return True

        except:
            return False


    def UpdateTrack(self, trackId):
        """ Updates the track to draw and calls the redraw methods. """
        self.trackId = trackId

        trackPoints = self.db.ListTrackPoints(self.trackId)

        #compose list for the points for easier handling while drawing
        slon = []
        slat = []
        self.trackPoints = []
        for tp in trackPoints:
            slon.append(tp[1])
            slat.append(tp[2])
            self.trackPoints.append([tp[1], tp[2]])

        #calculate some handy data for drawing
        self.slonMin = min(slon)
        self.slonMax = max(slon)
        self.slatMin = min(slat)
        self.slatMax = max(slat)
        self.slonDelta = self.slonMax-self.slonMin
        self.slatDelta = self.slatMax-self.slatMin

        #after we redrawed the first time,
        #repaint when the trackId changes.
        if self.onPaintDone:
            self.OnSize(None)
            self.Refresh()


#-------------------------------------------------------------------

# Panel in the main frame. It covers automatically the client area of
# its parent frame. The panel contains a single control (class MyDrawingArea),
# on which the drawing takes place. The position and size of this control is
# set up with layout constraints, so that the user see what happens to the
# drawing when the main frame is resized.
class MyPanel(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize)

        self.drawingarea = DrawMapWindow(self, -1, 2)

        self.SetAutoLayout(True)

        gap = 30 #in pixels
        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, gap)
        lc.left.SameAs(self, wx.Left, gap)
        lc.right.SameAs(self, wx.Width, gap)
        lc.bottom.SameAs(self, wx.Bottom, gap)
        self.drawingarea.SetConstraints(lc)

#-------------------------------------------------------------------

# Usual frame. Can be resized, maximized and minimized.
# The frame contains one panel.
class MyFrame(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'CommentedDrawing', wx.Point(0, 0), wx.Size(500, 400))
        self.panel = MyPanel(self, -1)

        wx.EVT_CLOSE(self, self.OnCloseWindow)

    def OnCloseWindow(self, event):
        self.Destroy()

#-------------------------------------------------------------------

class MyApp(wx.App):

    def OnInit(self):
        frame = MyFrame(None, -1)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

#-------------------------------------------------------------------

def main():
    print 'main is running...'
    app = MyApp(0)
    app.MainLoop()

#-------------------------------------------------------------------

if __name__ == "__main__" :
    main()

#eof-------------------------------------------------------------------
