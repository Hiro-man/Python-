#-*- coding:utf-8 -*-
import wx

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
#-------------------------------------------------------------------------------
class PDF(wx.Panel):
    """
    PDFを表示し操作するパネルを作成します．
    """
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
