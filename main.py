#-*- coding:utf-8 -*-
import wx
#-------------------------------------------------------------------------------
# srcフォルダ下のスクリプトのクラスやメソッドを呼び出す
from src.textpad import *
#------------------------------------------------------------------------------- 

if __name__ == '__main__':
    # GUIの作成
    application = wx.App()
    frame = textpad()
    
    # ステータスバーを常時更新
    timer = wx.Timer(frame)
    frame.Bind(wx.EVT_TIMER, frame.status_update)
    timer.Start(100) # 0.1s

    # 可視化
    frame.Show()
    frame.notebook.Refresh()
    application.MainLoop()
