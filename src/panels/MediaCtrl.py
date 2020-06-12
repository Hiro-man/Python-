#-*- coding:utf-8 -*-
import wx,wx.media

class MediaCtrl(wx.Panel):
    """
    .mp4/.aviという動画ファイルや.mp3/.wavという音楽ファイルを再生するための
    パネルでwxで作成したNotebook上に表示します．

    """
    
    def __init__(self,parent):
        """
        Parameter
        ----------
        parent：wx.Panelの親となるウィンドウ．
        　　　　textpad.pyが呼び出す際にNotebookが渡されます．
        
        """
        
        super().__init__(parent,wx.ID_ANY)

        # osの判定
        import platform
        pf = platform.system()

        # ファイルの再生のためにバックで使われるシステムの指定
        if pf == 'Windows':
            szBackend = wx.media.MEDIABACKEND_DIRECTSHOW
        elif pf == 'Darwin':
            szBackend = wx.media.MEDIABACKEND_QUICKTIME
        elif pt == 'Linux':
            szBackend = wx.media.MEDIABACKEND_GSTREAMER
            
        #上記以外にszBackendに指定できるもの
        #・MEDIABACKEND_MCI        
        #・MEDIABACKEND_REALPLAYER 
        #・MEDIABACKEND_WMP10
        
            
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
