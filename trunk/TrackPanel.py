import wx

from difdbi import *

class TrackPanel(wx.Panel):
    """
    This window shows the stored track list.
    """
    def __init__(self, parent, id, trackNotebook):
        wx.Panel.__init__(self, parent, id, size=(200, 80))

        DBOpen('test.dat')
        self.db = CachedDb()

        self.trackNotebook = trackNotebook
        
        id = wx.NewId()
        self.list = wx.ListBox(self, id)
        wx.EVT_LISTBOX(self, id, self.OnTrackSelect)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        mainSizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(mainSizer)

        self.Update()
        if(not self.list.IsEmpty()):
            self.list.Select(0)
        
    def Update(self):
        """ Updates the list and adds new list entries from
        the database. """
        
        tracks = self.db.ListTracks()
        self.list.Clear()
        for track in tracks:
            self.list.Append(track[1], track[0])

    def OnTrackSelect(self, event):
        """ This method is executed when an entry in the
        listbox is selected. """
        #we can savely take 0 since we can only select 1 entry
        self.trackNotebook.SetTrackId(self.list.GetClientData(self.list.GetSelections()[0]))

    def SetTrackNotebook(self, trackNotebook):
        self.trackNotebook = trackNotebook
