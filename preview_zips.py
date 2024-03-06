from PIL import Image
import wx, wx.media, os, glob
import zipfile as ziplib
import wx.lib.scrolledpanel as scrolled
import version

class MyFrame(wx.Frame): #TODO: Scroll bar...
    images = []
    def __init__(self, parent, title):
        screenSize = wx.DisplaySize()
        screenWidth = screenSize[0]
        screenHeight = screenSize[1]
        self.PhotoMaxSize = int(screenHeight/3)
        columns = int(screenSize[0]**(1/4.25))

        wx.Frame.__init__(self, parent, title=title, size=(int(screenWidth/1.3), int(screenHeight/1.3)))
        self.SetMinSize(wx.Size(int(screenWidth/1.3), int(screenHeight/1.3)))
        self.panel = wx.Panel(self, wx.ID_ANY)

        self.scrolled_panel = scrolled.ScrolledPanel(self.panel, -1, style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="scrolled_panel")
        self.scrolled_panel.SetAutoLayout(1)
        self.scrolled_panel.SetupScrolling()
        
        self.SetBackgroundColour('#1f1f1f')
        self.dirname="No file/directory selected."

        wrapper = wx.BoxSizer(wx.VERTICAL)

        self.fgs = wx.FlexGridSizer(cols=columns, hgap=5, vgap=5)
        self.fgs_btn = wx.FlexGridSizer(cols=2,hgap=5, vgap=5)

        for i in range(0,columns):
            self.fgs.AddGrowableCol(i,1)

        open_single = wx.Button(self.scrolled_panel, label="Open File", size=(200,100))
        open_multiple = wx.Button(self.scrolled_panel, label="Open Directory", size=(200,100))

        open_single.Bind(wx.EVT_BUTTON, self.on_open)
        open_multiple.Bind(wx.EVT_BUTTON, self.on_open_directory)
        self.fgs_btn.AddMany([open_single, open_multiple])

        wrapper.Add(self.fgs_btn, flag=wx.ALL | wx.ALIGN_LEFT, border=5)
        wrapper.Add(self.fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        self.CreateStatusBar() #Status bar below frame

        #Menu
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Preview images inside compressed folders")
        filemenu.AppendSeparator()

        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open file")
        filemenu.AppendSeparator()

        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate program")

        #Bind events
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)
        self.Bind(wx.EVT_MENU, self.on_exit, menuExit)
        self.Bind(wx.EVT_MENU, self.on_open, menuOpen)

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)

        self.scrolled_panel.SetSizer(wrapper)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        self.panel.SetSizer(panelSizer)
        self.scrolled_panel.Fit()
        self.panel.Fit()
        self.Fit()

    def update_view(self):
        self.fgs.Clear()
        if(len(self.images)>0):
            for img in self.images:
                # fgs.Add(wx.StaticBitmap(self.scrolled_window, -1, wx.Bitmap(img)), flag=wx.EXPAND)
                self.fgs.Add(wx.StaticBitmap(self.scrolled_panel, -1, wx.Bitmap(img)), flag=wx.EXPAND)
        self.panel.Layout()

    def on_open(self, event):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename =dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            path = os.path.join(self.dirname, self.filename)
            archive = self.get_archive(path)
            self.images = self.image_list(archive)
            archive.close()
        dlg.Destroy()
        self.update_view()
        self.SetStatusText("Path: "+self.dirname)

    def on_open_directory(self, event):
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a folder", self.dirname, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir_list = glob.glob(dlg.GetPath()+"/*.zip")
            for path in dir_list:
                archive = self.get_archive(path)
                self.images.extend(self.image_list(archive))
                archive.close()
        dlg.Destroy()
        self.update_view()
        self.SetStatusText("Path: "+ dlg.GetPath())
    
    def get_archive(self, path):
        return ziplib.ZipFile(path, 'r')
    
    def image_list(self, archive):
        infolist = archive.infolist()
        image_list = []
        for info in infolist:
            if not info.is_dir() and (info.filename.endswith('.png') or info.filename.endswith('.jpg')):
                with archive.open((info.filename), 'r') as file:
                    pil_image = Image.open(file)
                    pil_image = self.resize(pil_image)
                    wx_image = wx.Image(pil_image.size[0], pil_image.size[1])
                
                    wx_image.SetData(pil_image.convert('RGB').tobytes())
                    image_list.append(wx_image)
        return image_list
    
    def resize(self, img):
            W = img.size[0]
            H = img.size[1]
            if W > H:
                NewW = self.PhotoMaxSize
                NewH = self.PhotoMaxSize * H / W
            else:
                NewH = self.PhotoMaxSize
                NewW = self.PhotoMaxSize * W / H
            return img.resize((int(NewW),int(NewH)))

    def on_about(self, event):
        version_info = f"Version: {version.VERSION_STRING}"
        dlg = wx.MessageDialog(self, "Tool to preview images within multuiple zip folders.\n"+ version_info, "About preview_zips", wx.OK)
        dlg.ShowModal() #show it
        dlg.Destroy() #Destroy when finished.

    def on_exit(self, event):
        self.Close(True)

app = wx.App(False)
frame = MyFrame(None, 'Zip_Preview')
frame.Show()
app.MainLoop()