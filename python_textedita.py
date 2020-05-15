#-*- coding:utf-8 -*-
import wx,sys,re,os,wx.media,wx.html2,pickle,pprint,ast,codecs
import wx.lib.agw.aui.auibook as aui
from wx.html import HtmlEasyPrinting,HtmlWindow
import wx.lib.agw.rulerctrl as rc
#-------------------------------------------------------------------------------
import platform
pf = platform.system()
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
"""
pdfviewerに関して元々のモジュールのスクリプトを管理者権限で書き換えるか，
以下のようにメソッドをオーバーライドしないとエラーが発生し使えません．
詳しくは以下を．

 https://github.com/wxWidgets/Phoenix/issues/1350
 https://github.com/wxWidgets/Phoenix/pull/1519/commits/54b065f1fd8b7893e30c0d2047489166bb6d127d

オーバーライドする場合は以下のコード（ほぼコピペ）が必要ですが，
管理者権限でモジュールそのものを書き換えた場合は必要ありません．

モジュールそのものを書き換える場合，書き換えるファイルはプログラムファイルの
中のPythonのフォルダ下の
 \Lib\site-packages\wx\lib\pdfviewer
のディレクトリにある”viewer.py”を管理者権限で開き，
519行目（class mupdfProcessor(object)のdef RenderPageのtry構文の中）と
もう一ヶ所を以下のオーバーライドしたコードのように変更してください．
"""
from wx.lib.pdfviewer.viewer import pdfViewer,mupdfProcessor
from wx.lib.pdfviewer.buttonpanel import pdfButtonPanel
VERBOSE = True

try:
    # see http://pythonhosted.org/PyMuPDF - documentation & installation
    import fitz
    mupdf = True
except ImportError:
    mupdf = False
    try:
        # see http://pythonhosted.org/PyPDF2
        import PyPDF2
        from PyPDF2 import PdfFileReader
        from PyPDF2.pdf import ContentStream, PageObject
        from PyPDF2.filters import ASCII85Decode, FlateDecode
        if VERBOSE: print('pdfviewer using PyPDF2')
    except ImportError:
        msg = "PyMuPDF or PyPDF2 must be available to use pdfviewer"
        raise ImportError(msg)

GraphicsContext = wx.GraphicsContext
have_cairo = False
if not mupdf:
    try:
        import wx.lib.wxcairo as wxcairo
        import cairo
        from wx.lib.graphics import GraphicsContext
        have_cairo = True
    except ImportError:
        if VERBOSE: print('pdfviewer using wx.GraphicsContext')

    # New PageObject method added by Forestfield Software
    def extractOperators(self):
        """
        Locate and return all commands in the order they
        occur in the content stream
        """
        ops = []
        content = self["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pdf)
        for op in content.operations:
            if type(op[1] == bytes):
                op = (op[0], op[1].decode())
            ops.append(op)
        return ops
    # Inject this method into the PageObject class
    PageObject.extractOperators = extractOperators

    # If reportlab is installed, use its stringWidth metric. For justifying text,
    # where widths are cumulative, dc.GetTextExtent consistently underestimates,
    # possibly because it returns integer rather than float.
    try:
        from reportlab.pdfbase.pdfmetrics import stringWidth
        have_rlwidth = True
        if VERBOSE: print('pdfviewer using reportlab stringWidth function')
    except ImportError:
        have_rlwidth = False

class pdfViewer(pdfViewer):
    def CalculateDimensions(self):
        """
        Compute the required buffer sizes to hold the viewed rectangle and
        the range of pages visible. Set self.page_buffer_valid = False if
        the current set of rendered pages changes
        """
        self.frompage = 0
        self.topage = 0
        device_scale = wx.ClientDC(self).GetPPI()[0]/72.0   # pixels per inch/points per inch
        self.font_scale_metrics =  1.0
        self.font_scale_size = 1.0
        # for Windows only with wx.GraphicsContext the rendered font size is too big
        # in the ratio of screen pixels per inch to points per inch
        # and font metrics are too big in the same ratio for both for Cairo and wx.GC
        if wx.PlatformInfo[1] == 'wxMSW':
            self.font_scale_metrics = 1.0 / device_scale
            if not have_cairo:
                self.font_scale_size = 1.0 / device_scale

        self.winwidth, self.winheight = self.GetClientSize()
        """
        消去修正部分
        if self.winheight < 100:
            return
        """
        self.Ypage = self.pageheight + self.nom_page_gap
        if self.zoomscale > 0.0:
            self.scale = self.zoomscale * device_scale
        else:
            if int(self.zoomscale) == -1:   # fit width
                self.scale = self.winwidth / self.pagewidth
            else:                           # fit page
                self.scale = self.winheight / self.pageheight
        
        # 追加修正部分==========================================
        if self.scale == 0.0: # this could happen if the window was not yet initialized
            self.scale = 1.0
        # ======================================================
        self.Xpagepixels = int(round(self.pagewidth*self.scale))
        self.Ypagepixels = int(round(self.Ypage*self.scale))

        # adjust inter-page gap so Ypagepixels is a whole number of scroll increments
        # and page numbers change precisely on a scroll click
        idiv = self.Ypagepixels/self.scrollrate
        nlo = idiv * self.scrollrate
        nhi = (idiv + 1) * self.scrollrate
        if nhi - self.Ypagepixels < self.Ypagepixels - nlo:
            self.Ypagepixels = nhi
        else:
            self.Ypagepixels = nlo
        self.page_gap = self.Ypagepixels/self.scale - self.pageheight

        self.maxwidth = max(self.winwidth, self.Xpagepixels)
        self.maxheight = max(self.winheight, self.numpages*self.Ypagepixels)
        self.SetVirtualSize((self.maxwidth, self.maxheight))
        self.SetScrollRate(self.scrollrate, self.scrollrate)

        xv, yv = self.GetViewStart()
        dx, dy = self.GetScrollPixelsPerUnit()
        self.x0, self.y0   = (xv * dx, yv * dy)
        self.frompage = int(min(self.y0/self.Ypagepixels, self.numpages-1))
        self.topage = int(min((self.y0+self.winheight-1)/self.Ypagepixels, self.numpages-1))
        self.pagebufferwidth = max(self.Xpagepixels, self.winwidth)
        self.pagebufferheight = (self.topage - self.frompage + 1) * self.Ypagepixels

        # Inform buttonpanel controls of any changes
        if self.buttonpanel:
            self.buttonpanel.Update(self.frompage, self.numpages,
                                      self.scale/device_scale)

        self.page_y0 = self.frompage * self.Ypagepixels
        self.page_x0 = 0
        self.xshift = self.x0 - self.page_x0
        self.yshift = self.y0 - self.page_y0
        if not self.page_buffer_valid:  # via external setting
            self.cur_frompage = self.frompage
            self.cur_topage = self.topage
        else:   # page range unchanged? whole visible area will always be inside page buffer
            if self.frompage != self.cur_frompage or self.topage != self.cur_topage:
                self.page_buffer_valid = False    # due to page buffer change
                self.cur_frompage = self.frompage
                self.cur_topage = self.topage
        return
    
class mupdfProcessor(mupdfProcessor):
    def RenderPage(self, gc, pageno, scale=1.0):
        " Render the set of pagedrawings into gc for specified page "
        page = self.pdfdoc.loadPage(pageno)
        matrix = fitz.Matrix(scale, scale)
        try:
            pix = page.getPixmap(matrix=matrix)   # MUST be keyword arg(s)
            # 変更部分
            if [int(v) for v in fitz.version[1].split('.')] >= [1,15,0]:
                bmp = wx.Bitmap.FromBuffer(pix.width, pix.height, pix.samples)
            else:
                bmp = wx.Bitmap.FromBufferRGBA(pix.width, pix.height, pix.samples)
            gc.DrawBitmap(bmp, 0, 0, pix.width, pix.height)
            self.zoom_error = False
        except (RuntimeError, MemoryError):
            if not self.zoom_error:     # report once only
                self.zoom_error = True
                dlg = wx.MessageDialog(self.parent, 'Out of memory. Zoom level too high?',
                              'pdf viewer' , wx.OK |wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
#-------------------------------------------------------------------------------

shagantaishi="""\
回回回回回回回回回回回回回回回回回回回回回回回回回回回回回回
回　　　　　　　　　　　　　　　　　　　　　　　　　回
  回　　　　　　　　　　　　　　　　　　　　　　　回
    回　　　　　　　　　　　　　　　　　　　　　回
      回　　　　　　　　　　　　　　　　　　　回
        回　　　　回回回回回回回回回回回回回回
          回　　　　回　　　　　　　　　　回
            回回　　　回　　　　　　　　回
            回　回　　　回　　　　　　回
            回　　回　　　回回回回回回
            回　　　回　　　　　　　　　　　　　　回
            回　　　　回　　　　回　　　　　　　回回
            回　　　　回　　　回　回　　　　　回　回
            回　　　　回　　回　　　回　　　回　　回
            回　　　　回　回　　　　　回　回　　　回
            回　　　　回　　回　　　回　　回　　　回
            回　　　　回　　　回　回　　　回　　　回
            回　　　回　　　　　回　　　　回　　　回
            回　　回　　　　　　　　　　　回　　　回
            回　回　　　　　　　　　　　　回　　　回
            回回　　　　　　　　　　　　　回　　　回
            回　　　　　　　　　　　　　　回　　　回
                    回回回回回回回　　　　回　　  回
                  回　　　　　　　回　　　　回　  回
                回　　　　　　　　　回　　　　回  回
              回　　　　　　　　　　　回　　　　回回
            回回回回回回回回回回回回回回回　　　　回
          回　　　　　　　　　　　　　　　　　　　　回
        回　　　　　　　　　　　　　　　　　　　　　　回　
回回回回回回回回回回回回回回回回回回回回回回回回回回回回回\
"""

papurika="""\
うん。必ずしも泥棒が悪いとはお地蔵様も言わなかった。
パプリカのビキニより、ＤＣミニの回収に漕ぎ出すことが幸せの秩序です。
五人官女だってです！
カエルたちの笛や太鼓に合わせて回収中の不燃ゴミが吹き出してくる様は圧巻で、
まるでコンピューター・グラフィックスなんだ、それが！
総天然色の青春グラフィティや一億総プチブルを私が許さないことくらいオセアニアじゃあ常識なんだよ！

今こそ、青空に向かって凱旋だ！

絢爛たる紙吹雪は鳥居をくぐり、周波数を同じくするポストと冷蔵庫は先鋒をつかさどれ！
賞味期限を気にする無頼の輩は花電車の進む道にさながらシミとなってはばかることはない！
思い知るがいい！三角定規たちの肝臓を！
さぁ!この祭典こそ内なる小学３年生が決めた遙かなる望遠カメラ！

進め！集まれ！
私こそが！
お代官様！
すぐだ！
すぐにもだ！　　　　　　　　　　　　　　　　　　　　　
わたしを迎エいれるノだ！！\
"""
#-------------------------------------------------------------------------------
def check_encoding(file_path):
    from chardet.universaldetector import UniversalDetector
    detector = UniversalDetector()
    with open(file_path, mode='rb') as f:
        for binary in f:
            detector.feed(binary)
            if detector.done:
                break
    detector.close()
    return detector.result['encoding']
#-------------------------------------------------------------------------------

class MyBrowser(wx.Dialog): 
  def __init__(self, url): 
    super().__init__(None,wx.ID_ANY,"HTML変換画面", size=(700, 700))
    self.browser = wx.html2.WebView.New(self)
    self.browser.LoadURL(url)
    self.ShowModal()
#-------------------------------------------------------------------------------

class Notebook(aui.AuiNotebook):
    def __init__(self,parent,style):
        super().__init__(parent,style)

    def AddPage(self, page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap, control=None, tooltip="",
                file_type="txt", path=None, encoding=None, name=""):
        return self.InsertPage(self.GetPageCount(), page, caption, select, bitmap, disabled_bitmap, control, tooltip, file_type, path, encoding, name)

    def InsertPage(self, page_idx, page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap, control=None, tooltip="",
                   file_type="txt", path=None, encoding=None, name=""):
        from wx.lib.agw.aui import framemanager

        if not page:
            return False

        page.Reparent(self)
        info = aui.AuiNotebookPage()
        info.window = page
        
        info.window.file_type = file_type
        info.window.file_path = path
        info.window.file_encoding = encoding
        info.window.file_name = name
        # 拡張子の確認
        root, info.window.ext = os.path.splitext(name)
        if info.window.ext=='':
            info.window.ext = '.txt'
        
        info.caption = caption
        info.bitmap = bitmap
        info.active = False
        info.control = control
        info.tooltip = tooltip

        originalPaneMgr = framemanager.GetManager(page)
        if originalPaneMgr:
            originalPane = originalPaneMgr.GetPane(page)

            if originalPane:
                info.hasCloseButton = originalPane.HasCloseButton()

        if bitmap.IsOk() and not disabled_bitmap.IsOk():
            disabled_bitmap = MakeDisabledBitmap(bitmap)

        info.dis_bitmap = disabled_bitmap

        # if there are currently no tabs, the first added
        # tab must be active
        if self._tabs.GetPageCount() == 0:
            info.active = True

        self._tabs.InsertPage(page, info, page_idx)

        # if that was the first page added, even if
        # select is False, it must become the "current page"
        # (though no select events will be fired)
        if not select and self._tabs.GetPageCount() == 1:
            select = True

        active_tabctrl = self.GetActiveTabCtrl()
        if page_idx >= active_tabctrl.GetPageCount():
            active_tabctrl.AddPage(page, info)
        else:
            active_tabctrl.InsertPage(page, info, page_idx)

        force = False
        if control:
            force = True
            control.Reparent(active_tabctrl)
            control.Show()

        self.UpdateTabCtrlHeight(force=force)
        self.DoSizing()
        active_tabctrl.DoShowHide()

        # adjust selected index
        if self._curpage >= page_idx:
            self._curpage += 1

        if select:
            self.SetSelectionToWindow(page)

        return True

#-------------------------------------------------------------------------------

class TextCtrl(wx.Panel):
    def __init__(self,parent,text=""):
        super().__init__(parent,wx.ID_ANY)

        self.textctrl = wx.TextCtrl(self,wx.ID_ANY,value=text,style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
        self.textctrl.SetFont(wx.Font(
            pointSize = 10,
            family    = wx.FONTFAMILY_TELETYPE, # https://wxpython.org/Phoenix/docs/html/wx.FontFamily.enumeration.html
            style     = wx.FONTSTYLE_NORMAL,    # https://wxpython.org/Phoenix/docs/html/wx.FontStyle.enumeration.html
            weight    = wx.FONTWEIGHT_NORMAL    # https://wxpython.org/Phoenix/docs/html/wx.FontWeight.enumeration.html
            ))

        self.ruler1 = rc.RulerCtrl(self, -1, orient=wx.HORIZONTAL, style=wx.SUNKEN_BORDER)
        self.ruler2 = rc.RulerCtrl(self, -1, orient=wx.VERTICAL, style=wx.SUNKEN_BORDER)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        bottomleftsizer = wx.BoxSizer(wx.HORIZONTAL)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)

        leftsizer.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
        topsizer.Add((39, 0), 0, wx.ADJUST_MINSIZE, 0)
        topsizer.Add(self.ruler1, 1, wx.EXPAND, 0)
        leftsizer.Add(topsizer, 0, wx.EXPAND, 0)

        bottomleftsizer.Add((10, 0))
        bottomleftsizer.Add(self.ruler2, 0, wx.EXPAND, 0)
        bottomleftsizer.Add(self.textctrl, 1, wx.EXPAND, 0)
        leftsizer.Add(bottomleftsizer, 1, wx.EXPAND, 0)
        mainsizer.Add(leftsizer, 3, wx.EXPAND, 0)

        self.SetSizer(mainsizer)

#-------------------------------------------------------------------------------

import wx.lib.mixins.listctrl as listmix
class Table(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self,parent,path,data,ext,header):
        super().__init__(parent,wx.ID_ANY,style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        listmix.TextEditMixin.__init__(self)

        self.SetHeaderAttr(wx.ItemAttr(
            wx.Colour(colRGB=0),
            wx.Colour(colRGB=255),
            wx.Font(wx.FontInfo(10))
            )) # New in version 4.1/wxWidgets-3.1.1.

        # データを読み込んで表示
        for row,d in enumerate(data):
            if ext in (".pickle",".txt"):
                if header:
                    if row == 0:
                        self.add_header(d.keys())
                    self.add_row(row,d.values())
                else:
                    if row == 0:
                        self.add_header(["列{}".format(i+1) for i in range(len(d))])
                    self.add_row(row-1,d)
            else:
                if row == 0:
                    if header:
                        self.add_header(d)
                    else:
                        self.add_header(["列{}".format(i+1) for i in range(len(d))])
                else:
                    self.add_row(row-1,d)

    def add_header(self,data):
        for no,d in enumerate(data):
            self.InsertColumn(no,d)

    def add_row(self,row,data):
        for no,d in enumerate(data):
            if no == 0:
                #self.InsertStringItem(row,d) 
                self.InsertItem(row,str(d)) 
            else:
                #self.SetStringItem(row,no,d) 
                self.SetItem(row,no,str(d)) 

#-------------------------------------------------------------------------------

class PDF(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent,wx.ID_ANY)
        layout = wx.BoxSizer(wx.VERTICAL)

        self.buttonpanel =  pdfButtonPanel(self,
                                      wx.ID_ANY,
                                      wx.DefaultPosition,
                                      wx.DefaultSize,
                                      0)
        layout.Add(self.buttonpanel,0,
                   wx.GROW|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        self.viewer = pdfViewer(self,
                                wx.ID_ANY,
                                wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        layout.Add(self.viewer,1,wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        self.SetSizer(layout)
        self.SetAutoLayout(True)

        # Introduce buttonpanel and viewer to each other.
        """
        pdfButtonPanelにはviewer，
        pdfViewer　　 にはbuttonpanel　という変数がすでに用意されており，
        インスタンス化後，お互いを代入することで，連携され，
        PDFビューワのボタンが使えるようになります．
        以下をしない，もしくは別の変数に代入すると，
        ボタンは表示されるものの，連携していないため使えません．

        """
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel
        
#-------------------------------------------------------------------------------

class MediaCtrl(wx.Panel):
    def __init__(self,parent):
        super().__init__(parent,wx.ID_ANY)
        
        if pf == 'Windows':
            szBackend = wx.media.MEDIABACKEND_DIRECTSHOW
        elif pf == 'Darwin':
            szBackend = wx.media.MEDIABACKEND_QUICKTIME
        elif pt == 'Linux':
            szBackend = wx.media.MEDIABACKEND_GSTREAMER

        """
        上記以外にszBackendに指定できるもの
        ・MEDIABACKEND_MCI        
        ・MEDIABACKEND_REALPLAYER 
        ・MEDIABACKEND_WMP10
        """
            
        self.media = wx.media.MediaCtrl(self,style=wx.SIMPLE_BORDER,szBackend=szBackend)
        

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.media, 3, wx.EXPAND, 0)

        # szBackend依存のコントロールボタンバーの作成
        self.media.ShowPlayerControls()
        """
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK,self.switch_ShowPlayerControls)
        self.Bind(wx.EVT_RIGHT_UP,self.switch_ShowPlayerControls)
        self.switch_ShowPlayerControls_state = True
        """        
        self.SetSizer(mainsizer)
        # 再生が終わったらイベント処理
        self.Bind(wx.media.EVT_MEDIA_STOP, self.OnMediaStop, self.media)
        self.loop_play = False

    # 再生
    def play(self,event):
        #if event == wx.media.EVT_MEDIA_PLAY:
        self.media.Play()
        self.media.SetVolume(0.5)
    # 停止
    def stop(self,event):
        self.media.Stop()
    # 一時停止
    def pause(self,event):
        if event == wx.media.EVT_MEDIA_PAUSE:
            self.media.Pause()

    def OnMediaStop(self,event):
        if self.loop_play:
            self.media.Play()
        else:
            self.media.Stop()

    """
    def self.switch_ShowPlayerControls(self,event):
        self.media.ShowPlayerControls(frags=wx.media.MEDIACTRLPLAYERCONTROLS_NONE)
    """
#-------------------------------------------------------------------------------
class WordBox(wx.Dialog):
    
    def ok(self,event):
        self.process = True
        if self.title == "置換":
            self.text1 = self.text1.GetValue()
            self.text2 = self.text2.GetValue()
        else:
            self.text = self.text.GetValue()
        self.Destroy()

    def cancel(self,event):
        self.process = False
        self.Destroy()

    def __init__(self,title):
        self.title = title
        if title == "置換":
            super().__init__(None,wx.ID_ANY,title, size=(250, 130))
            root_panel = wx.Panel(self, wx.ID_ANY)

            # text
            text1_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
            self.text1 = wx.TextCtrl(text1_panel,wx.ID_ANY,size=(150,25))
            # text
            text2_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,30),size=(200,30))
            self.text2 = wx.TextCtrl(text2_panel,wx.ID_ANY,size=(150,25))
            
            # button
            btn_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,90),size=(200,30))
            button_ok =  wx.Button(btn_panel,label="OK")
            button_ok.Bind(wx.EVT_BUTTON,self.ok)
            button_can = wx.Button(btn_panel,label="CANCEL")
            button_can.Bind(wx.EVT_BUTTON,self.cancel)

            btn_layout = wx.BoxSizer(wx.HORIZONTAL)
            btn_layout.Add(button_ok,1, wx.GROW)
            btn_layout.Add(button_can,1, wx.GROW)
            btn_panel.SetSizer(btn_layout)

            self.Bind(wx.EVT_CLOSE,self.cancel)

            # layout
            root_layout = wx.BoxSizer(wx.VERTICAL)
            root_layout.Add(text1_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(text2_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(btn_panel,0,wx.ALL|wx.CENTER)
            root_panel.SetSizer(root_layout)
            root_layout.Fit(root_panel)
          
        else:
            super().__init__(None,wx.ID_ANY,title, size=(250, 100))
            root_panel = wx.Panel(self, wx.ID_ANY)

            # text
            text_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
            self.text = wx.TextCtrl(text_panel,wx.ID_ANY,size=(150,25))
        
            # button
            btn_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,60),size=(200,30))
            button_ok =  wx.Button(btn_panel,label="OK")
            button_ok.Bind(wx.EVT_BUTTON,self.ok)
            button_can = wx.Button(btn_panel,label="CANCEL")
            button_can.Bind(wx.EVT_BUTTON,self.cancel)

            btn_layout = wx.BoxSizer(wx.HORIZONTAL)
            btn_layout.Add(button_ok,1, wx.GROW)
            btn_layout.Add(button_can,1, wx.GROW)
            btn_panel.SetSizer(btn_layout)

            self.Bind(wx.EVT_CLOSE,self.cancel)

            # layout
            root_layout = wx.BoxSizer(wx.VERTICAL)
            root_layout.Add(text_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(btn_panel,0,wx.ALL|wx.CENTER)
            root_panel.SetSizer(root_layout)
            root_layout.Fit(root_panel)

        self.ShowModal()
#-------------------------------------------------------------------------------
class WordBox(wx.Dialog):
    
    def ok(self,event):
        self.process = True
        if self.title == "全置換":
            self.text1 = self.text1.GetValue()
            self.text2 = self.text2.GetValue()
        else:
            self.text = self.text.GetValue()
        self.Destroy()

    def cancel(self,event):
        self.process = False
        self.Destroy()

    def __init__(self,title):
        self.title = title
        if title == "全置換":
            super().__init__(None,wx.ID_ANY,title, size=(250, 130))
            root_panel = wx.Panel(self, wx.ID_ANY)

            # text
            text1_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
            self.text1 = wx.TextCtrl(text1_panel,wx.ID_ANY,size=(150,25))
            # text
            text2_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,30),size=(200,30))
            self.text2 = wx.TextCtrl(text2_panel,wx.ID_ANY,size=(150,25))
            
            # button
            btn_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,90),size=(200,30))
            button_ok =  wx.Button(btn_panel,label="OK")
            button_ok.Bind(wx.EVT_BUTTON,self.ok)
            button_can = wx.Button(btn_panel,label="CANCEL")
            button_can.Bind(wx.EVT_BUTTON,self.cancel)

            btn_layout = wx.BoxSizer(wx.HORIZONTAL)
            btn_layout.Add(button_ok,1, wx.GROW)
            btn_layout.Add(button_can,1, wx.GROW)
            btn_panel.SetSizer(btn_layout)

            self.Bind(wx.EVT_CLOSE,self.cancel)

            # layout
            root_layout = wx.BoxSizer(wx.VERTICAL)
            root_layout.Add(text1_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(text2_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(btn_panel,0,wx.ALL|wx.CENTER)
            root_panel.SetSizer(root_layout)
            root_layout.Fit(root_panel)
          
        else:
            super().__init__(None,wx.ID_ANY,title, size=(250, 100))
            root_panel = wx.Panel(self, wx.ID_ANY)

            # text
            text_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
            self.text = wx.TextCtrl(text_panel,wx.ID_ANY,size=(150,25))
        
            # button
            btn_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,60),size=(200,30))
            button_ok =  wx.Button(btn_panel,label="OK")
            button_ok.Bind(wx.EVT_BUTTON,self.ok)
            button_can = wx.Button(btn_panel,label="CANCEL")
            button_can.Bind(wx.EVT_BUTTON,self.cancel)

            btn_layout = wx.BoxSizer(wx.HORIZONTAL)
            btn_layout.Add(button_ok,1, wx.GROW)
            btn_layout.Add(button_can,1, wx.GROW)
            btn_panel.SetSizer(btn_layout)

            self.Bind(wx.EVT_CLOSE,self.cancel)

            # layout
            root_layout = wx.BoxSizer(wx.VERTICAL)
            root_layout.Add(text_panel,0,wx.ALL|wx.CENTER)
            root_layout.Add(btn_panel,0,wx.ALL|wx.CENTER)
            root_panel.SetSizer(root_layout)
            root_layout.Fit(root_panel)

        self.ShowModal()
#-------------------------------------------------------------------------------
def input_word(title):
    wordbox = WordBox(title)
    if wordbox.process:
        if title == "全置換":
            return wordbox.text1,wordbox.text2
        else:
            return wordbox.text
    else:
        if title == "全置換":
            return False,False
        else:
            return False
#-------------------------------------------------------------------------------
class TextBox(wx.Dialog):
    
    def ok(self,event):
        #print("ok")
        self.text = self.text.GetValue()
        self.encoding = self.combobox.GetStringSelection()
        self.Destroy()

    def cancel(self,event):
        #print("cancel")
        #print(self.combobox.GetStringSelection())
        self.text = None
        self.encoding = None
        self.Destroy()
    #---------------------------------------------------------------------------
    def __init__(self,name=""):
        super().__init__(None,wx.ID_ANY,'ファイル名を入力してください', size=(250, 150))
        root_panel = wx.Panel(self, wx.ID_ANY)

        # text
        text_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
        self.text = wx.TextCtrl(text_panel,wx.ID_ANY,name,size=(200,25))
        
        # ComboBox
        ComboBox_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,30),size=(200,30))
        self.combobox = wx.ComboBox(
            ComboBox_panel,
            wx.ID_ANY,
            '選択してください',
            choices=(
                "utf-8",
                "shift-jis",
                "cp932"
                ),
            style=wx.CB_READONLY)
        self.combobox.SetValue("utf-8")
        
        # button
        btn_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,60),size=(200,30))
        button_ok =  wx.Button(btn_panel,label="OK")
        button_ok.Bind(wx.EVT_BUTTON,self.ok)
        button_can = wx.Button(btn_panel,label="CANCEL")
        button_can.Bind(wx.EVT_BUTTON,self.cancel)

        btn_layout = wx.BoxSizer(wx.HORIZONTAL)
        btn_layout.Add(button_ok,1, wx.GROW)
        btn_layout.Add(button_can,1, wx.GROW)
        btn_panel.SetSizer(btn_layout)

        self.Bind(wx.EVT_CLOSE,self.cancel)

        # layout
        root_layout = wx.BoxSizer(wx.VERTICAL)
        root_layout.Add(text_panel,0,wx.ALL|wx.CENTER)
        root_layout.Add(ComboBox_panel,0,wx.ALL|wx.CENTER)
        root_layout.Add(btn_panel,0,wx.ALL|wx.CENTER)
        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

        self.ShowModal()
#-------------------------------------------------------------------------------
def input_file_name(name=""):
    textbox = TextBox(name)
    if textbox.text == None:
        return None,None
    else:
        text = textbox.text
        encoding = textbox.encoding
        #print(text,encoding)
        return text,encoding
#-------------------------------------------------------------------------------
class textpad(wx.Frame):
    #---------------------------------------------------------------------------    
    def convert_to_html(self):

        html_header = '''\
            <head>
                <meta http-equiv="Content-Type" content="text/html" charset="utf-8">
                <title>{}</title>
                <link crossorigin="anonymous" media="all" rel="stylesheet" type="text/css" href="github-frameworks.css">
                <link crossorigin="anonymous" media="all" rel="stylesheet" type="text/css" href="github-site.css">
                <link crossorigin="anonymous" media="all" rel="stylesheet" type="text/css" href="github.css">
            </head>\
            '''.format(self.notebook.GetCurrentPage().file_name)

        if self.notebook.GetCurrentPage().file_type == "txt":
            html_text = self.notebook.GetCurrentPage().textctrl.GetValue()

            if self.notebook.GetCurrentPage().ext == ".txt":
                html_text = html_text.replace("\n", "<br>")
                html_text = html_text.replace(" ","&nbsp;")
                html_text = html_text.replace("　","&nbsp;&nbsp;")
                html_text = html_text.replace("'","&#39;")
            elif self.notebook.GetCurrentPage().ext in (".md",".html"):
                dialog = wx.MessageDialog(None, 'コードのまま出力しますか？', '確認',style=wx.YES_NO | wx.ICON_INFORMATION)
                res = dialog.ShowModal()
                if res == wx.ID_YES:
                    html_text = html_text.replace("'","&#39;")
                    text = '<table class="highlight tab-size js-file-line-container" data-tab-size="8" data-paste-markdown-skip>'
                    for row,line in enumerate(html_text.split('\n')):
                        text += '''\
                            <tr>
                                <td id="L{0}" class="blob-num js-line-number" data-line-number="{0}">{0}</td>
                                <td id="LC{0}" class="blob-code blob-code-inner js-file-line">{1}</td>
                            </tr>\
                            '''.format(row+1,line)
                    text += '</table>'
                    html_text = text
                    del text
                elif res == wx.ID_NO:
                    if self.notebook.GetCurrentPage().ext == ".md":
                        import markdown
                        from markdown.extensions.tables import TableExtension
                        from markdown.extensions.codehilite import CodeHiliteExtension
                        html_text = markdown.markdown(html_text,extensions=[
                            TableExtension(),
                            CodeHiliteExtension()
                            ])

                        html_text = html_text.replace("<p><code>",'<div class="highlight highlight-source-shell"><pre><code>')
                        html_text = html_text.replace("</code></p>",'</code></pre></div>')
                        print(html_text)
                    else:
                        html_text = html_text.replace("\n", "<br>")
            else:
                text = '<table class="highlight tab-size js-file-line-container" data-tab-size="8" data-paste-markdown-skip>'
                for row,line in enumerate(html_text.split('\n')):
                    text += '''\
                        <tr>
                            <td id="L{0}" class="blob-num js-line-number" data-line-number="{0}">{0}</td>
                            <td id="LC{0}" class="blob-code blob-code-inner js-file-line">{1}</td>
                        </tr>\
                        '''.format(row+1,line)
                text += '</table>'
                html_text = text
                del text

        elif self.notebook.GetCurrentPage().file_type=="table":
            html_text = '<table>'

            html_text += "<tr>"
            for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                html_text += '<th>{}</th>'.format(self.notebook.GetCurrentPage().GetColumn(j).GetText())
            html_text += "</tr>"

            for i in range(self.notebook.GetCurrentPage().GetItemCount()):
                html_text += "<tr>"
                for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                    html_text += "<td>{}</td>".format(self.notebook.GetCurrentPage().GetItem(i,j).GetText())
                html_text += "</tr>"
            html_text += '</table>'

        html_body = """\
            <body class="logged-out env-production page-responsive f4">
                    <article class="markdown-body entry-content" itemprop="text">
                        {}
                    </article>
            </body>\
            """.format(html_text)
    
        html = "<!DOCTYPE html><html>" + html_header + html_body + "</html>"
        #print(html)
        return html
    #---------------------------------------------------------------------------    
    def printer(self):
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path,"printout.html")
        with open(path,mode="w",encoding="utf-8") as f:
            f.write(self.convert_to_html())
                
        printer = MyBrowser("file:///" + "/".join(path.split(os.path.sep)))
        printer.browser.Print()
        
        return
    #---------------------------------------------------------------------------    
    def yes_or_no(self,message,caption):
        answer = wx.MessageBox(
            message=message,
            caption=caption,
            style=wx.YES_NO
            )
        if answer == wx.YES:
            return True
        else:
            return False
    #---------------------------------------------------------------------------    
    def status_update(self,event):
        # メニューバーのon/off

        """
        if self.notebook.GetCurrentPage().file_type=="audio":
            self.menu_bar.Enable(20,True)
            self.menu_bar.Enable(21,True)
            self.menu_bar.Enable(22,True)
            self.menu_bar.Enable(23,True)
        else:
            self.menu_bar.Enable(20,False)
            self.menu_bar.Enable(21,False)
            self.menu_bar.Enable(22,False)
            self.menu_bar.Enable(23,False)
        """

        
        # 動画・音楽ファイルのタブのとき
        if self.notebook.GetCurrentPage().file_type=="audio":
            self.sb.SetStatusText('{}'.format(
                self.notebook.GetCurrentPage().file_path
                ),0)
            if self.notebook.GetCurrentPage().media.State == 2:
                self.sb.SetStatusText('Playing/Volume:{}%'.format(
                    int(self.notebook.GetCurrentPage().media.Volume*100)
                    ),1)
            elif self.notebook.GetCurrentPage().media.State == 1:
                self.sb.SetStatusText('Pause/Volume:{}%'.format(
                    int(self.notebook.GetCurrentPage().media.Volume*100)
                    ),1)
            elif self.notebook.GetCurrentPage().media.State == 0:
                self.sb.SetStatusText('Stopping/Volume:{}%'.format(
                    int(self.notebook.GetCurrentPage().media.Volume*100)
                    ),1)
            else:
                self.sb.SetStatusText('Volume:{}%'.format(
                    int(self.notebook.GetCurrentPage().media.Volume*100)
                    ),1)
            self.sb.SetStatusText(self.notebook.GetCurrentPage().file_name,2)

        # 表形式のファイルのタブのとき
        elif self.notebook.GetCurrentPage().file_type=="table":
            if self.notebook.GetCurrentPage().file_path:
                self.sb.SetStatusText('{}'.format(
                    self.notebook.GetCurrentPage().file_path
                    ),0)
            else:
                self.sb.SetStatusText('{}'.format(
                    self.notebook.GetPageText(self.notebook.GetSelection())
                    ),0)
            if self.notebook.GetCurrentPage().GetFocusedItem() == -1:
                self.sb.SetStatusText('',1)
            else:
                self.sb.SetStatusText('{}行目'.format(self.notebook.GetCurrentPage().GetFocusedItem()+1),1)
            if self.notebook.GetCurrentPage().file_encoding:
                self.sb.SetStatusText('エンコード：{}'.format(
                    self.notebook.GetCurrentPage().file_encoding
                    ),2)
            else:
                self.sb.SetStatusText('エンコード設定していません',2)

        # Webページのタブのとき
        elif self.notebook.GetCurrentPage().file_type=="url":
            self.sb.SetStatusText(self.notebook.GetCurrentPage().GetCurrentURL(),0)
            self.sb.SetStatusText("url load",1)
            self.sb.SetStatusText(self.notebook.GetCurrentPage().GetCurrentTitle(),2)
            self.notebook.SetPageText(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()),self.notebook.GetCurrentPage().GetCurrentTitle())

        # PDFのタブのとき
        elif self.notebook.GetCurrentPage().file_type=="pdf":
            self.sb.SetStatusText("計{}ページ".format(self.notebook.GetCurrentPage().viewer.numpages),0)
            self.sb.SetStatusText("pdf load",1)
            self.sb.SetStatusText("",2)
            
        # テキスト系ファイルのタブのとき
        else:
            text = re.sub(r"\s","",self.notebook.GetCurrentPage().textctrl.GetValue())

            pos  = self.notebook.GetCurrentPage().textctrl.PositionToXY(
                self.notebook.GetCurrentPage().textctrl.GetSelection()[0]
                )
            #print(self.notebook.GetSelection(),len(text),pos)
            if self.notebook.GetCurrentPage().file_path:
                self.sb.SetStatusText('{}'.format(
                    self.notebook.GetCurrentPage().file_path
                    ),0)
            else:
                self.sb.SetStatusText('{}'.format(
                    self.notebook.GetPageText(self.notebook.GetSelection())
                    ),0)
            
            self.sb.SetStatusText('{0}行{1}列　計：{2}文字'.format(
                pos[2],
                pos[1],
                len(text)
                ),1)
            if self.notebook.GetCurrentPage().file_encoding:
                self.sb.SetStatusText('エンコード：{}'.format(
                    self.notebook.GetCurrentPage().file_encoding
                    ),2)
            else:
                self.sb.SetStatusText('エンコード設定していません',2)
    #---------------------------------------------------------------------------
    def textctrl_make(self,text=None,path=None,encoding=None,name='新しいテキスト',title='新しいテキスト'):
        
        if text:
            page = TextCtrl(
                    self.notebook,
                    text=text
                    )
        else:
            page = TextCtrl(self.notebook)

        """
        InsertPageの場合，挿入位置を指定する必要があるが，
        基本的にAddPageと変わらない
        挿入位置を
        self.notebook.GetSelection()
        とした場合はAddPageとは違って選択中のページの前に挿入されていた

        どちらのメソッドも挿入後に選択されているページは
        挿入前に選択されていたページのままになっている
        """
        self.notebook.AddPage(
            page,
            title,
            path=path,
            encoding=encoding,
            name=name
            )
    #---------------------------------------------------------------------------
    def save_file(self):
        # テキストファイルの場合
        if self.notebook.GetCurrentPage().file_type=="txt":
            with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
                f.write(self.notebook.GetCurrentPage().textctrl.GetValue())
        # 表ファイルの場合
        elif self.notebook.GetCurrentPage().file_type=="table":
            # pickleの場合，元のデータとは形式が変わってしまう可能性がある
            if self.notebook.GetCurrentPage().ext in (".pickle",".txt"):
                text = []
                keys = [] # headerの要素を格納
                # headerの読み込み
                for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                    keys.append(self.notebook.GetCurrentPage().GetColumn(j).GetText())
                # 行ごとに読み込んでいく
                for i in range(self.notebook.GetCurrentPage().GetItemCount()):
                    element = {}
                    for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                        element[keys[j]] = self.notebook.GetCurrentPage().GetItem(i,j).GetText()
                    text.append(element)

                if self.notebook.GetCurrentPage().ext == ".pickle":
                    # pickle化
                    with open(self.notebook.GetCurrentPage().file_path,mode="wb") as f:
                        pickle.dump(text,f)
                elif self.notebook.GetCurrentPage().ext == ".txt":
                    with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
                        pprint.pprint(text,stream=f)
            else:
                text = ""
                # headerの読み込み
                for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                    if j == 0:
                        text += '{}'.format(self.notebook.GetCurrentPage().GetColumn(j).GetText())
                        continue
                    if self.notebook.GetCurrentPage().ext == ".csv":
                        text += ',{}'.format(self.notebook.GetCurrentPage().GetColumn(j).GetText())
                    elif self.notebook.GetCurrentPage().ext == ".tsv":
                        text += '\t{}'.format(self.notebook.GetCurrentPage().GetColumn(j).GetText())
                text += "\n"
                # 行ごとに読み込んでいく
                for i in range(self.notebook.GetCurrentPage().GetItemCount()):
                    for j in range(self.notebook.GetCurrentPage().GetColumnCount()):
                        if j == 0:
                            text += "{}".format(self.notebook.GetCurrentPage().GetItem(i,j).GetText())
                            continue
                        if self.notebook.GetCurrentPage().ext == ".csv":
                            text += ",{}".format(self.notebook.GetCurrentPage().GetItem(i,j).GetText())
                        elif self.notebook.GetCurrentPage().ext == ".tsv":
                            text += "\t{}".format(self.notebook.GetCurrentPage().GetItem(i,j).GetText())
                    text += "\n"
                # 出力
                with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
                    f.write(text)
        # Webページの場合，そのページのソース＝htmlを保存
        elif self.notebook.GetCurrentPage().file_type=="url":
            with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
                f.write(self.notebook.GetCurrentPage().GetPageSource())            
    #---------------------------------------------------------------------------
    def save_file_path(self):
        # ファイル名を入力
        title,encoding = input_file_name(self.notebook.GetCurrentPage().file_name)
        if title == None:
            return False
        
        # フォルダ選択ダイアログを作成
        folda = wx.DirDialog(None,style=wx.DD_CHANGE_DIR | wx.OK | wx.STAY_ON_TOP,message="保存先フォルダ")
        # フォルダが選択されたとき
        if folda.ShowModal() == wx.ID_OK:
            # 拡張子の確認
            root, ext = os.path.splitext(title)
            # 拡張子なし＝＞テキストファイルとして保存
            if ext=='':
                self.notebook.GetCurrentPage().file_path = os.path.join(folda.GetPath(),title+'.txt')
            # 拡張子アリ
            else:
                self.notebook.GetCurrentPage().file_path = os.path.join(folda.GetPath(),title)
            self.notebook.GetCurrentPage().file_encoding = encoding
            self.notebook.GetCurrentPage().file_name = title
            folda.Destroy()
            # タブ名を変更
            self.notebook.SetPageText(self.notebook.GetSelection(), title)
            return True
        else:
            folda.Destroy()
            return False
    #---------------------------------------------------------------------------
    def close_event(self,event):
        # 確認
        dialog = wx.MessageDialog(None,"本当に終了してもいいですか？","確認",style=wx.YES_NO | wx.ICON_INFORMATION)
        res = dialog.ShowModal()
        if res == wx.ID_YES:
            # タブ一つ一つに対して行う
            while self.notebook.GetPageCount()>0:
                if self.notebook.GetCurrentPage().file_type=="audio":
                    self.notebook.GetCurrentPage().stop(wx.media.EVT_MEDIA_STOP)
                elif  self.notebook.GetCurrentPage().file_type in ("txt","table"):
                    # 保存の確認
                    if self.yes_or_no("終了前に保存しますか？","確認ダイアログ"):
                        # 名前を付けて保存
                        if self.notebook.GetCurrentPage().file_path==None:      
                            if self.save_file_path():
                                self.save_file() 
                            else:
                                wx.MessageBox(message="保存をキャンセルしました",caption="キャンセル",style=wx.OK)
            
                        # 上書き保存
                        else:
                            self.save_file()
                    # 保存しない場合
                    else:
                        pass
                self.notebook.DeletePage(self.notebook.GetSelection())
            # 終了
            sys.exit()
        elif res == wx.ID_NO:
            event.Veto()
            return
    #---------------------------------------------------------------------------
    def tab_close(self,event):
        if self.yes_or_no("本当にタブを閉じていいですか？","確認ダイアログ"):
            if self.notebook.GetCurrentPage().file_type=="audio":
                self.notebook.GetCurrentPage().stop(wx.media.EVT_MEDIA_STOP)
            if self.notebook.GetPageCount()==1:
                self.textctrl_make()
            else:
                pass
        else:
            event.Veto()
    #---------------------------------------------------------------------------
    def selectMenu(self,event):

        #-----------------------------------------------------------------------
        def read_textfile(name,path):
            data = ""
            read_size = 0

            progress = wx.ProgressDialog("読み込み中", "しばらくお待ちください"
                                        , maximum=os.path.getsize(path)
                                        , parent=None
                                        ,style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.STAY_ON_TOP
                                        )
            progress.Show()
            # ファイルの読み込み
            # LoadFileメソッドはテキストファイルだけなので，with構文でファイルを読み込む
            encoding = check_encoding(path)
            try:
                with open(path,mode="r",encoding=encoding) as f:
                    for line in f:
                        data += line
                        read_size += len(line.encode(encoding))
                        progress.Update(read_size)
            except UnicodeDecodeError:
                encoding="utf-8"
                with codecs.open(path,mode="r",encoding="utf-8",errors="backslashreplace") as f:
                    for line in f:
                        data += line
                        read_size += len(line.encode(encoding))
                        progress.Update(read_size)
            progress.Destroy() 
            
            # ファイルの内容を新しいタブで表示
            self.textctrl_make(
                text=data,
                path=path,
                encoding=encoding,
                name=name,
                title=name
                )

            # プログレスダイアログが消えても表示されるのに時間がかかる場合がある
        #-----------------------------------------------------------------------
        def read_table(path,ext):

            def shape(text):
                # 要素数が一定になるように整形する
                data = []
                for no,t in enumerate(text):
                    # set型なら読み込み中止
                    if type(t) == set:
                        return False
                    # 要素数を取得
                    if no == 0:
                        elements_cnt = len(t)
                        # dictの場合はキーも取得
                        if type(t) == dict:
                            keys = t.keys()
                            header = True
                        else:
                            header = False
                    if len(t) > elements_cnt:
                        # dictの場合
                        if type(t) == dict:
                            data.append({key:value for key,value in list(t.itemes())[:elements_cnt]})
                            t = {key:value for key,value in list(t.itemes())[elements_cnt:]}
                        # list，tupleの場合
                        else:
                            data.append(t[:elements_cnt])
                            t = t[elements_cnt:]
                        if len(t) > elements_cnt:
                            while len(t) > elements_cnt:
                                # dictの場合
                                if type(t) == dict:
                                    data.append({key:value for key,value in list(t.itemes())[:elements_cnt]})
                                    t = {key:value for key,value in list(t.itemes())[elements_cnt:]}
                                # list，tupleの場合
                                else:
                                    data.append(t[:elements_cnt])
                                    t = t[elements_cnt:]
                                if len(t) <= elements_cnt:
                                    # dictの場合
                                    if type(t) == dict:
                                        for key in keys:
                                            try:
                                                t[key]
                                            except KeyError:
                                                t[key] = ""
                                    # tupleの場合
                                    elif type(t) == tuple:
                                        t = t + ('' for i in range(elements_cnt-len(t)))
                                    # listの場合
                                    elif type(t) == list:
                                        t = t + ['' for i in range(elements_cnt-len(t))]
                                    data.append(t)
                                    break
                    else:
                        # dictの場合
                        if type(t) == dict:
                            for key in keys:
                                try:
                                    t[key]
                                except KeyError:
                                    t[key] = ""
                        # tupleの場合
                        elif type(t) == tuple:
                            t = t + ('' for i in range(elements_cnt-len(t)))
                        # listの場合
                        elif type(t) == list:
                            t = t + ['' for i in range(elements_cnt-len(t))]

                        data.append(t)

                return data,header
            
            #-------------------------------------------------------------------
            # pprintでtxtファイルとして保存していたファイルの読み込みの場合
            if ext == ".txt":
                encoding = check_encoding(path)
                text = ""
                read_size = 0

                progress = wx.ProgressDialog("読み込み中", "しばらくお待ちください"
                                             , maximum=os.path.getsize(path)
                                             , parent=None
                                             ,style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.STAY_ON_TOP
                                             )
                progress.Show()
                # ファイルの読み込み
                try:
                    with open(path,mode="r",encoding=encoding) as f:
                        for line in f:
                            text += line
                            read_size += len(line.encode(encoding))
                            progress.Update(read_size)
                except UnicodeDecodeError:
                    encoding="utf-8"
                    with codecs.open(path,mode="r",encoding="utf-8",errors="backslashreplace") as f:
                        for line in f:
                            text += line
                            read_size += len(line.encode('utf-8'))
                            progress.Update(read_size)
                text = ast.literal_eval(text)
                    
                # 要素数が一定になるように整形する
                data,header = shape(text)

                progress.Destroy() 
            #-------------------------------------------------------------------
            # pickleファイルの場合
            elif ext == ".pickle":
                encoding = None

                # ファイルの読み込み
                with open(path,mode="rb") as f:
                    text = pickle.load(f)
                    
                # 要素数が一定になるように整形する
                data,header = shape(text)
            #-------------------------------------------------------------------
            # csvファイル・tsvファイルの場合
            elif ext in (".csv",".tsv"):
                dialog = wx.MessageDialog(None, "ヘッダーはありますか？", caption="確認",style=wx.YES_NO)
                res = dialog.ShowModal()
                if res == wx.ID_YES:
                    header = True
                elif res == wx.ID_NO:
                    header = False
                dialog.Destroy()
                
                encoding = check_encoding(path)
                data = []
                elements_cnt = 0
                
                read_size = 0

                progress = wx.ProgressDialog("読み込み中", "しばらくお待ちください"
                                             , maximum=os.path.getsize(path)
                                             , parent=None
                                             ,style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.STAY_ON_TOP
                                             )
                progress.Show()
                # ファイルの読み込み
                try:
                    with open(path,mode="r",encoding=encoding) as f:
                        for no,line in enumerate(f):
                            # 改行だけの空白行をスキップ
                            if len(line) == 1:
                                continue
                            # 区切り文字で要素を区切る
                            if ext == ".csv":
                                d = line.split(",")
                            else:
                                d = line.split("   ")
                            # 要素数を取得
                            if no == 0:
                                elements_cnt = len(d)
                            # 要素数が一定になるように整形する
                            if len(d) > elements_cnt:
                                data.append(d[:elements_cnt])
                                d = d[elements_cnt:]
                                if len(d) > elements_cnt:
                                    while len(d) > elements_cnt:
                                        data.append(d[:elements_cnt])
                                        d = d[elements_cnt:]
                                        if len(d) <= elements_cnt:
                                            d = d + ['' for i in range(elements_cnt-len(d))]
                                            data.append(d)
                                            break
                                elif len(d) < elements_cnt:
                                    d = d + ['' for i in range(elements_cnt-len(d))]
                                    data.append(d)
                                else:
                                    data.append(d)
                            elif len(d) < elements_cnt:
                                d = d + ['' for i in range(elements_cnt-len(d))]
                                data.append(d)
                            else:
                                data.append(d)
                            read_size += len(line.encode(encoding))
                            progress.Update(read_size)
                
                except UnicodeDecodeError:
                    encoding="utf-8"
                    with codecs.open(path,mode="r",encoding="utf-8",errors="backslashreplace") as f:                        
                        for no,line in enumerate(f.readline()):
                            # 改行だけの空白行をスキップ
                            if len(line) == 1:
                                continue
                            # 区切り文字で要素を区切る
                            if ext == ".csv":
                                d = line.split(",")
                            else:
                                d = line.split("   ")
                            # 要素数を取得
                            if no == 0:
                                elements_cnt = len(d)
                            # 要素数が一定になるように整形する
                            if len(d) > elements_cnt:
                                data.append(d[:elements_cnt])
                                d = d[elements_cnt:]
                                if len(d) > elements_cnt:
                                    while len(d) > elements_cnt:
                                        data.append(d[:elements_cnt])
                                        d = d[elements_cnt:]
                                        if len(d) <= elements_cnt:
                                            d = d + ['' for i in range(elements_cnt-len(d))]
                                            data.append(d)
                                            break
                                elif len(d) < elements_cnt:
                                    d = d + ['' for i in range(elements_cnt-len(d))]
                                    data.append(d)
                                else:
                                    data.append(d)
                            elif len(d) < elements_cnt:
                                d = d + ['' for i in range(elements_cnt-len(d))]
                                data.append(d)
                            else:
                                data.append(d)
                            read_size += len(line.encode(encoding))
                            progress.Update(read_size)
                progress.Destroy()                
            else:
                return False

            page = Table(
                self.notebook,
                path,
                data,
                ext,
                header
                )
            self.notebook.AddPage(
                    page,
                    path.split(os.path.sep)[-1],
                    file_type="table",
                    path=path,
                    encoding = encoding,
                    name=path.split(os.path.sep)[-1]
                    )
            return True
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # 新規保存（ファイル出力）
        if event.GetId() == 1:
            if self.save_file_path():
                self.save_file() 
            else:
                wx.MessageBox(message="保存をキャンセルしました",caption="キャンセル",style=wx.OK)
        #-----------------------------------------------------------------------           
        # 上書き保存（ファイル出力）
        elif event.GetId() == 2:
            # まだ保存されていなかった場合（新規保存）
            if self.notebook.GetCurrentPage().file_path==None: 
                if self.save_file_path():
                    self.save_file() 
                else:
                    wx.MessageBox(message="保存をキャンセルしました",caption="キャンセル",style=wx.OK)
                    return
            else:
                pass
            # SaveFileメソッドではテキストファイルだけなのでwith構文で保存
            self.save_file()
            
            # 保存したので*を外す（タブ名を変更）
            self.notebook.SetPageText(self.notebook.GetSelection(), self.notebook.GetCurrentPage().file_name)
        #-----------------------------------------------------------------------            
        # ファイルを開く１
        elif event.GetId() in (3,4):
            # ファイル選択ダイアログを作成
            dialog = wx.FileDialog(None, u'ファイル選択してください', style=wx.FD_OPEN )
            # ファイルが選択されたとき
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                dialog.Destroy()
            #elif dialog.ShowModal() == wx.ID_CANCEL:
            else:
                dialog.Destroy()
                return
            name=path.split(os.path.sep)[-1]

            # （テキストとして）ファイルを開く
            if event.GetId() == 3:
                read_textfile(name,path)
            # （表として）ファイルを開く
            if event.GetId() == 4:
                root, ext = os.path.splitext(name)
                read_table(path,ext)
        #-----------------------------------------------------------------------            
        # ファイルを開く２
        elif event.GetId() == 5:
            # ファイル選択ダイアログを作成
            dialog = wx.FileDialog(None, u'ファイル選択してください', style=wx.FD_OPEN )
            dialog.SetWildcard(
                """\
                All file(*)|*|
                TXT file(*.txt)|*.txt|
                Markdown(*.md)|*.md|
                MP4 file(*.mp4)|*.mp4|
                MP3 file(*.mp3)|*.mp3|
                AVI file(*.avi)|*.avi|
                WAV file(*.wmv)|*.wav|
                CSV file(*.csv)|*.csv|
                TSV file(*.tsv)|*.tsv|
                PICKLE file(*.pickle)|*.pickle|
                PDF file(*.pdf)|*.pdf""")

            # ファイルが選択されたとき
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                dialog.Destroy()
            else:
                dialog.Destroy()
                return
            name=path.split(os.path.sep)[-1]
            
            # 拡張子の確認
            root, ext = os.path.splitext(name)
            #-------------------------------------------------------------
            # テキストファイルを開く
            if ext in (".txt",".md"):
                read_textfile(name,path)
            #-------------------------------------------------------------
            # 表ファイルを開く
            elif ext in (".csv",".tsv",".pickle"):   
                read_table(path,ext)
            #-------------------------------------------------------------
            # 音楽ファイルを開く
            elif ext in (".mp4",".mp3",".avi",".wav"):
                page = MediaCtrl(self.notebook)           
                if page.media.Load(path):
                    self.notebook.AddPage(
                        page,
                        path.split(os.path.sep)[-1],
                        file_type="audio",
                        path=path,
                        name=path.split(os.path.sep)[-1]
                        )
            #-------------------------------------------------------------
            # PDFファイルを開く
            elif ext == ".pdf":
                page = PDF(self.notebook)
                page.viewer.LoadFile(path)

                self.notebook.AddPage(
                        page,
                        path.split(os.path.sep)[-1],
                        file_type="pdf",
                        path=path,
                        name=path.split(os.path.sep)[-1]
                        )
            
        #-----------------------------------------------------------------------
        # Webページ開く
        elif event.GetId() == 6:
            word = input_word("検索")
            if word:
                page = wx.html2.WebView.New(self.notebook)
                page.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11)
                page.LoadURL(word)
                wx.Sleep(10)
                
                self.notebook.AddPage(
                    page,
                    "Web Page",
                    file_type="url"
                    )
                """
                UnboundLocalError: local variable 'focusRect' referenced before assignment

                が出ることがある．．．
                """
        #-----------------------------------------------------------------------           
        # 新規作成
        elif event.GetId() == 7:
            self.textctrl_make()
        #-----------------------------------------------------------------------
        # 印刷
        elif event.GetId() == 8:
            if self.notebook.GetCurrentPage().file_type in ("txt","table"):
                self.printer()
            elif self.notebook.GetCurrentPage().file_type in ("pdf","url"):
                self.notebook.GetCurrentPage().Print()
        #-----------------------------------------------------------------------
        # 終了
        elif event.GetId() == 9:
            self.close_event(wx.EVT_CLOSE)
        #-----------------------------------------------------------------------
        # コピー
        if event.GetId() == 10:
            # 文字列をコピー
            if self.notebook.GetCurrentPage().file_type=="txt":
                wx.TheClipboard.SetData(wx.TextDataObject(self.notebook.GetCurrentPage().textctrl.GetValue()))
                wx.TheClipboard.Flush()
                wx.TheClipboard.Close()
            # URLコピー
            elif self.notebook.GetCurrentPage().file_type=="url":
                wx.TheClipboard.SetData(wx.TextDataObject(self.notebook.GetCurrentPage().GetCurrentURL()))
                wx.TheClipboard.Flush()
                wx.TheClipboard.Close()
        #-----------------------------------------------------------------------
        # タブを閉じる
        elif event.GetId() == 18:
            if self.yes_or_no("本当にタブを閉じていいですか？","確認ダイアログ"):
                if self.notebook.GetPageCount()==1:
                    self.textctrl_make()
                else:
                    pass
                
                if self.notebook.GetCurrentPage().file_type=="audio":
                    self.notebook.GetCurrentPage().stop(wx.media.EVT_MEDIA_STOP)
                self.notebook.DeletePage(self.notebook.GetSelection())
            else:
                return
        #-----------------------------------------------------------------------
        # 全てのタブを閉じる
        elif event.GetId() == 19:
            # 確認
            if self.yes_or_no("本当に全てのタブを閉じていいですか？","確認ダイアログ"):
                # AttributeError: 'AuiNotebook' object has no attribute 'DeleteAllPages'
                #self.notebook.DeleteAllPages()

                while self.notebook.GetPageCount()>0:
                    if self.notebook.GetCurrentPage().file_type=="audio":
                        self.notebook.GetCurrentPage().stop(wx.media.EVT_MEDIA_STOP)
                    self.notebook.DeletePage(self.notebook.GetSelection())
                self.textctrl_make()
            else:
                return
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # おまけ
        #-----------------------------------------------------------------------
        # 回＝回
        elif event.GetId() == 24:
            self.textctrl_make(text=shagantaishi,name="遮眼大師",title="遮眼大師")
            page = MediaCtrl(self.notebook)
            if page.media.LoadURI("https://susumuhirasawa.com/free-music/media/CHTE-0081/02_shagan-daishi.mp3"):
                self.notebook.AddPage(
                    page,
                    "遮眼大師",
                    file_type="audio",
                    path="https://susumuhirasawa.com/free-music/media/CHTE-0081/02_shagan-daishi.mp3",
                    name="遮眼大師"
                    )
        #-----------------------------------------------------------------------
        # パプリカ
        elif event.GetId() == 25:
            self.textctrl_make(text=papurika,name="白虎野の娘",title="白虎野の娘")
            page = MediaCtrl(self.notebook)
            if page.media.LoadURI("https://susumuhirasawa.com/free-music/media/CHTE-0038/01_byakkoya-no-musume.mp3"):
                self.notebook.AddPage(
                    page,
                    "白虎野の娘",
                    file_type="audio",
                    path="https://susumuhirasawa.com/free-music/media/CHTE-0038/01_byakkoya-no-musume.mp3",
                    name="白虎野の娘"
                    )
        #-----------------------------------------------------------------------
        # ザマギ / マジカルDEATH
        elif event.GetId() == 26:
            page = wx.html2.WebView.New(self.notebook)
            page.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11)
            page.LoadURL("https://www.youtube.com/watch?v=qYkicwSeXw0")
            wx.Sleep(10)
            self.notebook.AddPage(
                page,
                "マジカルDEATH",
                file_type="url",
                path="https://www.youtube.com/watch?v=qYkicwSeXw0",
                name="マジカルDEATH"
                )

            #IsBackendAvailable
            
        # group_inou / THERAPY
        elif event.GetId() == 27:
            page = wx.html2.WebView.New(self.notebook)
            page.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11)
            page.LoadURL("https://www.youtube.com/watch?v=ACEBZ-KmuQo")
            wx.Sleep(10)
            self.notebook.AddPage(
                page,
                "group_inou / THERAPY",
                file_type="url",
                path="https://www.youtube.com/watch?v=ACEBZ-KmuQo",
                name="group_inou / THERAPY"
                )
        #-----------------------------------------------------------------------
        # ファイルの種類によってしか発動しないメニュー
        #-----------------------------------------------------------------------
        # urlの場合だけのメニュー
        elif self.notebook.GetCurrentPage().file_type=="url":
            # Undo
            if event.GetId() == 14:
                self.notebook.GetCurrentPage().Undo()
            # Redo
            elif event.GetId() == 15:
                self.notebook.GetCurrentPage().Redo()
            # Paste
            elif event.GetId() == 16:
                self.notebook.GetCurrentPage().Paste()
            # Cut
            elif event.GetId() == 17:
                self.notebook.GetCurrentPage().SelectAll()
                self.notebook.GetCurrentPage().Cut()
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # txtの場合だけのメニュー
        elif self.notebook.GetCurrentPage().file_type=="txt":
            #-------------------------------------------------------------            
            # 検索
            if event.GetId() == 11:
                self.search_word = input_word("検索")
                if self.search_word:
                    self.search_word_pos = self.notebook.GetCurrentPage().textctrl.GetValue().find(self.search_word)
                    # 文字を選択状態にする
                    self.notebook.GetCurrentPage().textctrl.SetSelection(
                        from_=self.search_word_pos,
                        to_=self.search_word_pos+len(self.search_word)
                        )
            # 次を検索
            elif event.GetId() == 12:
                self.search_word_pos=self.notebook.GetCurrentPage().textctrl.GetValue().find(self.search_word,self.search_word_pos+1)
                # 次の候補がなかった場合，通常の検索と同じ
                if self.search_word_pos == -1:
                    self.search_word_pos = self.notebook.GetCurrentPage().textctrl.GetValue().find(self.search_word)
                # 文字の選択状態を解除
                self.notebook.GetCurrentPage().textctrl.SelectNone()
                #print(self.search_word_pos)
                # 文字を選択状態にする
                self.notebook.GetCurrentPage().textctrl.SetSelection(
                    from_=self.search_word_pos,
                    to_=self.search_word_pos+len(self.search_word)
                    )
            #--------------------------------------------------------------            
            # 全置換
            elif event.GetId() == 13:
                """
                self.notebook.GetCurrentPage().textctrl.Replace(from_, to_,str)
                という置換方法もあるが，置換位置が必要であり，本作では実装しない．
                """ 
                w1,w2 = input_word("全置換")
                if w1:
                    self.notebook.GetCurrentPage().textctrl.SetValue(self.notebook.GetCurrentPage().textctrl.GetValue().replace(w1,w2))
            #--------------------------------------------------------------            
            # Undo
            elif event.GetId() == 14:
                self.notebook.GetCurrentPage().textctrl.Undo()
            # Redo
            elif event.GetId() == 15:
                self.notebook.GetCurrentPage().textctrl.Redo()
            # Paste
            elif event.GetId() == 16:
                self.notebook.GetCurrentPage().textctrl.Paste()
            # Cut
            elif event.GetId() == 17:
                self.notebook.GetCurrentPage().textctrl.SelectAll()
                self.notebook.GetCurrentPage().textctrl.Cut()
        #-----------------------------------------------------------------------
        # audioの場合だけのメニュー
        elif self.notebook.GetCurrentPage().file_type=="audio":
            # 再生
            if event.GetId() == 20:
                self.notebook.GetCurrentPage().play(wx.media.EVT_MEDIA_PLAY)
            # 停止
            elif event.GetId() == 21:
                self.notebook.GetCurrentPage().stop(wx.media.EVT_MEDIA_STOP)
            # 一時停止
            elif event.GetId() == 22:
                self.notebook.GetCurrentPage().pause(wx.media.EVT_MEDIA_PAUSE)
            # ループ再生
            elif event.GetId() == 23:
                if self.menu_bar.FindMenuItem(22).IsChecked():
                    self.notebook.GetCurrentPage().loop_play = False
                else:
                    self.notebook.GetCurrentPage().loop_play = True
    #---------------------------------------------------------------------------
    def setmenubar(self):
        def show_help(event):
            self.sb.SetStatusText()
        
        import wx.lib.agw.flatmenu as FM
        
        menu_file = FM.FlatMenu()
        menu_file.Append(1, '名前を付けて保存')
        menu_file.Append(2, '上書き保存')
        menu_file.AppendSeparator()
        menu_file.Append(3, 'テキストファイルとして開く')
        menu_file.Append(4, '表ファイルとして開く')
        menu_file.Append(5, 'ファイルを開く')
        menu_file.Append(6, 'Webページ開く')
        menu_file.AppendSeparator()
        menu_file.Append(7, '新規作成')
        menu_file.AppendSeparator()
        menu_file.Append(8, '印刷')
        menu_file.AppendSeparator()
        menu_file.Append(9, '終了')
 
        menu_edit = FM.FlatMenu()
        menu_edit.Append(10, 'コピー',
                         """\
            テキストボックスに入力された文字を全てクリップボードにコピーします．
            Webページの場合はそのWebページのURLをクリップボードにコピーします．\
            """)
        menu_edit.AppendSeparator()
        menu_edit.Append(11, '検索', """\
            表示されつダイアログに検索したい文字を入力してください．
            テキストボックスに入力された全ての文字のうち，検索したい文字と最初に一致した文字を選択状態にします．\
            """)
        #menu_edit.Append(12, '次を検索')
        menu_edit.Append(13, '全置換', """\
            表示されつダイアログに置換したい文字と置換後の文字を順にを入力してください．
            テキストボックスに入力された全ての文字のうち，検索したい文字と一致した文字全てを置換後の文字に置き換えます．\
            """)
        menu_edit.AppendSeparator()
        menu_edit.Append(14, 'Undo', "元に戻す")
        menu_edit.Append(15, 'Redo', "やり直し")
        menu_edit.Append(16, 'Paste', "クリップボードにある文字列を貼り付けます．")
        menu_edit.Append(17, 'Cut')
        menu_edit.AppendSeparator()
        menu_edit.Append(18, 'タブを閉じる')
        menu_edit.Append(19, '全てのタブを閉じる')

        menu_media = FM.FlatMenu()
        menu_media.Append(20, '再生', "読み込んだオーディオファイルを再生します．")
        menu_media.Append(21, '停止', "読み込んだオーディオファイルを停止します")
        menu_media.Append(22, '一時停止', "読み込んだオーディオファイルを一時停止します")
        menu_media.AppendCheckItem(23,'ループ再生',
                                   "チェックを付けると，読み込んだオーディオファイルが停止した際に，自動的に再生されるようになります．")

        menu_special = FM.FlatMenu()
        menu_special.Append(24, '回＝回')
        menu_special.Append(25, 'パプリカ')
        menu_special.AppendSeparator()
        menu_special.Append(26, 'AC-bu1')
        menu_special.Append(27, 'AC-bu2')

        #menu_special.SetToolTip(wx.ToolTip('This Is Click Tooltip'))
        
        self.menu_bar = FM.FlatMenuBar(self,wx.ID_ANY,options=FM.FM_OPT_IS_LCD)
        self.menu_bar.Append(menu_file, 'ファイル')
        self.menu_bar.Append(menu_edit, '編集')
        self.menu_bar.Append(menu_media, '操作')
        self.menu_bar.Append(menu_special, 'おまけ')

        self.menu_bar.FindMenuItem(22).Check(False)

        #import wx.lib.agw.balloontip as BT
        #tipballoon = BT.BalloonTip(topicon=None, toptitle="textctrl",message="this is a textctrl",shape=BT.BT_ROUNDED,tipstyle=BT.BT_LEAVE)
        #tipballoon.SetTarget(menu_special)
        from wx.adv import RichToolTip
        tip = RichToolTip("t","t")
        tip.SetIcon(wx.ICON_INFORMATION)
        tip.ShowFor(menu_special)
        tip.SetTimeout(millisecondsTimeout=60, millisecondsDelay = 0)


        self.Bind(wx.EVT_MENU,self.selectMenu)
        self.Bind(FM.EVT_FLAT_MENU_ITEM_MOUSE_OVER,show_help)
        self.Bind(FM.EVT_FLAT_MENU_ITEM_MOUSE_OVER,self.status_update)
        #self.SetMenuBar(self.menu_bar)
    #---------------------------------------------------------------------------
    def __init__(self):
        super().__init__(None,wx.ID_ANY,'Python製メモ帳', size=(700, 500))

        self.notebook = Notebook(self,wx.ID_ANY)

        # text
        self.text_list = {}
        self.file_path_list = {}
        self.encoding_list = {}
        self.text_list_back_up = {}
        
        self.textctrl_make()

        # menu bar
        self.setmenubar()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.menu_bar, 0, wx.EXPAND)
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.SetAutoLayout(True)

        # status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.status_update(wx.EVT_TEXT)

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE,self.tab_close)

        self.Bind(wx.EVT_CLOSE,self.close_event)
        
        self.Bind(wx.EVT_TEXT,self.status_update)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED,self.status_update)

        # テキストにおける検索に使う
        self.search_word = ""
        self.search_word_pos = 0
#-------------------------------------------------------------------------------
if __name__ == '__main__':
  
    application = wx.App()
    frame = textpad()
    
    # ステータスバーを常時更新
    timer = wx.Timer(frame)
    frame.Bind(wx.EVT_TIMER, frame.status_update)
    timer.Start(100) # 0.1s

    
    frame.Show()
    frame.notebook.Refresh()
    application.MainLoop()
