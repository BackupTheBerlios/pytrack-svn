import wx

from difdbi import *

class TrackPanel(wx.Panel):
    """
    This window shows the stored track list.
    """
    def __init__(self, parent, id, trackNotebook):
        wx.Panel.__init__(self, parent, id, size=(200, 80))

        DBOpen()
        self.db = CachedDb()

        self.trackNotebook = trackNotebook

        id = wx.NewId()
        self.labelChoice = wx.Choice(self, id, (100, 50), choices = ['all'])
        self.activeLabel = 0
        self.Bind(wx.EVT_CHOICE, self.EvtLabelChoice, self.labelChoice)
        
        id = wx.NewId()
        self.list = wx.ListBox(self, id)
        wx.EVT_LISTBOX(self, id, self.OnTrackSelect)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        mainSizer.Add(self.labelChoice, 0, wx.BOTTOM|wx.EXPAND, 5)
        mainSizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizer(mainSizer)

        self.Update()
        if(not self.list.IsEmpty()):
            self.list.Select(0)
        
    def Update(self):
        """ Updates the list and adds new list entries from
        the database. """
        
        labels = self.db.ListLabels()
        self.labelChoice.Clear()
        self.labelChoice.Append('all', -1)
        for label in labels:
            self.labelChoice.Append(label[1], label[0])
        self.labelChoice.SetSelection(self.activeLabel)

        tracks = self.db.ListTracks(self.labelChoice.GetClientData(self.activeLabel))
        self.list.Clear()
        for track in tracks:
            self.list.Append(track[1], track[0])

    def OnTrackSelect(self, event):
        """ This method is executed when an entry in the
        listbox is selected. """
        self.trackNotebook.SetTrackId(self.list.GetClientData(self.list.GetSelection()))

    def EvtLabelChoice(self, event):
        self.activeLabel = self.labelChoice.GetSelection()
        self.Update()

    def SetTrackNotebook(self, trackNotebook):
        """ Sets the notebook for a specific track. """
        self.trackNotebook = trackNotebook

