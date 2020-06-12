#-*- coding:utf-8 -*-
import wx,os
import wx.lib.agw.aui.auibook as aui

class Notebook(aui.AuiNotebook):
    """
    wx.lib.agw.aui.auibook.AuiNotebookにいくつか変数を追加したクラスです．
    各メソッドの変数や機能についてはwx.lib.agw.aui.auibook.AuiNotebookを参照してください

    >>> import wx.lib.agw.aui.auibook as aui
    >>> help(aui.AuiNotebook)

    AuiNotebookはwx/lib/agw/aui/auibook.pyの2970行目以降に書かれています．
    ※バージョンによっては前後するかもしれません．
    """
    def __init__(self,parent,style):
        super().__init__(parent,style)
        self.Pagelist = {} # 作成されたpageのdict

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

        #-----------------------------------------------------------------------
        # 追加部分
        info.window.file_type = file_type
        info.window.file_path = path
        info.window.file_encoding = encoding
        info.window.file_name = name

        self.Pagelist[page_idx] = file_type
        
        # 拡張子の確認
        root, info.window.ext = os.path.splitext(name)
        if info.window.ext=='':
            info.window.ext = '.txt'
        #-----------------------------------------------------------------------
        
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

    def DeletePage(self, page_idx):

        #-----------------------------------------------------------------------
        # 追加部分
        self.Pagelist.pop(page_idx, "Not Found")
        #-----------------------------------------------------------------------

        if page_idx >= self._tabs.GetPageCount():
            return False

        wnd = self._tabs.GetWindowFromIdx(page_idx)
        # hide the window in advance, as this will
        # prevent flicker
        wnd.Show(False)

        self.RemoveControlFromPage(page_idx)

        if not self.RemovePage(page_idx):
            return False

        wnd.Destroy()

        return True
