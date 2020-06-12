#-*- coding:utf-8 -*-
import wx

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
