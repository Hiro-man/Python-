#-*- coding:utf-8 -*-
import wx,sys,re,os,unicodedata,markdown
import wx.lib.agw.aui.auibook as aui
from wx.html import HtmlEasyPrinting
from wx.html import HtmlWindow
from wx.media import * 

#-------------------------------------------------------------------------------

class MyHtmlPrinter(HtmlEasyPrinting):

    def __init__(self, parent,name):
 
        # 印刷するドキュメントの名前
        name = name

        # Init the HtmlEasyPrinting.
        HtmlEasyPrinting.__init__(self, name, parent)
    
        # Get the current script directory.
        self.current_dir = os.path.normpath(os.path.dirname(__file__))
    
        # Set some default printer and page options.
        self.GetPrintData().SetPaperId(wx.PAPER_A4) # サイズ一覧：https://wxpython.org/Phoenix/docs/html/wx.PaperSize.enumeration.html
        self.GetPrintData().SetOrientation(wx.PORTRAIT)  # 紙の方向：wx.LANDSCAP＝横向き，wx.PORTRAIT＝縦向き
        # Black and white printing if False.
        self.GetPrintData().SetColour(True)
        # マージンの設定:(上，左)or(下，右)を1mm単位で指定したタプルを渡す
        self.GetPageSetupData().SetMarginTopLeft((12, 6))
        self.GetPageSetupData().SetMarginBottomRight((12, 6))
    


    def GetHtmlText(self, text):
        """
        文字列をHTML形式に変換
        """
        text = text.replace(' ','&nbsp;').replace('　','&nbsp;&nbsp;')

        # 拡張子の確認
        root, ext = os.path.splitext(self.GetName())
        if ext == "md":
            md = markdown.Markdown(extensions=['tables'])
            text = md.convert(text)
            html_text = text.replace("\n", "<br>")
        else:
            html_text = ""
            text_long = 0
            text_list = text.split('\n')
            text_cols = len(text_list)
            
            for now_cols,i in enumerate(text_list):
                text_count = len(i)
                for no,j in enumerate(i):
                    ret = unicodedata.east_asian_width(j)
                    if ret in ('F','W','A'): # 1行全角42文字
                        text_long += 4.1
                    else: # 1行半角85文字
                        text_long += 2.04
                        
                    if text_count == no+1:
                        text_long = 0
                    
                    if text_long > 174: # A4のときの一行の幅（mm）
                        html_text += "<br>"
                        text_long = 0
                    html_text += j
                if now_cols+1 == text_cols:
                    pass
                else:
                    html_text += "<br>"
                
            html_text = """
            <!doctype html>
            <html>
            <head>
              <meta http-equiv="Content-Type" content="text/html" charset="utf-8">
            </head>
            <body>
              <p><TT>{0}</TT></p>
            </body>
            </html>
            """.format(html_text)

        return html_text
    #---------------------------------------------------------------------------
    def page_setup(self):
        """
        Show page setup.
        """
        self.PageSetup()        
    def print_text(self, text):
        """
        Print the text.
        """
        return self.PrintText(self.GetHtmlText(text), basepath=self.current_dir)

    def preview_text(self, text):
        """
        Preview html text.
        """        
        self.SetHeader("@DATE@ @TIME@  @TITLE@")
        self.SetFooter("Page @PAGENUM@ of @PAGESCNT@")

        return self.PreviewText(self.GetHtmlText(text), basepath=self.current_dir)

    def print_file(self, file):
        """
        Print the text.
        """
    
        return self.PrintFile(file)

    def preview_file(self, file):
        """
        Preview html file.
        """

        return self.PreviewFile(file)
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
class TextCtrl(wx.TextCtrl):
    def __init__(self,parent,text="",path=None,encoding=None,name=""):
        wx.TextCtrl.__init__(self,parent,wx.ID_ANY,value=text,style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
        self.file_path = path
        self.file_encoding = encoding
        self.file_name = name
        self.SetFont(wx.Font(
            pointSize = 10,
            family    = wx.FONTFAMILY_TELETYPE, # https://wxpython.org/Phoenix/docs/html/wx.FontFamily.enumeration.html
            style     = wx.FONTSTYLE_NORMAL, # https://wxpython.org/Phoenix/docs/html/wx.FontStyle.enumeration.html
            weight    = wx.FONTWEIGHT_NORMAL # https://wxpython.org/Phoenix/docs/html/wx.FontWeight.enumeration.html
            ))
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
def input_word(title):
    wordbox = WordBox(title)
    if wordbox.process:
        if title == "置換":
            return wordbox.text1,wordbox.text2
        else:
            return wordbox.text
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
    def __init__(self):
        super().__init__(None,wx.ID_ANY,'ファイル名を入力してください', size=(250, 150))
        root_panel = wx.Panel(self, wx.ID_ANY)

        # text
        text_panel = wx.Panel(root_panel, wx.ID_ANY,pos=(0,0),size=(200,30))
        self.text = wx.TextCtrl(text_panel,wx.ID_ANY,size=(200,25))
        
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
def input_file_name():
    textbox = TextBox()
    if textbox.text == None:
        return None,None
    else:
        text = textbox.text
        encoding = textbox.encoding
        print(text,encoding)
        return text,encoding
#-------------------------------------------------------------------------------
class textpad(wx.Frame):
    #---------------------------------------------------------------------------    
    def printer(self):
        MyHtmlPrinter(self,self.notebook.GetCurrentPage().file_name).preview_text(self.notebook.GetCurrentPage().GetValue())    
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
        #print(self.notebook.GetSelection())
        #print(self.notebook.GetCurrentPage().GetValue())
        #print(wx.Cursor().IsOk())

        text = re.sub(r"\s","",self.notebook.GetCurrentPage().GetValue())

        pos  = self.notebook.GetCurrentPage().PositionToXY(
            self.notebook.GetCurrentPage().GetSelection()[0]
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
                    text=text,
                    path=path,
                    encoding=encoding,
                    name=name
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
            title
            )
    #---------------------------------------------------------------------------
    def save_file(self):
        with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
            f.write(self.notebook.GetCurrentPage().GetValue())
    #---------------------------------------------------------------------------
    def save_file_path(self):
        # ファイル名を入力
        title,encoding = input_file_name()
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
        if self.yes_or_no("本当に終了してもいいですか？","確認ダイアログ"):
            # 保存の確認
            if self.yes_or_no("終了前に保存しますか？","確認ダイアログ"):
                # タブ一つ一つに対して行う
                while self.notebook.GetPageCount()>0:
                    # 名前を付けて保存
                    if self.notebook.GetCurrentPage().file_path==None:      
                        if self.save_file_path():
                            self.save_file() 
                        else:
                            wx.MessageBox(message="保存をキャンセルしました",caption="キャンセル",style=wx.OK)
            
                    # 上書き保存
                    else:
                        self.save_file()
                    self.notebook.DeletePage(self.notebook.GetSelection())
            # 保存しない場合
            else:
                pass
                
            # 終了
            sys.exit()
        else:
            event.Destroy()
            return
    #---------------------------------------------------------------------------
    def tab_close(self,event):
        if self.yes_or_no("本当にタブを閉じていいですか？","確認ダイアログ"):
            if self.notebook.GetPageCount()==1:
                self.textctrl_make()
            else:
                pass
        else:
            """
            event.Destroy()を実行すると以下のようなエラーが出るが，
            スクリプト自体はその後も動き，イベントも破棄できるようではある
            
            Traceback (most recent call last):
            File "C:\Program Files\Python36\lib\site-packages\wx\lib\agw\aui\auibook.py", line 5577, in OnTabButton
                if not e.IsAllowed():
              File "C:\Program Files\Python36\lib\site-packages\wx\lib\agw\aui\auibook.py", line 542, in IsAllowed
                return self.notify.IsAllowed()
            RuntimeError: wrapped C/C++ object of type AuiNotebookEvent has been deleted
            """
            event.Destroy()
    #---------------------------------------------------------------------------
    def selectMenu(self,event):
        #-----------------------------------------------------------------------
        # 新規保存（ファイル出力）
        if event.GetId() == 1:
            if self.save_file_path():
                self.save_file() 
            else:
                wx.MessageBox(message="保存をキャンセルしました",caption="キャンセル",style=wx.OK)
        #-----------------------------------------------------------------------           
        # 上書き保存（ファイル出力）
        elif event.GetId() == 7:
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
        # 終了
        elif event.GetId() == 2:
            self.close_event(wx.EVT_CLOSE)
        #-----------------------------------------------------------------------            
        # ファイルを開く
        elif event.GetId() == 5:
            # ファイル選択ダイアログを作成
            dialog = wx.FileDialog(None, u'ファイル選択してください', style=wx.FD_OPEN )
            #dialog.SetWildcard("(* .tex）| * .tex")

            # ファイルが選択されたとき
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                dialog.Destroy()
            #elif dialog.ShowModal() == wx.ID_CANCEL:
            else:
                dialog.Destroy()
                return
            
            # ファイルの読み込み
            # LoadFileメソッドはテキストファイルだけなので，with構文でファイルを読み込む
            encoding = check_encoding(path)
            with open(path,mode="r",encoding=encoding) as f:
                data = f.read()
            # ファイルの内容を新しいタブで表示
            self.textctrl_make(
                text=data,
                path=path,
                encoding=encoding,
                name=path.split(os.path.sep)[-1],
                title=path.split(os.path.sep)[-1]
                )
            
            del data,path
        #-----------------------------------------------------------------------           
        # 新規作成
        elif event.GetId() == 6:
            self.textctrl_make()
        #-----------------------------------------------------------------------
        # 印刷
        elif event.GetId() == 11:
            self.printer()
        #-----------------------------------------------------------------------
        # コピー
        if event.GetId() == 3:
            wx.TheClipboard.SetData(wx.TextDataObject(self.notebook.GetCurrentPage().GetValue()))
            wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
        #-----------------------------------------------------------------------            
        # 置換
        elif event.GetId() == 8:
            w1,w2 = input_word("置換")
            self.notebook.GetCurrentPage().SetValue(self.notebook.GetCurrentPage().GetValue().replace(w1,w2))
        #-----------------------------------------------------------------------
        # タブを閉じる
        elif event.GetId() == 9:
            if self.yes_or_no("本当にタブを閉じていいですか？","確認ダイアログ"):
                if self.notebook.GetPageCount()==1:
                    self.textctrl_make()
                else:
                    pass
                self.notebook.DeletePage(self.notebook.GetSelection())
            else:
                return
        #-----------------------------------------------------------------------
        # 全てのタブを閉じる
        elif event.GetId() == 10:
            # 確認
            if self.yes_or_no("本当に全てのタブを閉じていいですか？","確認ダイアログ"):
                # AttributeError: 'AuiNotebook' object has no attribute 'DeleteAllPages'
                #self.notebook.DeleteAllPages()

                while self.notebook.GetPageCount()>0:
                    self.notebook.DeletePage(self.notebook.GetSelection())
                self.textctrl_make()
            else:
                return
    #---------------------------------------------------------------------------
    def setmenubar(self):
        menu_file = wx.Menu()
        menu_file.Append(1, '名前を付けて保存')
        menu_file.Append(7, '上書き保存')
        menu_file.AppendSeparator()
        menu_file.Append(5, 'ファイルを開く')
        menu_file.AppendSeparator()
        menu_file.Append(6, '新規作成')
        menu_file.AppendSeparator()
        menu_file.Append(11, '印刷')
        menu_file.AppendSeparator()
        menu_file.Append(2, '終了')
 
        menu_edit = wx.Menu()
        menu_edit.Append(3, 'コピー')
        menu_edit.AppendSeparator()
        menu_edit.Append(8, '置換')
        menu_edit.AppendSeparator()
        menu_edit.Append(9, 'タブを閉じる')
        menu_edit.Append(10, '全てのタブを閉じる')
 
        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'ファイル')
        menu_bar.Append(menu_edit, '編集')

        self.Bind(wx.EVT_MENU,self.selectMenu)
        self.SetMenuBar(menu_bar)
    #---------------------------------------------------------------------------
    def __init__(self):
        super().__init__(None,wx.ID_ANY,'Python製メモ帳', size=(500, 400))

        self.notebook = aui.AuiNotebook(self,wx.ID_ANY)

        # text
        self.text_list = {}
        self.file_path_list = {}
        self.encoding_list = {}
        self.text_list_back_up = {}
        
        self.textctrl_make()

        # menu bar
        self.setmenubar()

        # status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.status_update(wx.EVT_TEXT)

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE,self.tab_close)

        self.Bind(wx.EVT_CLOSE,self.close_event)
        
        self.Bind(wx.EVT_TEXT,self.status_update)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED,self.status_update)
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
