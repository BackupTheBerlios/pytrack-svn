##
##
##
## Beschreibung:
## Table to show trackpoints of a track.
##
## 
##
##
# secs from Unix epoch (start of 1970) to Sun Dec 31 00:00:00 1989
TimeEpoch = 631065600

import wx
from wx import grid
import string
import sys
sys.path.append("garmin")
import garmin
import time

class TrackPointDataTable(grid.PyGridTableBase):

    def __init__(self):
        grid.PyGridTableBase.__init__(self)
        self.colLabels = ['id', 'slat', 'slon', 'alt', 'time']
        self.dataTypes = [grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_STRING]
        self.data = []

    def GetNumberRows(self):
        return len(self.data) + 1

    def GetNumberCols(self):
        return 5

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row]
        except:
            return 1
        
    def GetValue(self, row, col):
        try:
            if col==1 or col==2:
                return garmin.degrees(self.data[row][col])
            elif col==4:
                return str(time.asctime(time.gmtime(TimeEpoch+int(self.data[row][col]))))
            else:
                return str(self.data[row][col])
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        #print "row: %d col: %d value: %s"%(row, col, str(value))
        try:
            if col==0:
                self.data[row][col] = int(value)
            elif col == 1:
                self.data[row][col] = double(value)
            elif col == 2:
                self.data[row][col] = double(value)
            elif col == 3:
                self.data[row][col] = double(value)
            elif col == 4:
                self.data[row][col] = value
        except IndexError:
            # add a new row
            if col==0:
                self.data.append([-1, -1, -1, '', -1])
            msg = grid.GridTableMessage(self,grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,1)
            self.GetView().ProcessTableMessage(msg)

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Load the table. Table grows dynamically.
    def LoadTable(self,lst):
        n = self.GetNumberRows()
        msg = grid.GridTableMessage(self,grid.GRIDTABLE_NOTIFY_ROWS_DELETED,0,n-1)
        self.GetView().ProcessTableMessage(msg)
        self.data = lst
        msg = grid.GridTableMessage(self,grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,self.GetNumberRows()-1)
        self.GetView().ProcessTableMessage(msg)

    # Readout the table
    def ReadTable(self):
        return self.data

    # Delete row and shrink grid by 1
    def DeleteRow(self,row):
        try:
            #self.data[row].delete()
            del self.data[row]
            if self.GetNumberRows() > 0:
                msg = grid.GridTableMessage(self,grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                                         self.GetNumberRows(),1)
                self.GetView().ProcessTableMessage(msg)
            return 1
        except:
            return 0


class TrackPointGrid(grid.Grid):
    '''Table to display/edit tupels
    '''

    dClickHandler = None
    
    def __init__(self, parent):
        grid.Grid.__init__(self, parent, -1)

        table = TrackPointDataTable()
        self.table = table
        self.SetTable(table, True)

        self.SetRowLabelSize(0)
        self.SetColSize(0,40)
        self.SetColSize(1,140)
        self.SetColSize(2,140)
        self.SetColSize(3,100)
        self.SetColSize(4, 200)
        self.SetMargins(0,0)
        self.EnableDragGridSize(0)
        self.SetLabelFont(self.GetCellFont(0,0))
        self.SetColLabelSize(22)

        grid.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
        grid.EVT_GRID_CELL_RIGHT_DCLICK(self, self.OnRightDClick)
        wx.EVT_KEY_DOWN(self,self.OnKeypress)

        # Make some columns read-only
        attr = grid.GridCellAttr()
        attr.SetReadOnly()
        self.SetColAttr(0,attr)
        self.SetColAttr(1,attr)
        self.SetColAttr(2,attr)
        self.SetColAttr(3,attr)
        self.SetColAttr(4,attr)

    def SetDClickHandler(self, handler):
        self.dClickHandler = handler
        
    # Start cell editor on double clicks
    def OnLeftDClick(self, evt):
        if self.dClickHandler:
            self.dClickHandler(evt)

    # Delete row by right double click
    def OnRightDClick(self, evt):
        pass
        #self.table.DeleteRow(evt.GetRow())

    # Delete row by pressing "Delete" key
    def OnKeypress(self, evt):
        #if evt.GetKeyCode() == wx.K_DELETE:
        #    row = self.GetGridCursorRow()
        #    self.table.DeleteRow(row)
        evt.Skip()
        
    # Load application table
    # lst: [id,...]
    def Setup(self,lst):
        self.table.LoadTable(lst)

    def ReadTrackPoints(self):
        return self.table.ReadTable()

    #returns the trackpoint id of the row in which the cursor resides
    def GetGridCursorTrackId(self):
        row = self.GetGridCursorRow()
        trackid = self.table.data[row][0]
        self.table.DeleteRow(row)
        return trackid
#---------------------------------------------------------------------------

class TrackPointTable(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER,size=(405,500))
        sz = wx.BoxSizer(wx.VERTICAL)
        self.sz = sz
        grid = TrackPointGrid(self)
        self.grid = grid
        sz.Add(grid,1,wx.EXPAND)
        self.SetSizer(sz)
        self.SetAutoLayout(True)
        self.Layout()

    def Setup(self,lst):
        self.grid.Setup(lst)
        self.sz.SetVirtualSizeHints(self.grid)

    def GetRow(self, row):
        try:
            return self.grid.table.data[row]
        except IndexError:
            return []
        
    def DeleteMarkedTrackPoint(self):
        pass

##     def DeleteTrackPoint(self, delWord):
##         trackPointList = self.GetTrackPoints()
##         for i in range(len(trackPointList)):
##             if trackPointList[i] == delTrackPoint:
##                 self.grid.table.DeleteRow(i)
##                 break

##     def AddWord(self, leconid, first, description, second):
##         row=len(self.grid.table.data)
##         self.grid.table.SetValue(row,0,GetNewWordId(None))
##         self.grid.table.data[row].SetFirstLanguage(first)
##         self.grid.table.data[row].SetLeconId(leconid)
##         self.grid.table.data[row].SetSecondLanguage(second)
##         self.grid.table.data[row].SetDescription(description)
##         if self.grid.table.data[row].write():
##             self.grid.table.DeleteRow(row)
##         self.grid.SetGridCursor(row, 0)
##         self.sz.SetVirtualSizeHints(self.grid)
        
##     def GetWords(self):
##         return self.grid.ReadWords()

