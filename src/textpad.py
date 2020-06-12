#-*- coding:utf-8 -*-
import wx,sys,re,os,wx.media,wx.html2,pickle,pprint,ast,codecs
# 自作モジュールの呼び出し
if __name__ == '__main__':
    #-------------------------------------------------------------------------------
    # 同じディレクトリ下のスクリプトのクラスやメソッドを呼び出す
    from Notebook import *
    #-------------------------------------------------------------------------------
    # panelsフォルダ下のスクリプトのクラスやメソッドを呼び出す
    from panels.MediaCtrl import *
    from panels.PDFCtrl   import PDF
    from panels.TableCtrl import Table
    from panels.TextCtrl  import *
    #-------------------------------------------------------------------------------
    # toolsフォルダ下のスクリプトのクラスやメソッドを呼び出す
    from tools.tools import *
    from tools.filename_input_tool import input_file_name
    from tools.find_and_replace_for_text import input_word
    #-------------------------------------------------------------------------------
else:
    #-------------------------------------------------------------------------------
    # 同じディレクトリ下のスクリプトのクラスやメソッドを呼び出す
    from .Notebook import *
    #-------------------------------------------------------------------------------
    # panelsフォルダ下のスクリプトのクラスやメソッドを呼び出す
    from .panels.MediaCtrl import *
    from .panels.PDFCtrl   import PDF
    from .panels.TableCtrl import Table
    from .panels.TextCtrl  import *
    #-------------------------------------------------------------------------------
    # toolsフォルダ下のスクリプトのクラスやメソッドを呼び出す
    from .tools.tools import *
    from .tools.filename_input_tool import input_file_name
    from .tools.find_and_replace_for_text import input_word
    #-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def load_css(css_path):
    """
    印刷時にcssを使用するために，
    別ディレクトリ下のcssをhtmlファイルが読み込むのではなく，
    htmlファイルにcssのスクリプトを直接書くことで，
    exe化する際にワンファイルで出力できるようにする．
    """
    encoding = check_encoding(css_path)
    try:
        with open(css_path,mode="r",encoding=encoding) as f:
            css_data = f.read()
    except UnicodeDecodeError:
        encoding="utf-8"
        with codecs.open(css_path,mode="r",encoding="utf-8",errors="backslashreplace") as f:
            css_data = f.read()
    return '<script crossorigin="anonymous" media="all" rel="stylesheet">{}</script>'.format(css_data)

#-------------------------------------------------------------------------------
class textpad(wx.Frame):
    #---------------------------------------------------------------------------    
    def convert_to_html(self):
        style = ""

        # githubのcssを使用
        #style += '<link crossorigin="anonymous" media="all" integrity="sha512-xnQIMZDOHZTyEPkXHdiwqBPPUAyzDzAU5iDJa6OfzDqwhJdI+0IyBajpzgDAKoegEWUXs4Ze9+/jGhP/OMD98w==" rel="stylesheet" href="./css/github/frameworks-c674083190ce1d94f210f9171dd8b0a8.css" />'
        #style += "\n"
        #style += '<link crossorigin="anonymous" media="all" integrity="sha512-BW+uq8GWEGtIyPfgCQaURqVHC2lyEh4xoU0+XMJkdPyYoSLpzVibSaWwt+Ve/4l8Lmk+SS+RA1Jr8j58P/84Xw==" rel="stylesheet" href="./css/github/github-056faeabc196106b48c8f7e009069446.css" />'

        # githubのcssを使用：htmlファイルにスクリプトを埋め込んでしまう方法
        #style += load_css(os.path.join(os.path.dirname(os.path.abspath(__file__)),"css","github","frameworks-c674083190ce1d94f210f9171dd8b0a8.css"))
        #style += "\n"
        style += load_css(os.path.join(os.path.dirname(os.path.abspath(__file__)),"css","github","github-056faeabc196106b48c8f7e009069446.css"))

        html_header = '''\
            <head>
                <meta http-equiv="Content-Type" content="text/html" charset="utf-8">
                <title>{0}</title>
                {1}
            </head>\
            '''.format(self.notebook.GetCurrentPage().file_name,style)

        if self.notebook.GetCurrentPage().file_type == "txt":
            html_text = self.notebook.GetCurrentPage().textctrl.GetValue()
            
            if self.notebook.GetCurrentPage().ext == ".txt":
                html_text = html_text.replace("\n", "<br>")
                html_text = html_text.replace(" ","&nbsp;")
                html_text = html_text.replace("　","&nbsp;&nbsp;")
                html_text = html_text.replace("'","&#39;")

                html_text = "<p>{}</p>".format(html_text)
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
                        from markdown.extensions.extra import ExtraExtension
                        #from markdown.extensions.tables import TableExtension
                        from markdown.extensions.codehilite import CodeHiliteExtension
                        html_text = markdown.markdown(html_text,extensions=[
                            ExtraExtension(),
                            CodeHiliteExtension()
                            ])

                        html_text = html_text.replace("<p><code>",'<div class="highlight highlight-source-shell"><pre><code>')
                        html_text = html_text.replace("</code></p>",'</code></pre></div>')
                        #print(html_text)
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

            # headerの作成
            html_text += "<tr>"
            # indexがあればその分空けておく
            if self.notebook.GetCurrentPage().index:
                html_text += '<th></th>'
            for label in self.notebook.GetCurrentPage().grid.GetTable().colLabels:
                html_text += '<th>{}</th>'.format(label)
            html_text += "</tr>"

            for no,rows in enumerate(self.notebook.GetCurrentPage().grid.GetTable().data):
                html_text += "<tr>"
                # indexがあれば挿入
                if self.notebook.GetCurrentPage().index:
                    html_text += '<th>{}</th>'.format(self.notebook.GetCurrentPage().grid.GetTable().rowLabels[no])
                # 表の中身を書いていく
                for row in rows:
                    html_text += "<td>{}</td>".format(row)
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
        """
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path,"printout.html")
        with open(path,mode="w",encoding="utf-8") as f:
            f.write(self.convert_to_html())
        """
                
        #printer = MyBrowser("file:///" + "/".join(path.split(os.path.sep)))
        # HTMLに変換したものをブラウザ表示する
        printer = wx.Dialog(None,wx.ID_ANY,"HTML変換画面", size=(700, 700))
        printer.browser = wx.html2.WebView.New(printer)
        #printer.browser.LoadURL("file:///" + "/".join(path.split(os.path.sep)))
        printer.browser.SetPage(self.convert_to_html(),"")
        printer.ShowModal()
        # 印刷プレビューの表示＆印刷
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
        if self.notebook.GetCurrentPage().file_type=="table":
            self.menu_bar.FindMenuItem(25).Enable(enable=True)
            self.menu_bar.FindMenuItem(26).Enable(enable=True)
            self.menu_bar.FindMenuItem(27).Enable(enable=True)
            self.menu_bar.FindMenuItem(28).Enable(enable=True)
            self.menu_bar.FindMenuItem(29).Enable(enable=True)
            self.menu_bar.FindMenuItem(30).Enable(enable=True)
            self.menu_bar.FindMenuItem(31).Enable(enable=True)
            self.menu_bar.FindMenuItem(32).Enable(enable=True)
        else:
            self.menu_bar.FindMenuItem(25).Enable(enable=False)
            self.menu_bar.FindMenuItem(26).Enable(enable=False)
            self.menu_bar.FindMenuItem(27).Enable(enable=False)
            self.menu_bar.FindMenuItem(28).Enable(enable=False)
            self.menu_bar.FindMenuItem(29).Enable(enable=False)
            self.menu_bar.FindMenuItem(30).Enable(enable=False)
            self.menu_bar.FindMenuItem(31).Enable(enable=False)
            self.menu_bar.FindMenuItem(32).Enable(enable=False)        

        
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
            
            self.sb.SetStatusText('{0}行目{1}列目のセルを選択中'.format(
                self.notebook.GetCurrentPage().grid.GetGridCursorRow(),
                self.notebook.GetCurrentPage().grid.GetGridCursorCol()
                ),1)

            
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
            
            # 元のデータとは形式が変わってしまう可能性がある
            if self.notebook.GetCurrentPage().ext in (".pickle",".txt"):
                # indexある場合
                if self.notebook.GetCurrentPage().index:
                    data = {}
                # indexない場合
                else:
                    data = []
                
                # 行ごとに読み込んでいく
                for no,rows in enumerate(self.notebook.GetCurrentPage().grid.GetTable().data):
                    # indexある場合
                    if self.notebook.GetCurrentPage().index:
                        if self.notebook.GetCurrentPage().header:
                            element = {self.notebook.GetCurrentPage().grid.GetTable().colLabels[no]:row for no,row in enumerate(rows)}
                        else:
                            element = rows
                        data[self.notebook.GetCurrentPage().grid.GetTable().rowLabels[no]] = element
                    # indexない場合
                    else:
                        if self.notebook.GetCurrentPage().header:
                            element = {self.notebook.GetCurrentPage().grid.GetTable().colLabels[no]:row for no,row in enumerate(rows)}
                        else:
                            element = rows
                        data.append(element)

                if self.notebook.GetCurrentPage().ext == ".pickle":
                    # pickle化
                    with open(self.notebook.GetCurrentPage().file_path,mode="wb") as f:
                        pickle.dump(data,f)
                elif self.notebook.GetCurrentPage().ext == ".txt":
                    with open(self.notebook.GetCurrentPage().file_path,mode="w",encoding=self.notebook.GetCurrentPage().file_encoding) as f:
                        pprint.pprint(data,stream=f)
            else:
                text = ""
                # headerの読み込み
                if self.notebook.GetCurrentPage().header:
                    if self.notebook.GetCurrentPage().ext == ".csv":
                        text += ",".join(self.notebook.GetCurrentPage().grid.GetTable().colLabels)
                    elif self.notebook.GetCurrentPage().ext == ".tsv":
                        text += "   ".join(self.notebook.GetCurrentPage().grid.GetTable().colLabels)
                    text += "\n"
                else:
                    pass
                # 行ごとに読み込んでいく
                for no,rows in enumerate(self.notebook.GetCurrentPage().grid.GetTable().data):
                    # indexある場合
                    if self.notebook.GetCurrentPage().index:
                        if self.notebook.GetCurrentPage().ext == ".csv":
                            text += "{},".format(self.notebook.GetCurrentPage().grid.GetTable().rowLabels[no])
                        elif self.notebook.GetCurrentPage().ext == ".tsv":
                            text += "{}   ".format(self.notebook.GetCurrentPage().grid.GetTable().rowLabels[no])
                    else:
                        pass

                    # 要素の追加
                    if self.notebook.GetCurrentPage().ext == ".csv":
                        text += ",".join(rows)
                    elif self.notebook.GetCurrentPage().ext == ".tsv":
                        text += "   ".join(rows) 
                    
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
            # 拡張子なし
            if ext=='':
                # 表ファイルの場合，デフォルトとしてcsvファイルとして保存
                if self.notebook.GetCurrentPage().file_type == "table":
                    self.notebook.GetCurrentPage().ext = ".csv"
                    self.notebook.GetCurrentPage().file_path = os.path.join(folda.GetPath(),title+'.csv')
                # テキストファイルとして保存
                else:
                    self.notebook.GetCurrentPage().file_path = os.path.join(folda.GetPath(),title+'.txt')
                
            # 拡張子アリ
            else:
                if self.notebook.GetCurrentPage().file_type == "table":
                    self.notebook.GetCurrentPage().ext = ext
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
            """
            読み込んだデータは整形するとともに2次元リストに変換して扱う．
            """
            #-------------------------------------------------------------------
            def shape(pre_data):
                data = []
                for no,d in enumerate(pre_data):
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
                            
                return data
            #-------------------------------------------------------------------
            def shape2list(text):
                """
                pprintでtxtファイルとして保存していたファイルとpickleファイルから
                読み込んだ表形式データを2次元リストに整形する
                """
                
                # 要素数が一定になるように整形する
                data   = []
                header = None
                index  = None

                # まずは2次元リストに変換
                # 辞書型以外のリスト系データ
                if type(text) in (list,tuple,set):
                    for i in text:
                        items = []
                        if type(i) in (list,tuple,set):
                            for j in i:
                                # リスト系では処理できない？ので文字型に変換
                                if type(j) in (list,tuple,set,dict):
                                    items.append(str(j))
                                # それ以外
                                else:
                                    items.append(j)
                        elif type(i) == dict:
                            header = list(i.keys())
                            for j in i.values():
                                # リスト系では処理できない？ので文字型に変換
                                if type(j) in (list,tuple,set,dict):
                                    items.append(str(j))
                                # それ以外
                                else:
                                    items.append(j)     
                        data.append(items)
                # 辞書型の場合
                elif type(text) == dict:
                    for idx,i in text.items():
                        index.append(idx)
                        if type(i) in (list,tuple,set):
                            for j in i:
                                # リスト系では処理できない？ので文字型に変換
                                if type(j) in (list,tuple,set,dict):
                                    items.append(str(j))
                                # それ以外
                                else:
                                    items.append(j)
                        elif type(i) == dict:
                            header = list(i.keys())
                            for j in i.values():
                                # リスト系では処理できない？ので文字型に変換
                                if type(j) in (list,tuple,set,dict):
                                    items.append(str(j))
                                # それ以外
                                else:
                                    items.append(j)     
                        data.append(items)
                else:
                    return False # とりあえず．．．

                # 整形
                data = shape(data)

                return data,header,index
                #---------------------------------------------------------------
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
                data,header,index = shape2list(text)

                progress.Destroy() 
            #-------------------------------------------------------------------
            # pickleファイルの場合
            elif ext == ".pickle":
                encoding = None

                # ファイルの読み込み
                with open(path,mode="rb") as f:
                    text = pickle.load(f)
                    
                # 要素数が一定になるように整形する
                data,header,index = shape2list(text)
            #-------------------------------------------------------------------
            # csvファイル・tsvファイルの場合
            elif ext in (".csv",".tsv"):
                # ヘッダーの確認
                dialog = wx.MessageDialog(None, "ヘッダーはありますか？", caption="確認",style=wx.YES_NO)
                res = dialog.ShowModal()
                if res == wx.ID_YES:
                    header = True
                elif res == wx.ID_NO:
                    header = None
                dialog.Destroy()
                
                # indexの確認
                dialog = wx.MessageDialog(None, "インデックスはありますか？", caption="確認",style=wx.YES_NO)
                res = dialog.ShowModal()
                if res == wx.ID_YES:
                    index = []
                elif res == wx.ID_NO:
                    index = None
                dialog.Destroy()
                
                encoding = check_encoding(path)
                data = []
                
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
                            # dataに追加
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
                            # dataに追加
                            data.append(d)                            
                            read_size += len(line.encode(encoding))
                            progress.Update(read_size)

                data = shape(data)
                
                if header != None:
                    header = data[0]
                    data   = data[1:]

                if index  != None:
                    header = header[1:]
                    index  = [str(i[0]) for i in data]
                    data   = [i[1:] for i in data]
                
            else:
                return False

            # headerがある場合，要素が文字列でないとエラーになるので，念のために
            if header != None:
                header = [str(i) for i in header]

            page = Table(
                self.notebook,
                path,
                data,
                header,
                index
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
                # https://wxpython.org/Phoenix/docs/html/wx.html2.WebViewIE_EmulationLevel.enumeration.html
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
        # テキスト入力用のパネルを作成
        elif event.GetId() == 7:
            self.textctrl_make()
        # 表形式のパネルを作成
        elif event.GetId() == 8:
            page = Table(
                self.notebook,
                None,
                # 空の2次元リストをデータとして渡す
                [["","","","",""],["","","","",""],["","","","",""],["","","","",""],["","","","",""]],
                None,
                None
                )
            self.notebook.AddPage(
                    page,
                    '新規表ファイル',
                    file_type="table",
                    path=None,
                    encoding = None,
                    name='新規表ファイル'
                    )            
        #-----------------------------------------------------------------------
        # 印刷
        elif event.GetId() == 9:
            if self.notebook.GetCurrentPage().file_type in ("txt","table"):
                self.printer()
            elif self.notebook.GetCurrentPage().file_type in ("pdf","url"):
                self.notebook.GetCurrentPage().Print()
        #-----------------------------------------------------------------------
        # 終了
        elif event.GetId() == 10:
            self.close_event(wx.EVT_CLOSE)
        #-----------------------------------------------------------------------
        # コピー
        if event.GetId() == 11:
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
        elif event.GetId() == 19:
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
        elif event.GetId() == 20:
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
        # audioの場合だけのメニュー
        elif event.GetId() in (21,22,23,24):
            for page_idx in self.notebook.Pagelist.keys():
                if self.notebook.Pagelist[page_idx] == "audio":
                    # 再生
                    if event.GetId() == 21:
                        self.notebook.GetPage(page_idx).play(wx.media.EVT_MEDIA_PLAY)
                    # 停止
                    elif event.GetId() == 22:
                        self.notebook.GetPage(page_idx).stop(wx.media.EVT_MEDIA_STOP)
                    # 一時停止
                    elif event.GetId() == 23:
                        self.notebook.GetPage(page_idx).pause(wx.media.EVT_MEDIA_PAUSE)
                    # ループ再生
                    elif event.GetId() == 24:
                        if self.menu_bar.FindMenuItem(22).IsChecked():
                            self.notebook.GetPage(page_idx).loop_play = False
                        else:
                            self.notebook.GetPage(page_idx).loop_play = True
                else:
                    continue
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # おまけ
        #-----------------------------------------------------------------------
        # 回＝回
        elif event.GetId() == 41:
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
        elif event.GetId() == 42:
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
        elif event.GetId() == 43:
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
        elif event.GetId() == 44:
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
            if event.GetId() == 15:
                self.notebook.GetCurrentPage().Undo()
            # Redo
            elif event.GetId() == 16:
                self.notebook.GetCurrentPage().Redo()
            # Paste
            elif event.GetId() == 17:
                self.notebook.GetCurrentPage().Paste()
            # Cut
            elif event.GetId() == 18:
                self.notebook.GetCurrentPage().SelectAll()
                self.notebook.GetCurrentPage().Cut()
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # txtの場合だけのメニュー
        elif self.notebook.GetCurrentPage().file_type=="txt":
            #-------------------------------------------------------------            
            # 検索
            if event.GetId() == 12:
                self.search_word = input_word("検索")
                if self.search_word:
                    self.search_word_pos = self.notebook.GetCurrentPage().textctrl.GetValue().find(self.search_word)
                    # 文字を選択状態にする
                    self.notebook.GetCurrentPage().textctrl.SetSelection(
                        from_=self.search_word_pos,
                        to_=self.search_word_pos+len(self.search_word)
                        )
            # 次を検索
            elif event.GetId() == 13:
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
            elif event.GetId() == 14:
                """
                self.notebook.GetCurrentPage().textctrl.Replace(from_, to_,str)
                という置換方法もあるが，置換位置が必要であり，本作では実装しない．
                """ 
                w1,w2 = input_word("全置換")
                if w1:
                    self.notebook.GetCurrentPage().textctrl.SetValue(self.notebook.GetCurrentPage().textctrl.GetValue().replace(w1,w2))
            #--------------------------------------------------------------            
            # Undo
            elif event.GetId() == 15:
                self.notebook.GetCurrentPage().textctrl.Undo()
            # Redo
            elif event.GetId() == 16:
                self.notebook.GetCurrentPage().textctrl.Redo()
            # Paste
            elif event.GetId() == 17:
                self.notebook.GetCurrentPage().textctrl.Paste()
            # Cut
            elif event.GetId() == 18:
                self.notebook.GetCurrentPage().textctrl.SelectAll()
                self.notebook.GetCurrentPage().textctrl.Cut()
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        # tableの場合だけのメニュー
        elif self.notebook.GetCurrentPage().file_type=="table":
            # Undo
            #if event.GetId() == 15:
            #   pass

            # 最後尾に1列追加する
            if event.GetId() == 25:
                self.notebook.GetCurrentPage().grid.AppendCols()
            # 最後尾に1行追加する
            elif event.GetId() == 26:
                self.notebook.GetCurrentPage().grid.AppendRows()
            # 現在選択中の1列を削除する
            elif event.GetId() == 27:
                self.notebook.GetCurrentPage().grid.DeleteCols(pos=self.notebook.GetCurrentPage().grid.GetGridCursorCol())
            # 現在選択中の1行を削除する
            elif event.GetId() == 28:
                self.notebook.GetCurrentPage().grid.DeleteRows(pos=self.notebook.GetCurrentPage().grid.GetGridCursorRow())
            # 最後尾の1列を削除する
            elif event.GetId() == 29:
                self.notebook.GetCurrentPage().grid.PopCols()
            # 最後尾の1行を削除する
            elif event.GetId() == 30:
                self.notebook.GetCurrentPage().grid.PopRows()

            # 現在選択中の列のラベル名を変更する
            elif event.GetId() == 31:
                word = input_word("列ラベル名編集")
                if word:
                    self.notebook.GetCurrentPage().grid.SetColLabelValue(self.notebook.GetCurrentPage().grid.GetGridCursorCol(),word)
                else:
                    return
            # 現在選択中の行のラベル名を変更する
            elif event.GetId() == 32:
                word = input_word("行ラベル名編集")
                if word:
                    self.notebook.GetCurrentPage().grid.SetRowLabelValue(self.notebook.GetCurrentPage().grid.GetGridCursorRow(),word)
                else:
                    return
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
        menu_file_new = FM.FlatMenu()
        menu_file_new.Append(7,'テキスト')
        menu_file_new.Append(8,'表')
        menu_file.AppendSubMenu(menu_file_new, '新規作成')
        menu_file.AppendSeparator()
        menu_file.Append(9, '印刷')
        menu_file.AppendSeparator()
        menu_file.Append(10, '終了')

        menu_edit = FM.FlatMenu()
        menu_edit.Append(11, 'コピー',
                         """\
            テキストボックスに入力された文字を全てクリップボードにコピーします．
            Webページの場合はそのWebページのURLをクリップボードにコピーします．\
            """)
        menu_edit.AppendSeparator()
        menu_edit.Append(12, '検索', """\
            表示されつダイアログに検索したい文字を入力してください．
            テキストボックスに入力された全ての文字のうち，検索したい文字と最初に一致した文字を選択状態にします．\
            """)
        #menu_edit.Append(13, '次を検索')
        menu_edit.Append(14, '全置換', """\
            表示されつダイアログに置換したい文字と置換後の文字を順にを入力してください．
            テキストボックスに入力された全ての文字のうち，検索したい文字と一致した文字全てを置換後の文字に置き換えます．\
            """)
        menu_edit.AppendSeparator()
        menu_edit.Append(15, 'Undo', "元に戻す")
        menu_edit.Append(16, 'Redo', "やり直し")
        menu_edit.Append(17, 'Paste', "クリップボードにある文字列を貼り付けます．")
        menu_edit.Append(18, 'Cut')
        menu_edit.AppendSeparator()
        menu_edit.Append(19, 'タブを閉じる')
        menu_edit.Append(20, '全てのタブを閉じる')

        menu_media = FM.FlatMenu()
        menu_media.Append(21, '全再生', "読み込んだオーディオファイルを再生します．")
        menu_media.Append(22, '全停止', "読み込んだオーディオファイルを停止します")
        menu_media.Append(23, '全一時停止', "読み込んだオーディオファイルを一時停止します")
        menu_media.AppendCheckItem(24,'ループ再生',
                                   "チェックを付けると，読み込んだオーディオファイルが停止した際に，自動的に再生されるようになります．")
        menu_media.AppendSeparator()
        menu_media.Append(25,'最後尾に1列追加する')
        menu_media.Append(26,'最後尾に1行追加する')
        menu_media.Append(27,'現在選択中の1列を削除する')
        menu_media.Append(28,'現在選択中の1行を削除する')
        menu_media.Append(29,'最後尾の1列を削除する')
        menu_media.Append(30,'最後尾の1行を削除する')
        menu_media.Append(31,'現在選択中の列のラベル名を変更する')
        menu_media.Append(32,'現在選択中の行のラベル名を変更する')

        menu_special = FM.FlatMenu()
        menu_special.Append(41, '回＝回')
        menu_special.Append(42, 'パプリカ')
        menu_special.AppendSeparator()
        menu_special.Append(43, 'AC-bu1')
        menu_special.Append(44, 'AC-bu2')

        #menu_special.SetToolTip(wx.ToolTip('This Is Click Tooltip'))
        
        self.menu_bar = FM.FlatMenuBar(self,wx.ID_ANY,options=FM.FM_OPT_IS_LCD)
        self.menu_bar.Append(menu_file, 'ファイル')
        self.menu_bar.Append(menu_edit, '編集')
        self.menu_bar.Append(menu_media, '操作')
        self.menu_bar.Append(menu_special, 'おまけ')

        self.menu_bar.FindMenuItem(24).Check(False)

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
