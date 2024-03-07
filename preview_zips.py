import PIL
from PIL import Image
import wx, wx.media, os, glob
import zipfile as ziplib
import wx.lib.scrolledpanel as scrolled
import version
import random

class MyFrame(wx.Frame):
    images = []
    def __init__(self, parent, title):
        screenSize = wx.DisplaySize()
        screenWidth = screenSize[0]
        screenHeight = screenSize[1]
        self.PhotoMaxSize = int(screenHeight/3)
        self.columns = int(screenSize[0]**(1/4.25))

        wx.Frame.__init__(self, parent, title=title, size=(int(screenWidth/1.3), int(screenHeight/1.3)))
        self.SetMinSize(wx.Size(int(screenWidth/1.3), int(screenHeight/1.3)))
        self.panel = wx.Panel(self, wx.ID_ANY)

        self.scrolled_panel = scrolled.ScrolledPanel(self.panel, -1, style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="scrolled_panel")
        self.scrolled_panel.SetAutoLayout(1)
        self.scrolled_panel.SetupScrolling()
        
        self.SetBackgroundColour('#1f1f1f')
        self.dirname="No file/directory selected."

        self.main_wrapper = wx.BoxSizer(wx.VERTICAL)
        self.image_wrapper = wx.BoxSizer(wx.VERTICAL)

        #button start
        open_single_btn = wx.Button(self.panel, label="Open Zip File", size=(200,100))
        open_multiple_btn = wx.Button(self.panel, label="Open Zips Directory", size=(200,100))
        open_multiple_unzipped_btn = wx.Button(self.panel,label="Open Image Directory", size=(200,100))
        shuffle_btn = wx.Button(self.panel, label="Shuffle", size=(200,100))
        clear_btn = wx.Button(self.panel, label="Clear", size=(200,100))


        open_single_btn.Bind(wx.EVT_BUTTON, self.on_open)
        open_multiple_btn.Bind(wx.EVT_BUTTON, self.on_open_zip_directory)
        open_multiple_unzipped_btn.Bind(wx.EVT_BUTTON, self.on_open_directory)
        shuffle_btn.Bind(wx.EVT_BUTTON, self.on_shuffle)
        clear_btn.Bind(wx.EVT_BUTTON, self.clear_view)

        btn_list = [
            open_single_btn,
            open_multiple_btn,
            open_multiple_unzipped_btn,
            shuffle_btn,
            clear_btn
        ]

        self.button_wrapper = wx.FlexGridSizer(cols=len(btn_list),hgap=5, vgap=5)
        self.button_wrapper.AddMany(btn_list)
        self.main_wrapper.Add(self.button_wrapper, flag=wx.ALL | wx.ALIGN_LEFT, border=5)
        #button end

        self.CreateStatusBar() #Status bar below frame

        #Menu Start
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Preview images inside compressed folders")
        filemenu.AppendSeparator()

        menuOpen = filemenu.Append(wx.ID_OPEN, "&Add", "Add file")
        filemenu.AppendSeparator()

        menuShuffle = filemenu.Append(wx.ID_REFRESH, '&Shuffle', "Shuffle list")
        filemenu.AppendSeparator()

        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate program")

        #Bind events
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)
        self.Bind(wx.EVT_MENU, self.on_exit, menuExit)
        self.Bind(wx.EVT_MENU, self.on_shuffle, menuShuffle)

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)
        #Menu End

        
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self.main_wrapper, 0, wx.EXPAND | wx.ALL, 5)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        self.panel.SetSizer(panelSizer)
        self.panel.Fit()
        self.Fit()
        self.scrolled_panel.SetSizer(self.image_wrapper)
        self.scrolled_panel.Fit()
        self.scrolled_panel.Layout()
        self.image_wrapper.Layout()
        self.panel.Layout()

    def update_view(self):
        self.image_wrapper.Clear(True)
        counter = 0
        if(len(self.images)>0):
            sizer = wx.WrapSizer(wx.HORIZONTAL)
            for img in self.images:
                if counter%(self.columns) == 0:
                    self.image_wrapper.Add(sizer, flag = wx.ALL|wx.EXPAND, border=5)
                    sizer = wx.WrapSizer(wx.HORIZONTAL)
                #sizer.Add(wx.StaticBitmap(self.scrolled_panel, -1, wx.Bitmap(img)), flag=wx.EXPAND)
                sizer.Add(wx.StaticBitmap(self.scrolled_panel, -1, wx.Bitmap(img)), flag=wx.EXPAND)
                counter+=1
            self.image_wrapper.Add(sizer, flag=wx.ALL | wx.EXPAND, border=5)
            self.image_wrapper.Layout()
        self.scrolled_panel.SetupScrolling()

    def clear_view(self, event):
        self.image_wrapper.Clear(True)

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
        self.update_view()
        self.SetStatusText("Path: "+self.dirname)
        dlg.Destroy()

    def on_open_zip_directory(self, event):
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a folder", self.dirname, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir_list = glob.glob(dlg.GetPath()+"/*.zip")
            for path in dir_list:
                archive = self.get_archive(path)
                self.images.extend(self.image_list(archive))
                archive.close()
        self.update_view()
        self.SetStatusText("Path: "+ dlg.GetPath())
        dlg.Destroy()


    def on_open_directory(self, event):
        self.dirname = ''
        self.images = []
        dlg = wx.DirDialog(self, "Choose a folder", self.dirname, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir_path = dlg.GetPath()
            image_files = glob.glob(os.path.join(dir_path, '*.[Pp][Nn][Gg]')) + glob.glob(os.path.join(dir_path, '*.[Jj][Pp][Gg]')) + glob.glob(os.path.join(dir_path, '*.[Jj][Pp][Ee][Gg]'))
            resized_images = [self.resize(img) for img in image_files]
            image_list = []
            for img in resized_images:
                wx_image = wx.Image(img.size[0], img.size[1])
                wx_image.SetData(img.convert('RGB').tobytes())
                image_list.append(wx_image)
            self.images.extend(image_list)
        self.update_view()
        self.SetStatusText("Path: " + dir_path)
        dlg.Destroy()

    def on_shuffle(self, event):
        random.shuffle(self.images)
        self.update_view()

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
            if hasattr(img, 'size') == False:
                img = Image.open(img)
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