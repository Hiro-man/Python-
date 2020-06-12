#-*- coding:utf-8 -*-
import wx
import wx.lib.agw.rulerctrl as rc

class TextCtrl(wx.Panel):
    """
    テキストを入力，もしくはファイルを読み取り，
    文字列を表示させるパネルを作成します．
    """
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
