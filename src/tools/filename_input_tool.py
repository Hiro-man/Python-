#-*- coding:utf-8 -*-
import wx

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

        return text,encoding
