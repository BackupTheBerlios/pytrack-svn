import wx
import difdbi


class ConfigDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        difdbi.DBOpen()
        self.db = difdbi.CachedDb()

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1,
                              "For *nix system, set the serial device to\n"+
                              "the device name where the garmin unit is \n"+
                              "connected to. On Windows systems, set the \n"
                              "device name to 0 for COM1, 1 for COM2 etc.")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Serial Device:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.serialText = wx.TextCtrl(self, -1, self.db.GetSerialDevice(), size=(80,-1))
        box.Add(self.serialText, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        btn = wx.Button(self, wx.ID_OK, " OK ")
        btn.SetDefault()
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOkButton)
        
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        btn = wx.Button(self, wx.ID_CANCEL, " Cancel ")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnOkButton(self, event):
        self.db.SetSerialDevice(self.serialText.GetValue())
        self.EndModal(wx.ID_OK)
